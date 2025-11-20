import pytest
from ewokscore.bindings import execute_graph


@pytest.mark.parametrize("mono_counter", ["mono_enc", "energy"])
def test_convert(example_hdf5_path, mono_counter, tmp_path):
    output_filename = tmp_path / "example_scan13.xdi"
    entry_name = "13.1"
    optional_counters = [
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
    optional_mca_counters = ["Te_Ka"]
    livetime_normalization = 3.0
    crystal_motor = "c_sel"

    load_identifier = "ReadXasHdf5"
    save_identifier = "SaveXasXdi"
    inputs = [
        {
            "task_identifier": load_identifier,
            "name": "filename",
            "value": str(example_hdf5_path),
        },
        {
            "task_identifier": load_identifier,
            "name": "entry_name",
            "value": entry_name,
        },
        {
            "task_identifier": load_identifier,
            "name": "mono_counter",
            "value": mono_counter,
        },
        {
            "task_identifier": load_identifier,
            "name": "crystal_motor",
            "value": crystal_motor,
        },
        {
            "task_identifier": load_identifier,
            "name": "optional_counters",
            "value": optional_counters,
        },
        {
            "task_identifier": load_identifier,
            "name": "optional_mca_counters",
            "value": optional_mca_counters,
        },
        {
            "task_identifier": load_identifier,
            "name": "livetime_normalization",
            "value": livetime_normalization,
        },
        {
            "task_identifier": save_identifier,
            "name": "filename",
            "value": str(output_filename),
        },
    ]

    result = execute_graph(_WORKFLOW, inputs=inputs, outputs=[{"all": False}])
    xdi_file = result["output_filename"]
    assert xdi_file == str(output_filename)


_WORKFLOW = {
    "graph": {"id": "convert", "schema_version": "1.1"},
    "nodes": [
        {
            "id": "load",
            "default_inputs": [],
            "task_type": "class",
            "task_identifier": "ewoksbm08.tasks.read_xas.ReadXasHdf5",
        },
        {
            "id": "save",
            "default_inputs": [],
            "task_type": "class",
            "task_identifier": "ewoksbm08.tasks.save_xas.SaveXasXdi",
        },
    ],
    "links": [
        {
            "source": "load",
            "target": "save",
            "data_mapping": [{"source_output": "xdi_data", "target_input": "xdi_data"}],
        }
    ],
}
