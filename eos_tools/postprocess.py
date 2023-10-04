import logging
from pathlib import Path
from typing import Tuple

from pymatgen.io.vasp import Vasprun

logger = logging.getLogger(__name__)


def parse_volume_and_energy(calc_dir_path: Path) -> Tuple[float, float]:
    """Parse volume and total energy from calculation directory

    Args:
        calc_dir_path (Path): Path object of calculation directory

    Returns:
        Tuple[float, float]: volume and total energy
    """
    logger.info(f" Analysing {calc_dir_path.name}")

    # Extract volume from POSCAR.init
    poscar_path = calc_dir_path / "POSCAR.init"
    with poscar_path.open("r") as f:
        poscar_lines = [line.strip() for line in f]
    lattice_constant = float(poscar_lines[1])
    volume = lattice_constant**3

    logger.info(f"      lattice constant (ang): {lattice_constant}")
    logger.info(f"      volume (ang^3)        : {volume}")

    # Extract total energy from vasprun.xml
    vasprun_xml_path = calc_dir_path / "vasprun.xml"
    vasprun = Vasprun(
        str(vasprun_xml_path),
        parse_dos=False,
        parse_eigen=False,
        parse_potcar_file=False,
    )
    energy = vasprun.final_energy

    logger.info(f"      energy (eV)           : {energy}")

    return volume, energy
