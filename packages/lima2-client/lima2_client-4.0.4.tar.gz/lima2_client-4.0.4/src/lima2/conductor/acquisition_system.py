# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 acquisition system encapsulation.

Abstraction over the Lima2 system as a whole (control + receivers). Exposes
the state and commands.
"""

import asyncio
import copy
import functools
import logging
import textwrap
import time
import traceback
import weakref
from typing import Any, Callable, Literal, cast
from uuid import UUID, uuid1

import orjson
from jsonschema_rs import ValidationError

from lima2.common.exceptions import (
    Lima2BackendError,
    Lima2BadCommand,
    Lima2Conflict,
    Lima2DeviceError,
    Lima2NotFound,
    Lima2ParamError,
)
from lima2.common.progress_counter import ProgressCounter, SingleCounter
from lima2.common.state import DeviceState, RunState, State
from lima2.conductor import processing
from lima2.conductor.processing import failing, legacy, smx, xpcs
from lima2.conductor.processing.pipeline import Pipeline, PipelineErrorEvent
from lima2.conductor.tango.control import TangoControl
from lima2.conductor.tango.receiver import TangoReceiver
from lima2.conductor.tango.utils import TangoDevice, format_exception, unpack_exception
from lima2.conductor.topology import DynamicDispatch, Topology
from lima2.conductor.utils import (
    DecoratedFunc,
    get_subschema,
    list_to_jsonpath,
    naturaltime,
    validate,
)

logger = logging.getLogger(__name__)


class DisconnectedError(RuntimeError):
    """Returned by ping_all() when some devices are offline."""


class AcquisitionSystem:
    def __init__(
        self,
        control: TangoControl,
        receivers: list[TangoReceiver],
        topology: Topology,
        tango_timeout_s: float,
    ):
        self.control = control
        self.receivers = receivers
        self.topology = topology
        """Static topology (frame dispatch). Passed to Pipeline constructor on prepare()."""

        self.tango_timeout_s = tango_timeout_s

        self.user_lock = asyncio.Lock()
        """Prevents user commands from being executed concurrently."""

        self.current_pipeline: Pipeline | None = None
        self.cached_pipelines: dict[UUID, Pipeline] = {}

        self.runstate = RunState.IDLE
        """Represents the completion state of the current run."""

        self.finished_receivers: set[TangoReceiver] = set()
        """Tracks which receivers have finished acquisition."""

        self.register_event_callbacks()

    ###########################################################################
    # Connection
    ###########################################################################

    async def ping_all(self) -> list[int]:
        """Ping all devices, raise a DisconnectedError if any are offline."""

        async def ping_dev(device: TangoDevice) -> int:
            ping_us = await device.ping()
            logger.debug(f"Ping {device.name}: {ping_us}µs")
            return ping_us

        devices = [self.control, *self.receivers]
        pings_us = await asyncio.gather(
            *[ping_dev(device) for device in devices],
            return_exceptions=True,  # Collect exceptions
        )

        errors = [result for result in pings_us if isinstance(result, Lima2DeviceError)]
        if len(errors) > 0:
            raise DisconnectedError(
                "The following devices are offline:\n- "
                + "\n- ".join([err.device_name for err in errors])
            )

        return cast(list[int], pings_us)

    ###########################################################################
    # State
    ###########################################################################

    async def device_states(self) -> list[DeviceState]:
        """Return the device states as a serializable dictionary."""
        states: list[DeviceState] = []

        devices = [self.control, *self.receivers]
        dev_states = await asyncio.gather(
            *[device.acq_state() for device in devices], return_exceptions=True
        )

        for state in dev_states:
            if isinstance(state, Exception):
                states.append(DeviceState.OFFLINE)
            elif isinstance(state, DeviceState):
                states.append(state)
            else:
                raise NotImplementedError(f"Unexpected device state type: {state}")

        return states

    async def state(self) -> State:
        """Compute the unified system state from the individual device states."""
        try:
            await self.ping_all()
        except DisconnectedError:
            return State.DISCONNECTED

        devices = [self.control, *self.receivers]
        dev_states = await self.device_states()

        for dev, state in zip(devices, dev_states, strict=True):
            logger.info(f"{dev.name}: {state.name}")

        return State.from_device_states(states=dev_states)

    ###########################################################################
    # User commands
    ###########################################################################

    @staticmethod
    def user_command(
        allowed_states: list[State],
    ) -> Callable[[DecoratedFunc], DecoratedFunc]:
        """A decorator to wrap a method with the user_lock, to prevent concurrent commands.

        Raises a Lima2Conflict exception straight away if another
        @user_command-decorated method is ongoing.

        Raises a Lima2BadCommand if the current state forbids the requested
        command.

        Args:
            allowed_states: list of allowed initial states for the command.
        """

        def decorator(method: DecoratedFunc) -> DecoratedFunc:
            async def wrapper(self, *args, **kwargs):  # type: ignore
                if self.user_lock.locked():
                    raise Lima2Conflict("Another command is in progress.")

                async with self.user_lock:
                    state = await self.state()
                    logger.debug(f"Current state in call to {method.__name__}: {state}")
                    if state in allowed_states:
                        return await method(self, *args, **kwargs)
                    else:
                        raise Lima2BadCommand(
                            f"Cannot {method.__name__} in current state ({state.name})"
                        )

            return cast(DecoratedFunc, wrapper)

        return decorator

    @user_command(allowed_states=[State.IDLE, State.PREPARED, State.UNKNOWN])
    async def prepare(
        self,
        ctl_params: dict[str, Any],
        acq_params: dict[str, Any],
        proc_params: dict[str, Any],
    ) -> UUID:
        """Prepare for an acquisition.

        Validate parameters, send them to each device, and call prepare
        to instantiate the processing pipeline.

        Raises:
          Lima2ParamError: a set of params does not fit its schema.
          Lima2BackendError: an error occurred on a device during the tango command.
        """
        logger.debug("Handling prepare transition")

        if self.current_pipeline:
            # Ignore events from the previous pipeline
            # TODO(mdu) a smarter way could be to instantiate a new acquisition object,
            # with its own state machine, for every prepare() call.
            self.current_pipeline.unregister()

        # Homogeneous processing
        ctl = copy.deepcopy(ctl_params)
        rcv_plist = [copy.deepcopy(acq_params) for _ in self.receivers]
        proc_plist = [copy.deepcopy(proc_params) for _ in self.receivers]

        for i in range(len(self.receivers)):
            # NOTE: Dectris specific: assign unique filename rank per detector
            # RAW saving stream.
            # TODO(mdu): should be factored to detector-specific logic along
            # with associated code in pipeline.prepare(),
            # pipeline_progress_by_channel().
            if "saving" in rcv_plist[i]:
                rcv_plist[i]["saving"]["filename_rank"] = i
                if type(self.topology) is DynamicDispatch:
                    rcv_plist[i]["saving"]["include_frame_idx"] = True

            match proc_params["class_name"]:
                case "LimaProcessingLegacy":
                    legacy.finalize_params(
                        proc_params=proc_plist[i],
                        receiver_idx=i,
                        topology=self.topology,
                    )
                case "LimaProcessingSmx":
                    smx.finalize_params(
                        proc_params=proc_plist[i],
                        receiver_idx=i,
                        num_receivers=len(self.receivers),
                        topology=self.topology,
                    )
                case "LimaProcessingXpcs":
                    xpcs.finalize_params(
                        proc_params=proc_plist[i],
                        receiver_idx=i,
                        topology=self.topology,
                    )
                case "LimaProcessingFailing":
                    failing.finalize_params(
                        proc_params=proc_plist[i],
                        topology=self.topology,
                    )
                case _:
                    raise NotImplementedError

        validate_t0 = time.perf_counter()

        # NOTE: Param validation can strongly impact the total time spent in the
        # prepare() call. To alleviate this, we try to cache as much as
        # possible:
        # - the schemas, in control and receiver devices -> avoids fetching them
        #   from tango db every time,
        # - the validator, created from the parsed schema (cached by
        #   validate()).

        def validate_control(control: TangoControl, params: dict[str, Any]) -> None:
            schema = control.fetch_params_schema()
            try:
                validate(instance=params, schema=schema)
            except ValidationError as e:
                raise Lima2ParamError(
                    e.message,
                    where="control params",
                    path=list_to_jsonpath(e.instance_path),
                    schema=get_subschema(orjson.loads(schema), e.schema_path[:-1]),
                ) from e

        def validate_receiver_params(
            receiver: TangoReceiver,
            rcv_params: dict[str, Any],
        ) -> None:
            rcv_schema = receiver.fetch_params_schema()
            try:
                validate(instance=rcv_params, schema=rcv_schema)
            except ValidationError as e:
                raise Lima2ParamError(
                    e.message,
                    where=f"acquisition params for {receiver.name}",
                    path=list_to_jsonpath(e.instance_path),
                    schema=get_subschema(orjson.loads(rcv_schema), e.schema_path[:-1]),
                ) from e

        def validate_proc_params(
            receiver: TangoReceiver,
            proc_params: dict[str, Any],
        ) -> None:
            proc_class: str = proc_params["class_name"]
            proc_schema = receiver.fetch_proc_schema(proc_class=proc_class)
            try:
                validate(instance=proc_params, schema=proc_schema)
            except ValidationError as e:
                raise Lima2ParamError(
                    e.message,
                    where=f"processing params for {receiver.name}",
                    path=list_to_jsonpath(e.instance_path),
                    schema=get_subschema(orjson.loads(proc_schema), e.schema_path[:-1]),
                ) from e

        validate_fut = [
            asyncio.to_thread(validate_control, control=self.control, params=ctl)
        ]
        for rcv, rcv_p, proc_p in zip(
            self.receivers, rcv_plist, proc_plist, strict=True
        ):
            validate_fut.append(
                asyncio.to_thread(
                    validate_receiver_params, receiver=rcv, rcv_params=rcv_p
                )
            )
            validate_fut.append(
                asyncio.to_thread(
                    validate_proc_params, receiver=rcv, proc_params=proc_p
                )
            )

        # Raise the first exception to occur in one of the validations
        await asyncio.gather(*validate_fut)

        logger.debug(
            f"All params validated in {naturaltime(time.perf_counter() - validate_t0)}"
        )

        acq_id = uuid1()

        # Prepare concurrently
        ctl_prep = self.control.prepare(uuid=acq_id, params=ctl)
        rcv_preps = [
            rcv.prepare(uuid=acq_id, acq_params=rcv_plist[i], proc_params=proc_plist[i])
            for i, rcv in enumerate(self.receivers)
        ]

        t0 = time.perf_counter()
        results = await asyncio.gather(
            ctl_prep,
            *rcv_preps,
            return_exceptions=True,  # Collect exceptions in results
        )
        logger.info(f"Device prepare() took {time.perf_counter() - t0}s")

        errors = [result for result in results if result is not None]
        if any(errors):
            details = textwrap.indent(
                "\n".join([f"{str(error)}" for error in errors]),
                prefix="  ",
            )
            raise Lima2BackendError(
                f"Prepare command failed on {len(errors)} device(s):\n{details}"
            )

        # Instantiate the pipeline
        self.current_pipeline = await self.get_pipeline(uuid=acq_id)

        async def on_finished(errors: list[str]) -> None:
            logger.info("All processing devices done")
            if len(errors) == 0:
                logger.info("✅ Pipeline finished without errors")
                await self.update_runstate(event=RunState.PROC_DONE)
            else:
                logger.error("🆘 Pipeline finished with errors: see above 🔥")

        async def on_error(evt: PipelineErrorEvent) -> None:
            """On pipeline error, abort the acquisition."""
            logger.error(f"⁉️ Current pipeline {acq_id} failed. {evt.error_msg}")
            await self.update_runstate(event=RunState.PROC_EXCEPTION)

        await self.current_pipeline.connect(on_finished=on_finished, on_error=on_error)

        self.current_pipeline.prepare(
            acq_params=acq_params,
            proc_params=proc_params,
            det_info=await self.det_info(),
        )

        await self.clear_previous_pipelines()

        logger.info(f"Ready for acquisition {acq_id}")

        return acq_id

    @user_command(allowed_states=[State.PREPARED])
    async def start(self) -> None:
        """Call start on all devices.

        Raises:
          Lima2BackendError: an error occurred on a device during the tango command.
        """
        logger.debug("Handling start transition")

        self.finished_receivers = set()

        self.runstate = RunState.RUNNING

        # Start concurrently
        ctl_start = self.control.start()
        rcv_starts = [rcv.start() for rcv in self.receivers]

        results = await asyncio.gather(
            ctl_start,
            *rcv_starts,
            return_exceptions=True,  # Collect exceptions in results
        )

        errors = [result for result in results if result is not None]
        if any(errors):
            details = textwrap.indent(
                "\n".join([f"{str(error)}" for error in errors]),
                prefix="  ",
            )
            raise Lima2BackendError(
                f"Start command failed failed on {len(errors)} device(s):\n{details}"
            )

        if self.current_pipeline:
            self.current_pipeline.start()
        else:
            # NOTE: this can happen if the conductor is restarted between prepare and start calls
            logger.warning(
                "Started acquisition without a handle on the current pipeline. "
                "Reduced data fetching not started."
            )

        logger.info("🚄 Acquisition running 🚄")

    async def trigger(self) -> None:
        """Call trigger on the Control device."""
        if self.runstate == RunState.RUNNING:
            await self.control.trigger()
        else:
            logger.warning(f"Got trigger() while {self.runstate.name} -> ignoring")

    @user_command(allowed_states=[State.FAULT, State.IDLE, State.UNKNOWN])
    async def reset(self) -> None:
        """Reset the devices to recover from FAULT state."""
        logger.info("Calling reset on every device")

        await asyncio.gather(
            self.control.reset(),
            *[receiver.reset() for receiver in self.receivers],
        )

        self.runstate = RunState.IDLE

    @user_command(allowed_states=[State.RUNNING, State.FAULT, State.IDLE])
    async def stop(self) -> None:
        """Stop the running acquisition."""

        await self.stop_all_running()

        nb_frames_xferred = await self.nb_frames_xferred()
        logger.warning(
            f"Stop requested after {nb_frames_xferred.sum} "
            f"({' + '.join([str(count.value) for count in nb_frames_xferred.counters])}) frames."
        )

        # control.close() is called in update_runstate when processings are done

    ###########################################################################
    # Run event handlers
    ###########################################################################

    async def stop_all_running(self) -> None:
        async def stop_if_running(device: TangoDevice) -> None:
            acq_state = await device.acq_state()
            running = acq_state == DeviceState.RUNNING
            if running:
                await device.stop()

        await asyncio.gather(
            *[stop_if_running(device=dev) for dev in [self.control, *self.receivers]],
        )

    async def update_runstate(self, event: RunState) -> None:
        """Notify the RunState of finished acquisition or processing."""

        # NOTE(mdu) A more robust mechanism could be a queue of events coupled
        # with a state machine.

        logger.debug(
            f"RunState = {self.runstate.name} ({self.runstate}) + {event.name} ({event})"
        )

        # NOTE: update self.runstate straight away, before calling any async methods.
        prev_runstate = self.runstate
        self.runstate |= event

        if event in (RunState.ACQ_EXCEPTION, RunState.PROC_EXCEPTION):
            if prev_runstate & RunState.FAULT:
                logger.debug("Already in FAULT -> skipping abort")
            else:
                logger.debug(f"Aborting for {event.name} while {self.runstate.name=}")
                await self.stop_all_running()

        if event == RunState.PROC_DONE:
            if self.current_pipeline:
                # Stop reduced data fetching, master file generation
                logger.debug("Joining pipeline")
                try:
                    await self.current_pipeline.close()
                except Exception:
                    logger.error(
                        f"Error in pipeline.close():\n{traceback.format_exc()}"
                    )
                logger.info("Closed pipeline 👌👌👌")
        elif event == RunState.PROC_EXCEPTION:
            if self.current_pipeline:
                logger.debug("Pipeline exception -> joining")
                try:
                    await self.current_pipeline.close()
                except Exception:
                    logger.error(
                        f"Error in pipeline.close():\n{traceback.format_exc()}"
                    )
                logger.info("Closed pipeline after processing exception 🤕")

        if prev_runstate & RunState.PROC_EXCEPTION and event == RunState.ACQ_DONE:
            logger.info("Acquisition done after processing failed")
            await self.control.close()
            self.runstate = RunState.FAULT
            logger.info("😥 Acquisition finished with processing errors 😥")
        elif prev_runstate & RunState.ACQ_EXCEPTION and event == RunState.PROC_DONE:
            logger.info("Processing done after acquisition failed")
            await self.control.close()
            self.runstate = RunState.FAULT
            logger.info("😥 Acquisition finished with acquisition errors 😥")

        if prev_runstate & RunState.FAULT:
            logger.debug(
                f"Runstate update {event.name} received while in {prev_runstate=}"
            )

        if self.runstate == RunState.DONE:
            # Acquisition success and processing success

            # TODO(mdu) here we have a race condition: we sometimes see
            # control.close() called after it is already closed (in idle state).
            # This would be better handled by the event queue + state machine system.
            logger.info("Runstate is DONE -> calling control.close()")
            await self.control.close()
            self.runstate = RunState.IDLE
            logger.info("🙌 Acquisition finished 🙌")
        elif event in (RunState.ACQ_DONE, RunState.PROC_DONE):
            # Either ACQ_DONE or PROC_DONE but not both
            logger.debug(f"Runstate is {self.runstate.name} ({self.runstate.value})")

        logger.info(
            f"RunState = {prev_runstate.name} ({prev_runstate}) "
            f"+ {event.name} ({event}) "
            f"= {self.runstate.name} ({self.runstate})"
        )

    ###########################################################################
    # Pipelines
    ###########################################################################

    async def list_pipelines(self) -> list[UUID]:
        """Fetch the list of pipeline UUIDs"""
        pipelines: set[UUID] = set()
        for receiver in self.receivers:
            for name in await receiver.list_pipelines():
                pipelines.add(UUID(name))

        return list(pipelines)

    async def get_pipeline(self, uuid: Literal["current"] | str | UUID) -> Pipeline:
        """Get a specific pipeline by uuid.

        Automatically connects to the processing devices if the pipeline
        instance doesn't exist yet (hence the async).

        Raises:
          Lima2NotFound: pipeline uuid not found in list of pipelines
        """

        if uuid == "current":
            if self.current_pipeline is not None:
                return self.current_pipeline
            else:
                raise Lima2NotFound("No current pipeline: call prepare first")
        elif type(uuid) is str:
            uuid = UUID(uuid)

        assert type(uuid) is UUID

        if uuid in self.cached_pipelines:
            return self.cached_pipelines[uuid]

        pipeline_list = await self.list_pipelines()
        if uuid not in pipeline_list:
            raise Lima2NotFound(
                f"Pipeline {uuid} not found in existing pipelines: {pipeline_list}"
            )

        pipeline = processing.from_uuid(
            uuid=uuid,
            topology=self.topology,
            tango_timeout_s=self.tango_timeout_s,
        )

        self.cached_pipelines[uuid] = pipeline

        return pipeline

    async def clear_previous_pipelines(self) -> list[str]:
        """Erase all pipelines except the current one."""
        if self.current_pipeline is not None:
            current = self.current_pipeline.uuid
        else:
            current = None

        async def clear(receiver: TangoReceiver) -> list[str]:
            """Clear previous pipelines from a single receiver device."""
            pipelines = await receiver.list_pipelines()

            cleared: list[str] = []
            for uuid_str in pipelines:
                if uuid_str != str(current):
                    logger.debug(
                        f"Erasing pipeline {uuid_str} from recv {receiver.name}"
                    )
                    await receiver.erase_pipeline(uuid_str)
                    cleared.append(uuid_str)
            return cleared

        futures = [clear(receiver=rcv) for rcv in self.receivers]
        results = await asyncio.gather(*futures, return_exceptions=True)

        cleared: set[str] = set()
        for rcv, res in zip(self.receivers, results, strict=True):
            if isinstance(res, BaseException):
                logger.warning(
                    f"Exception while clearing pipelines from {rcv.name}: "
                    + "".join(traceback.format_exception(res))
                )
            else:
                cleared = cleared.union(res)

        logger.info(f"Cleared pipelines {[uuid for uuid in set(cleared)]}")

        # Reset local cache
        if self.current_pipeline is not None:
            self.cached_pipelines = {self.current_pipeline.uuid: self.current_pipeline}
        else:
            self.cached_pipelines = {}

        return list(cleared)

    ###########################################################################
    # Info
    ###########################################################################

    async def nb_frames_acquired(self) -> SingleCounter:
        return await self.control.nb_frames_acquired()

    async def nb_frames_xferred(self) -> ProgressCounter:
        return ProgressCounter(
            name="nb_frames_xferred",
            counters=[await rcv.nb_frames_xferred() for rcv in self.receivers],
        )

    async def det_info(self) -> dict[str, Any]:
        return await self.control.det_info()

    async def det_status(self) -> dict[str, Any]:
        return await self.control.det_status()

    async def det_capabilities(self) -> dict[str, Any]:
        return await self.control.det_capabilities()

    async def errors(self) -> list[str]:
        errors: list[str] = []
        for dev in self.receivers:
            err = await dev.last_error()
            if err == "No error":
                continue

            what, info = unpack_exception(err)

            errors.append(
                format_exception(
                    where=dev.name, when="during acquisition", what=what, info=info
                )
            )

        return errors

    ###########################################################################
    # Event handler registration
    ###########################################################################

    def register_control_callbacks(self) -> None:
        """Register on_state_change callback on the control device"""

        async def on_state_change(new_state: DeviceState) -> None:
            logger.info(f"Control in new state: {new_state}")

        self.control.on_state_change(on_state_change)

    def register_receiver_callbacks(self) -> None:
        """Register on_state_change callback on the receiver devices"""

        # NOTE: Using weakref in event handlers is necessary to allow the
        # garbage collector to destroy the Acquisition object.
        wself = weakref.ref(self)

        async def on_state_change(dev: TangoReceiver, new_state: DeviceState) -> None:
            """Handler for receiver device state changes."""
            logger.info(f"Receiver {dev.name} in new state: {new_state}")

            self_ref = wself()
            if self_ref is None:
                return

            if new_state == DeviceState.FAULT:
                payload = await dev.last_error()

                what, info = unpack_exception(payload)

                logger.error(f"⁉️ FAULT state on {dev.name}. Reason: {what} ({info})")
                await self_ref.update_runstate(event=RunState.ACQ_EXCEPTION)

            elif new_state == DeviceState.IDLE and self_ref.runstate & RunState.RUNNING:
                self_ref.finished_receivers.add(dev)

                if self_ref.finished_receivers == set(self_ref.receivers):
                    logger.info("✅ All frames received")
                    await self_ref.update_runstate(event=RunState.ACQ_DONE)

        for receiver in self.receivers:
            receiver.on_state_change(functools.partial(on_state_change, receiver))

    def register_event_callbacks(self) -> None:
        """Subscribe to events on the control and receiver devices.

        Can be called multiple times: the callback will be updated.
        """
        self.register_control_callbacks()
        self.register_receiver_callbacks()
