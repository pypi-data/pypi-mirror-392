import importlib.resources as importlib_resources
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


@contextmanager
def resource_path(*args) -> Generator[Path, None, None]:
    """
    .. code-block:: python

        with resource_path("example.h5") a path:
            ...
    """
    source = importlib_resources.files(__name__).joinpath(*args)
    with importlib_resources.as_file(source) as path:
        if not path.is_file():
            raise FileNotFoundError(f"Not a file: '{path}'")
        yield path
