from pathlib import Path

import pytest

tests_dir_path = Path(__file__).resolve().parent


@pytest.fixture()
def inputs_dir_path() -> Path:
    return tests_dir_path / "data" / "inputs"
