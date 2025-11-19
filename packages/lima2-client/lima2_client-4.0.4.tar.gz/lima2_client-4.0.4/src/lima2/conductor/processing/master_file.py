# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Master file generation utilities."""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version
from typing import Any, Literal, TypedDict

import h5py
import numpy as np
import numpy.typing as npt

from lima2.common.types import FrameInfo, FrameSource, FrameType
from lima2.conductor.topology import GlobalIdx, LookupTable
from lima2.conductor.utils import naturaltime

logger = logging.getLogger(__name__)


class SavingParams(TypedDict):
    """Required keys from lima::io::h5::saving_params.

    Not exhaustive.
    """

    base_path: str
    filename_prefix: str
    file_exists_policy: str
    nb_frames_per_file: int
    nx_entry_name: str
    nx_instrument_name: str
    nx_detector_name: str
    nb_dimensions: Literal["dim_4d", "dim_3d_or_4d"]
    enabled: bool


FrameChannel = tuple[FrameSource, FrameInfo, SavingParams | None]
"""
Represents the set of informations required to write a master file
for a particlar frame type.
"""


@dataclass
class MasterFileDescription:
    """Contains all parameters required to build a master file."""

    master_file_path: str
    base_path: str
    filename_prefix: str
    frame_info: FrameInfo
    params: SavingParams

    def data_path(self) -> str:
        """Path to the dataset."""
        entry = self.params["nx_entry_name"]
        instrument = self.params["nx_instrument_name"]
        detector = self.params["nx_detector_name"]
        return f"{entry}/{instrument}/{detector}/data"


def configure(channels: dict[str, FrameChannel]) -> dict[str, MasterFileDescription]:
    """Build a set of MasterFileDescriptions from a set of FrameChannels."""

    mfd: dict[str, MasterFileDescription] = {}
    """Master file descriptions"""

    for name, (source, info, params) in channels.items():
        # Skip non-dense frame sources
        if source.frame_type != FrameType.DENSE:
            logger.info(
                f"Master file not generated for '{name}': not a DENSE frame type"
            )
            continue
        # Skip non-persistent sources
        if params is None:
            logger.info(
                f"Master file not generated for '{name}': no associated saving channel"
            )
            continue
        # Skip source if channel is disabled
        if not params["enabled"]:
            logger.info(
                f"Master file not generated for '{name}': saving disabled in this run"
            )
            continue

        base_path = params["base_path"]
        filename_prefix = params["filename_prefix"]
        file_exists_policy = params["file_exists_policy"]

        master_file_path = f"{base_path}/{filename_prefix}_master.h5"

        if os.path.exists(master_file_path) and file_exists_policy != "overwrite":
            raise RuntimeError(
                f"Master file (channel={source.saving_channel}) exists at {master_file_path} "
                f"but {file_exists_policy=}. Cannot enable master file generation."
            )

        logger.info(
            f"Master file will be generated for source '{name}' at {master_file_path}"
        )

        mfd[name] = MasterFileDescription(
            master_file_path=master_file_path,
            base_path=base_path,
            frame_info=info,
            filename_prefix=filename_prefix,
            params=params,
        )

    return mfd


@dataclass
class MasterFileMetadata:
    acq_params: dict[str, Any]
    proc_params: dict[str, Any]
    det_info: dict[str, Any]


class MasterFileGenerator:
    def __init__(self) -> None:
        self.mfd: dict[str, MasterFileDescription] = {}
        """Master file descriptions"""

    def prepare(
        self,
        frame_channels: dict[str, FrameChannel],
        metadata: MasterFileMetadata,
    ) -> None:
        self.mfd = configure(channels=frame_channels)
        self.metadata = metadata

    async def write_master_files(self, num_receivers: int, lut: LookupTable) -> None:
        """For each saved frame channel, write the virtual dataset to the master file."""
        for description in self.mfd.values():
            layout = await build_layout(
                num_receivers=num_receivers,
                lookup_table=lut,
                frame_info=description.frame_info,
                params=description.params,
            )

            write_t0 = time.perf_counter()

            with h5py.File(description.master_file_path, "w") as master_file:
                write_virtual_dataset(
                    file=master_file,
                    nx_entry_name=description.params["nx_entry_name"],
                    nx_instrument_name=description.params["nx_instrument_name"],
                    nx_detector_name=description.params["nx_detector_name"],
                    layout=layout,
                )

                write_metadata(
                    master_file=master_file,
                    metadata=self.metadata,
                    nx_entry_name=description.params["nx_entry_name"],
                    nx_instrument_name=description.params["nx_instrument_name"],
                    nx_detector_name=description.params["nx_detector_name"],
                )

            logger.info(
                f"Master file written in {naturaltime(time.perf_counter() - write_t0)} "
                f"at {description.master_file_path}"
            )


class Indexer:
    """
    Keeps track of frames acquired by a receiver and holds a VirtualSource for
    each completed file.
    """

    UNKNOWN = np.iinfo(np.uint32).max

    def __init__(
        self,
        file_size: int,
        base_path: str,
        filename_prefix: str,
        datapath: str,
        frame_info: FrameInfo,
    ) -> None:
        self.file_size = file_size
        self.datapath = datapath
        self.base_path = base_path
        self.filename_prefix = filename_prefix
        self.frame_info = frame_info

        self.cur_index = np.full(
            fill_value=Indexer.UNKNOWN, shape=file_size, dtype=np.uint32
        )
        """Array of frame indices. Copied to vsource when a whole file is indexed."""
        self.frame_cursor = 0
        """Index of the next frame to map in the current file."""
        self.file_cursor = 0
        """Index of the current file."""
        self.vsources: list[tuple[npt.NDArray[np.uint32], h5py.VirtualSource]] = []
        """List of (mapping, virtual source) tuples."""
        self.num_indexed = 0
        """Number of frames indexed."""

    def _index_next_file(self, index: npt.NDArray[np.uint32]) -> None:
        """Add a vsource using the content of index."""
        filepath = f"{self.base_path}/{self.filename_prefix}_{self.file_cursor:05d}.h5"

        vsource = h5py.VirtualSource(
            filepath,
            self.datapath,
            shape=(
                index.size,
                self.frame_info.num_channels,
                self.frame_info.height,
                self.frame_info.width,
            ),
        )

        self.vsources.append((index.copy(), vsource))
        self.num_indexed += index.size
        self.frame_cursor = 0
        self.file_cursor += 1

    def index(self, frame_idx: GlobalIdx) -> None:
        self.cur_index[self.frame_cursor] = frame_idx

        if self.frame_cursor + 1 >= self.file_size:
            self._index_next_file(index=self.cur_index)
            self.cur_index[:] = Indexer.UNKNOWN  # safety measure
        else:
            self.frame_cursor += 1

    def flush(self) -> None:
        """Index any remaining frames in the index to the last file."""
        remainder = self.cur_index[: self.frame_cursor]
        if remainder.size > 0:
            self._index_next_file(index=remainder)


async def build_index(
    num_receivers: int,
    lookup_table: LookupTable,
    frame_info: FrameInfo,
    base_path: str,
    filename_prefix: str,
    datapath: str,
    frames_per_file: int,
) -> list[Indexer]:
    """Using the lookup table, build an index of virtual sources for each receiver.

    This procedure uses the provided lookup table to determine where each frame
    is saved. It expects the lookup table to be updated by an external task until
    all frames have been associated with a receiver.
    """

    # We can't expect to know the number of frames we will acquire, since
    # acquisition may be cancelled. The VirtualLayout will be created at the end.
    # During the acquisition, all we have to do is map frames to files when
    # files become complete. All we need for that is the lookup table and
    # number of frames saved per file.

    indexers = [
        Indexer(
            file_size=frames_per_file,
            base_path=base_path,
            filename_prefix=f"{filename_prefix}_{i}",
            datapath=datapath,
            frame_info=frame_info,
        )
        for i in range(num_receivers)
    ]

    async for mapping in lookup_table.iterate():
        indexers[mapping.receiver_idx].index(frame_idx=mapping.frame_idx)

    for indexer in indexers:
        indexer.flush()

    return indexers


async def build_layout(
    num_receivers: int,
    lookup_table: LookupTable,
    frame_info: FrameInfo,
    params: SavingParams,
) -> h5py.VirtualLayout:
    """Build a VirtualLayout from the lookup table.

    This procedure uses the provided lookup table to determine where each frame
    is saved. It expects the lookup table to be updated by an external task until
    all frames have been associated with a receiver.
    """

    base_path = params["base_path"]

    logger.info(f"Generating virtual dataset for files at {base_path}")

    filename_prefix = params["filename_prefix"]
    nx_entry_name = params["nx_entry_name"]
    nx_instrument_name = params["nx_instrument_name"]
    nx_detector_name = params["nx_detector_name"]

    indexers = await build_index(
        num_receivers=num_receivers,
        lookup_table=lookup_table,
        frame_info=frame_info,
        base_path=base_path,
        filename_prefix=filename_prefix,
        datapath=f"{nx_entry_name}/{nx_instrument_name}/{nx_detector_name}/data",
        frames_per_file=params["nb_frames_per_file"],
    )

    num_indexed = sum([indexer.num_indexed for indexer in indexers])
    logger.info(f"Total number of frames indexed: {num_indexed}")

    layout_shape = determine_layout_shape(
        num_frames=num_indexed,
        frame_info=frame_info,
        nb_dimensions=params["nb_dimensions"],
    )

    layout = h5py.VirtualLayout(
        shape=layout_shape,
        dtype=frame_info.pixel_type,
    )

    for indexer in indexers:
        for index, vsource in indexer.vsources:
            logger.debug(f"{index} -> {vsource.path}")
            layout[index] = vsource

    return layout


def determine_layout_shape(
    num_frames: int,
    frame_info: FrameInfo,
    nb_dimensions: Literal["dim_4d", "dim_3d_or_4d"],
) -> tuple[int, int, int] | tuple[int, int, int, int]:
    """Determine the shape of the virtual layout."""
    layout_shape: tuple[int, int, int] | tuple[int, int, int, int]

    if frame_info.num_channels != 1:
        # multiple pixel channels -> 4d
        layout_shape = (
            num_frames,
            frame_info.num_channels,
            frame_info.height,
            frame_info.width,
        )
    elif nb_dimensions == "dim_4d":
        # 1 pixel channel but dim_4d -> keep 4d
        layout_shape = (
            num_frames,
            frame_info.num_channels,
            frame_info.height,
            frame_info.width,
        )
    elif nb_dimensions == "dim_3d_or_4d":
        # 1 pixel channel and 3d ok -> reduce to 3d
        layout_shape = (num_frames, frame_info.height, frame_info.width)
    else:
        raise ValueError(
            f"Invalid combination of {frame_info.num_channels=} and {nb_dimensions=}"
        )

    return layout_shape


def write_virtual_dataset(
    file: h5py.File,
    nx_entry_name: str,
    nx_instrument_name: str,
    nx_detector_name: str,
    layout: h5py.VirtualLayout,
) -> None:
    """Commit a virtual dataset to a master file."""

    data_path = f"{nx_entry_name}/{nx_instrument_name}/{nx_detector_name}/data"
    measurement_path = f"{nx_entry_name}/measurement"
    plot_path = f"{nx_entry_name}/{nx_instrument_name}/{nx_detector_name}/plot/data"

    # Create VDS
    dataset = file.create_virtual_dataset(data_path, layout=layout)
    dataset.attrs["interpretation"] = "image"

    # Create links
    file[f"{measurement_path}/data"] = file[data_path]
    file[measurement_path].attrs["NX_class"] = "NXcollection"
    file[plot_path] = file[data_path]

    logger.debug(f"Virtual dataset written at {file.filename}")


def write_metadata(
    master_file: h5py.File,
    metadata: MasterFileMetadata,
    nx_entry_name: str,
    nx_instrument_name: str,
    nx_detector_name: str,
) -> None:
    """Add metadata copied from the first file to a master file."""
    logger.debug(f"{master_file.filename}: writing metadata")

    # Root
    root = master_file["/"]
    root.attrs["NX_class"] = "NXroot"
    root.attrs["default"] = nx_entry_name
    root.attrs["file_name"] = master_file.filename
    root.attrs["creator"] = f"lima2-conductor v{version('lima2-client')}"
    root.attrs["file_time"] = datetime.now(timezone.utc).isoformat()

    # Entry
    entry = master_file[f"{nx_entry_name}"]
    entry.attrs["NX_class"] = "NXentry"
    entry.attrs["default"] = f"{nx_instrument_name}/{nx_detector_name}/plot"

    # Instrument
    instrument = entry[f"{nx_instrument_name}"]
    instrument.attrs["NX_class"] = "NXinstrument"
    instrument.attrs["default"] = f"{nx_detector_name}/plot"

    # Detector
    detector = instrument[f"{nx_detector_name}"]
    detector.attrs["NX_class"] = "NXdetector"
    detector.attrs["default"] = "plot"
    write_recursive(
        target=detector,
        name="params",
        value={"acquisition": metadata.acq_params, "processing": metadata.proc_params},
    )

    write_recursive(target=detector, name="info", value=metadata.det_info)

    # Plot
    plot = detector["plot"]
    plot.attrs["NX_class"] = "NXdata"
    plot.attrs["signal"] = "data"


def write_recursive(target: h5py.Group, name: str, value: Any) -> None:
    if type(value) is dict:
        subgroup = target.create_group(name=name)
        subgroup.attrs["NX_class"] = "NXcollection"
        for key, value in value.items():
            write_recursive(target=subgroup, name=key, value=value)
    elif type(value) is list:
        subgroup = target.create_group(name=name)
        subgroup.attrs["NX_class"] = "NXcollection"
        for i, item in enumerate(value):
            write_recursive(target=subgroup, name=f"{i}", value=item)
    else:
        target[name] = value
