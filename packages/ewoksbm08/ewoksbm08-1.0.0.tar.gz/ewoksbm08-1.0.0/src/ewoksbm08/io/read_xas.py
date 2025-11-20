import logging
import re

import h5py
import numpy
from blissdata.h5api.dynamic_hdf5 import Group

from .types import XdiData

logger = logging.getLogger(__name__)

GroupType = Group | h5py.Group


def read_xas_hdf5(
    h5scan: GroupType,
    mono_counter: str,
    crystal_motor: str,
    counters: list[str],
    mca_counters: list[str],
    livetime_normalization: float | None = None,
    skip_mca: dict[str, list[int | None]] = None,
    mono_edge_theoretical: float | None = None,
    mono_edge_experimental: float | None = None,
) -> XdiData:
    """
    :param h5scan: NXentry group of one Bliss scan.
    :param mono_counter: energy or theta counter.
    :param crystal_motor: defines the mono crystal that is selected.
    :param counters: map name in the measurement group to name in XDI.
    :param mca_counters: counters the be extracted for all MCA detector. Use `skip_mca` to skip some.
    :param livetime_normalization: normalize `mca_counters` to a common live-time.
    :param skip_mca: scan MCA detector.
    :param mono_edge_theoretical: theoretical edge position in `mono_counter` units.
    :param mono_edge_experimental: experimental edge position in `mono_counter` units.
    :returns: XAS scan object
    """
    xdi_metadata = {
        "Beamline": {},
    }

    # Scan
    start_time = h5scan["start_time"][()].decode()
    end_time = h5scan["end_time"][()].decode()
    xdi_metadata["Scan"] = {"start_time": start_time, "end_time": end_time}

    # Facility
    instrument = h5scan["instrument"]
    current = instrument["machine/current"][()]
    filling_mode = instrument["machine/filling_mode"][()].decode()
    xdi_metadata["Facility"] = {
        "current": current,
        "fillingMode": filling_mode,
    }

    # Mono
    si_hkl = _get_si_hkl(h5scan, crystal_motor)
    d_spacing = _mono_d_spacing(*si_hkl)
    si_hkl_string = "".join(map(str, si_hkl))
    xdi_metadata["Mono"] = {"name": f"Si {si_hkl_string}", "d_spacing": d_spacing}

    # Energy in eV from monochromator counter
    measurement = h5scan["measurement"]
    if mono_counter not in measurement:
        raise ValueError(
            f"{mono_counter!r} is not in {measurement.file.filename}::{measurement.name}"
        )
    mono_dset = measurement[mono_counter]
    energy = _convert_to_energy(
        mono_dset, d_spacing, mono_edge_theoretical, mono_edge_experimental
    )
    column_names = ["energy"]
    column_data = [energy]

    # Regular counters
    if counters:
        ctr_column_names, ctr_column_data = _get_counter_columns(h5scan, counters)
        column_names += ctr_column_names
        column_data += ctr_column_data

    # MCA counters
    if mca_counters:
        mca_column_names, mca_column_data = _get_mca_columns(
            h5scan, mca_counters, livetime_normalization, skip_mca or {}
        )
        column_names += mca_column_names
        column_data += mca_column_data

    # Ensure all columns have the same length
    lengths = [len(values) for values in column_data]
    if len(set(lengths)) > 1:
        n = min(lengths)
        column_data = [values[:n] for values in column_data]

    return XdiData(
        column_names=column_names, column_data=column_data, xdi_metadata=xdi_metadata
    )


def _convert_to_energy(
    mono_dset: h5py.Dataset,
    d_spacing: float,
    mono_edge_theoretical: float | None,
    mono_edge_experimental: float | None,
) -> numpy.ndarray:
    """Energy in eV from theta in radians or energy in keV or eV."""
    mono_values = mono_dset[()]
    if mono_edge_theoretical is not None and mono_edge_experimental is not None:
        mono_values += round(mono_edge_theoretical - mono_edge_experimental, 7)

    # TODO: should this be fixed in blissdata? When there are no units, it waits retry_timeout
    # seconds and then returns, even when the scan is over.
    mono_units = dict(mono_dset.attrs).get("units", "").lower()
    if mono_units == "ev":
        return mono_values
    if mono_units == "kev":
        return mono_values * 1000
    if mono_units in ("deg", "degree", "degrees"):
        mono_values = numpy.radians(mono_values)
        mono_units = ""
    if mono_units in ("", "rad", "radian", "radians"):
        return _theta_to_energy(mono_values, d_spacing)
    raise ValueError(f"Unknown monochromator counter units {mono_units!r}")


def _mono_d_spacing(si_h: int, si_k: int, si_l: int) -> float:
    """D-spacing from Si HKL planes in Å.

    Cubic lattice: dhkl(Å) = A0(Å) / sqrt(h^2+k^2+l^2)
    """
    si_lattice_constant = 5.42944537  # Å
    return si_lattice_constant / numpy.sqrt(si_h**2 + si_k**2 + si_l**2)


def _theta_to_energy(theta_angle: float | numpy.ndarray, d_spacing: float) -> float:
    """Converts the monochromator angle in radians into energy
    given a monochromator crystal d-spacing.

    Bragg's Law: E(eV) = (h * c) / (2 * dhkl(Å) * sinθ)
    """
    hc = 12398.42014541  # Å/eV
    sin_theta = numpy.sin(theta_angle)
    return numpy.round(hc / (2 * d_spacing * sin_theta), 3)


def _get_counter_columns(
    h5scan: GroupType, counters: list[str]
) -> tuple[list[str], list[numpy.ndarray]]:
    measurement = h5scan["measurement"]
    column_names = []
    column_data = []
    for name in counters:
        if name in measurement:
            column_names.append(name)
            column_data.append(measurement[name][()])
        else:
            logger.warning(
                "Skip: regular counter %r not in %r",
                name,
                f"{measurement.file.filename}::{measurement.name}",
            )
    return column_names, column_data


def _get_mca_columns(
    h5scan: GroupType,
    mca_counters: list[str],
    livetime_normalization: float | None,
    skip_mca: dict[str, list[int]],
) -> tuple[list[str], list[numpy.ndarray]]:
    instrument = h5scan["instrument"]
    mca_detectors = _get_mca_detectors(instrument)
    if not mca_detectors:
        logger.warning(
            "No MCA detector found in %s::%s", h5scan.file.filename, instrument.name
        )
        return [], []

    if livetime_normalization is not None and livetime_normalization <= 0:
        livetime_normalization = _get_count_time(h5scan) or -1

    column_short_names = []
    column_prefixes = []
    column_data = []

    for (controller_name, detector_index), detector in mca_detectors.items():
        skip_indices = skip_mca.get(controller_name, [])
        if detector_index in skip_indices:
            continue
        for counter_name in mca_counters:
            values = _mca_counter_values(detector, counter_name, livetime_normalization)
            if values is None:
                continue
            column_short_name = f"{counter_name}_{detector_index}"
            column_short_names.append(column_short_name)
            column_prefixes.append(controller_name)
            column_data.append(values)

    if len(column_short_names) != len(set(column_short_names)):
        column_names = [
            f"{prefix}_{name}"
            for prefix, name in zip(column_prefixes, column_short_names)
        ]
    else:
        column_names = column_short_names

    return column_names, column_data


def _get_mca_detectors(instrument: GroupType) -> dict[tuple[str, int], GroupType]:
    """Find all HDF5 groups that belong to a detector index of an MCA controller."""
    groups = {}
    for name in instrument:
        item = instrument[name]
        if not isinstance(item, GroupType):
            continue

        if "type" in item:
            detector_type = item["type"][()].decode()
        else:
            continue

        if detector_type == "mca":
            match = re.match(r"^(.*?)_det(\d+)$", name)
            if match:
                controller_name = match.group(1)
                detector_index = int(match.group(2))
                groups[(controller_name, detector_index)] = item
    return groups


def _mca_counter_values(
    detector: GroupType,
    counter_name: str,
    livetime_normalization: float | None,
) -> numpy.ndarray | None:
    """Return the counter values (if present) for a detector index of an MCA controller."""
    if counter_name not in detector:
        logger.warning(
            "Skip: MCA counter %r not in %r",
            counter_name,
            f"{detector.file.filename}::{detector.name}",
        )
        return None

    values = detector[counter_name][()]

    # Extract live-time to normalize to from elapsed time per point
    if livetime_normalization is not None and livetime_normalization <= 0:
        if "elapsed_time" in detector:
            elapsed_time = detector["elapsed_time"][()]
            livetime_normalization = numpy.nanmedian(elapsed_time)
            logger.info(
                "Median elapsed time per scan point: %s seconds", livetime_normalization
            )
        else:
            livetime_normalization = None
            logger.warning(
                "Skip live-time normalization of MCA counter %r since %r is not in %r",
                counter_name,
                "elapsed_time",
                f"{detector.file.filename}::{detector.name}",
            )

    # Normalize counts to a common live-time
    if livetime_normalization is not None:
        if "live_time" in detector:
            effective_livetime = detector["live_time"][()]
            if values.size != effective_livetime.size:
                n = min(values.size, effective_livetime.size)
                values = values[:n]
                effective_livetime = effective_livetime[:n]
            values = values / effective_livetime * livetime_normalization
        else:
            logger.warning(
                "Skip live-time normalization of MCA counter %r since %r is not in %r",
                counter_name,
                "live_time",
                f"{detector.file.filename}::{detector.name}",
            )

    return values


def _get_count_time(h5scan: GroupType) -> float | None:
    if "scan_parameters" in h5scan:
        scan_parameters = h5scan["scan_parameters"]
        if "count_time" in scan_parameters:
            count_time = scan_parameters["count_time"][()]
            logger.info("User preset count time: %s seconds", count_time)
            return count_time


def _get_si_hkl(h5scan: GroupType, crystal_motor: str) -> tuple[int, int, int]:
    positioners = h5scan["instrument/positioners"]
    if crystal_motor not in positioners:
        raise ValueError(
            f"{crystal_motor!r} is not in {positioners.file.filename}::{positioners.name}"
        )
    if positioners[crystal_motor][()] > 0:
        return 3, 1, 1
    else:
        return 1, 1, 1
