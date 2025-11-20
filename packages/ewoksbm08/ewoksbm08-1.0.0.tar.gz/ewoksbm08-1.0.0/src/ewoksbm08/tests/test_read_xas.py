import h5py

from ..io.read_xas import read_xas_hdf5


def test_read_xas(example_hdf5_path):
    entry_name = "13.1"
    mono_counter = "mono_enc"
    counters = [
        "I0_eh1",
        "I1_eh1",
        "IX_eh1",
        "I0_eh2",
        "I1_eh2",
        "IX_eh2",
        "IR_eh2",
        "volt1",
        "volt2",
    ]
    mca_counters = ["Te_Ka"]
    crystal_motor = "c_sel"

    with h5py.File(example_hdf5_path, mode="r") as h5file:
        xdi_data = read_xas_hdf5(
            h5file[entry_name], mono_counter, crystal_motor, counters, mca_counters
        )

    expected = [
        "energy",
        "I0_eh1",
        "I1_eh1",
        "IX_eh1",
        "I0_eh2",
        "I1_eh2",
        "IX_eh2",
        "IR_eh2",
        "volt1",
        "volt2",
        "Te_Ka_0",
        "Te_Ka_1",
        "Te_Ka_2",
        "Te_Ka_3",
    ]
    assert xdi_data.column_names == expected
