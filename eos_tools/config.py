import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Config:
    mode: str
    inputs_dir: str = "data/inputs"
    eos_name: str = "vinet"
    atomic_energy: float = -3.37689


def load_config(path: str) -> Config:
    """Load configs/*.json

    Args:
        path (str): path to configs/*.json

    Returns:
        Config: EOS calculation config dataclass
    """
    with open(path) as f:
        config_dict = json.load(f)
    return Config.from_dict(config_dict)  # type: ignore
