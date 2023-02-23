import json
import logging
import re
from pathlib import Path
from typing import Tuple

from pymatgen.io.vasp import Vasprun

logger = logging.getLogger(__name__)


def parse_volume_and_energy(dir_path: Path) -> Tuple[float, float]:
    logger.info(f" Analysing {dir_path.stem}")

    lattice_constant_pattern = re.compile(r"\d+")
    m = lattice_constant_pattern.search(dir_path.stem)
    lattice_constant = float(m.group(0)) / 100
    volume = lattice_constant**3

    logger.info(f"      lattice constant (ang): {lattice_constant}")
    logger.info(f"      volume (ang^3)        : {volume}")

    vasprun_xml_json_path = dir_path / "vasprun_xml.json"
    if vasprun_xml_json_path.exists():
        with vasprun_xml_json_path.open("r") as f:
            vasprun_dict = json.load(f)
    else:
        vasprun_xml_path = dir_path / "vasprun.xml"
        vasprun = Vasprun(str(vasprun_xml_path), parse_potcar_file=False)
        vasprun_dict = vasprun.as_dict()
        with vasprun_xml_json_path.open("w") as f:
            json.dump(vasprun_dict, f, indent=4)
    energy = vasprun_dict["output"]["final_energy"]

    logger.info(f"      energy (eV)           : {energy}")

    return volume, energy
