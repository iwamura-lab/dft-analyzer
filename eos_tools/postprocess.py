import logging
from pathlib import Path
from typing import Tuple

from pymatgen.io.vasp import Poscar, Vasprun

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
    poscar = Poscar.from_file(str(poscar_path), check_for_POTCAR=False)
    volume = poscar.structure.volume

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
