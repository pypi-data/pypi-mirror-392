import numpy
from pydantic import BaseModel


class XdiBaseModel(BaseModel):
    def header_lines(self, prefix: str = None) -> list[str]:
        lines = []

        for field_name in type(self).model_fields:
            value = getattr(self, field_name)

            if value is None:
                continue

            if isinstance(value, XdiBaseModel):
                lines.extend(
                    value.header_lines(
                        prefix=f"{prefix}.{field_name}" if prefix else field_name
                    )
                )
            else:
                if prefix:
                    lines.append(f"{prefix}.{field_name}: {value}")
                else:
                    lines.append(str(value))

        return lines


class XdiFacility(XdiBaseModel):
    name: str = "ESRF"
    xray_source: str = "bending magnet"
    current: float | None = None
    fillingMode: str | None = None


class XdiBeamline(XdiBaseModel):
    name: str = "BM08-LISA"


class XdiScan(XdiBaseModel):
    start_time: str | None = None
    end_time: str | None = None


class XdiMono(XdiBaseModel):
    name: str | None = None
    d_spacing: float | None = None
    notes: str | None = "LNT cooled"


class XdiSample(XdiBaseModel):
    name: str | None = None


class XdiMetadata(XdiBaseModel):
    """XDI SPECS:

    https://github.com/XraySpectroscopy/XAS-Data-Interchange/blob/master/specification/spec.md
    """

    Scheme: str = "XDI/1.0 GSE/1.0"
    Title: str = (
        "Data collected at BM08-LISA of ESRF preproccessed with the beamline Calibration Tool"
    )
    Facility: XdiFacility
    Beamline: XdiBeamline
    Scan: XdiScan | None = None
    Mono: XdiMono | None = None
    Sample: XdiSample | None = None


class XdiData(BaseModel, arbitrary_types_allowed=True):
    column_names: list[str]
    column_data: list[numpy.ndarray]
    xdi_metadata: XdiMetadata

    def header_lines(self) -> list[str]:
        lines = self.xdi_metadata.header_lines()
        if self.column_names:
            for i, name in enumerate(self.column_names):
                lines.append(f"Column.{i}: {name}")
            lines.append("-------------")
            lines.append(" ".join(self.column_names))
        return lines
