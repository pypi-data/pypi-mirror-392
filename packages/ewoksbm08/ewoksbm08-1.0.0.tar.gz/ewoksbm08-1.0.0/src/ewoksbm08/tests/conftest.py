import pytest

from .data import resource_path


@pytest.fixture
def example_hdf5_path():
    with resource_path("example.h5") as filename:
        yield filename
