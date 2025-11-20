import logging
import os

import numpy

from .types import XdiData

logger = logging.getLogger(__name__)


def save_xdi_data(xdi_data: XdiData, filename: str) -> None:
    parent = os.path.dirname(filename)
    if parent:
        os.makedirs(parent, exist_ok=True)

    if os.path.exists(filename):
        logger.warning("Overwrite %r", filename)

    header = "\n".join(xdi_data.header_lines())
    data = numpy.column_stack(xdi_data.column_data)
    numpy.savetxt(
        filename,
        data,
        fmt="%.7f",
        header=header,
    )
