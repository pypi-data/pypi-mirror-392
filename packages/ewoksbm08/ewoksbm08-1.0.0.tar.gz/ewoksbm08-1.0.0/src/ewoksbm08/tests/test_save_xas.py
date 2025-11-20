import numpy

from ..io.save_xas import save_xdi_data
from ..io.types import XdiData


def test_save_xas(tmp_path):
    xdi_filename = tmp_path / "example.xdi"

    xdi_metadata = {
        "Beamline": {},
        "Scan": {
            "start_time": "2025-09-02T17:26:14.195421+02:00",
            "end_time": "2025-09-02T17:44:38.146967+02:00",
        },
        "Facility": {"current": 84.5, "fillingMode": "16 bunch"},
        "Mono": {"name": "Si 311", "d_spacing": 1.637039},
    }
    data = {
        "column_names": ["A", "B"],
        "column_data": [numpy.asarray([1, 2, 3]), numpy.asarray([4, 5, 6])],
        "xdi_metadata": xdi_metadata,
    }
    xdi_data = XdiData(**data)

    save_xdi_data(xdi_data, xdi_filename)

    with open(xdi_filename, "r") as f:
        content = f.read()

    expected = """# XDI/1.0 GSE/1.0
# Data collected at BM08-LISA of ESRF preproccessed with the beamline Calibration Tool
# Facility.name: ESRF
# Facility.xray_source: bending magnet
# Facility.current: 84.5
# Facility.fillingMode: 16 bunch
# Beamline.name: BM08-LISA
# Scan.start_time: 2025-09-02T17:26:14.195421+02:00
# Scan.end_time: 2025-09-02T17:44:38.146967+02:00
# Mono.name: Si 311
# Mono.d_spacing: 1.637039
# Mono.notes: LNT cooled
# Column.0: A
# Column.1: B
# -------------
# A B
1.0000000 4.0000000
2.0000000 5.0000000
3.0000000 6.0000000
"""

    print(content)

    assert content == expected
