import os

from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from ewokscore.task import Task
from pydantic import Field

from ..io.save_xas import save_xdi_data
from ..io.types import XdiData


class InputModel(BaseInputModel):
    filename: str = Field(..., description="XDI file name.", examples=[])
    xdi_data: XdiData = Field(..., description="XDI data to be saved.", examples=[])


class OutputModel(BaseOutputModel):
    output_filename: str = Field(..., description="XDI file name.")


class SaveXasXdi(Task, input_model=InputModel, output_model=OutputModel):
    """Save one XAS scan as an XDI file."""

    def run(self):
        save_xdi_data(self.inputs.xdi_data, self.inputs.filename)
        self.outputs.output_filename = os.path.abspath(self.inputs.filename)
