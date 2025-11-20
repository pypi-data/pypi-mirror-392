from blissdata.h5api import dynamic_hdf5
from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from ewokscore.task import Task
from pydantic import Field

from ..io.read_xas import read_xas_hdf5
from ..io.types import XdiData


class InputModel(BaseInputModel):
    filename: str = Field(..., description="Bliss HDF5 file name.")
    entry_name: str = Field(
        ..., description="NeXus entry name.", examples=["1.1", "5.2"]
    )
    mono_counter: str = Field(
        ..., description="Counter of the energy or theta value of the monochromator."
    )
    crystal_motor: str = Field(
        ..., description="Motor that selects the monochromator crystal."
    )
    optional_counters: list[str | None] = Field(
        None, description="Counters other than the energy to be added to the XDI data."
    )
    optional_mca_counters: list[str | None] = Field(
        None,
        description="MCA counters (ROI's) other than the energy to be added to the XDI data.",
    )
    livetime_normalization: float | None = Field(
        None,
        description="Live-time normalization in seconds for 'optional_mca_counters' "
        "(`None`: no normalization, `<=0` the median of the elapsed time).",
    )
    skip_mca: dict[str, list[int | None]] = Field(
        None,
        description="Skip detectors from MCA controllers.",
        examples=[{"d08xmap": [1, 3]}],
    )
    retry_timeout: float | None = Field(
        0.0, description="Timeout when trying to read data from HDF5."
    )
    mono_edge_theoretical: float | None = Field(
        None,
        description="The theoretical edge position in 'mono_counter' units.",
    )
    mono_edge_experimental: float | None = Field(
        None,
        description="The experimental edge position in 'mono_counter' units.",
    )


class OutputModel(BaseOutputModel):
    xdi_data: XdiData = Field(..., description="")


class ReadXasHdf5(Task, input_model=InputModel, output_model=OutputModel):
    """Read one XAS scan with XDI structured metadata."""

    def run(self):
        with dynamic_hdf5.File(
            self.inputs.filename, retry_timeout=self.inputs.retry_timeout
        ) as h5file:
            h5scan = h5file[self.inputs.entry_name]
            self.outputs.xdi_data = read_xas_hdf5(
                h5scan,
                mono_counter=self.inputs.mono_counter,
                crystal_motor=self.inputs.crystal_motor,
                counters=self.inputs.optional_counters,
                mca_counters=self.inputs.optional_mca_counters,
                livetime_normalization=self.inputs.livetime_normalization,
                skip_mca=self.inputs.skip_mca,
                mono_edge_theoretical=self.inputs.mono_edge_theoretical,
                mono_edge_experimental=self.inputs.mono_edge_experimental,
            )
