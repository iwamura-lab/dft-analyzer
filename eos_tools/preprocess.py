from pathlib import Path

import numpy as np
from pymatgen.io.vasp import Poscar


def generate_deformed_structures() -> None:
    """Generate structures with different volume from relaxed structure"""
    # Load POSCAR
    relaxed_poscar_path = Path("relax") / "POSCAR"
    relaxed_structure = Poscar.from_file(str(relaxed_poscar_path)).structure
    perfect_poscar_path = Path("relax") / "POSCAR.init"
    perfect_structure = Poscar.from_file(str(perfect_poscar_path)).structure

    # Calculate the lattice constant of most stable structure
    with perfect_poscar_path.open("r") as f:
        poscar_lines = [line.strip() for line in f]
    eq_lattice_constant = float(poscar_lines[1]) * (
        relaxed_structure.volume / perfect_structure.volume
    ) ** (1 / 3)

    max_volume_strain = 0.08
    line_strain_list = np.linspace(1 - max_volume_strain, 1 + max_volume_strain, 9) ** (
        1 / 3
    )

    for i, strain in enumerate(line_strain_list, 1):
        poscar_lines[1] = str(eq_lattice_constant * strain)

        # Save generated structures as POSCAR
        deformed_dir_path = Path(f"deformed_{str(i).zfill(2)}")
        deformed_dir_path.mkdir()

        poscar_path = deformed_dir_path / "POSCAR"
        with poscar_path.open("w") as f:
            f.write("\n".join(poscar_lines))
