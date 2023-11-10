import json
import logging
from pathlib import Path

import click
import numpy as np
from pymatgen.analysis.eos import EOS
from pymatgen.io.vasp import Poscar
from tqdm import tqdm

from eos_tools.config import load_config
from eos_tools.postprocess import parse_volume_and_energy
from eos_tools.preprocess import generate_deformed_structures


@click.command()
@click.argument("config_file", nargs=1)
def main(config_file):
    """Usefull tools to perform EOS calculation by DFT"""
    logging.basicConfig(level=logging.INFO)
    logging.info(" Load config file")
    config = load_config(config_file)

    if config.mode == "preprocess":
        generate_deformed_structures(config.max_volume_strain, config.n_structure)

    if config.mode == "postprocess":
        logging.info(" Start EOS postprocessing")
        logging.info(f"     calculation directory: {config.calc_root_dir}")

        calc_info_dict = {}
        calc_info_dict["calc_root_dir"] = config.calc_root_dir
        calc_info_dict["eos_name"] = config.eos_name

        calc_dir_path_list = [
            path.parent
            for path in Path(config.calc_root_dir).glob("deformed_*/vasprun.xml")
        ]
        ev_data = np.array(
            [
                parse_volume_and_energy(calc_dir_path)
                for calc_dir_path in tqdm(calc_dir_path_list)
            ]
        )

        # Calculate cohesive energy using n_atom obtained from some structure
        struct = Poscar.from_file(
            str(calc_dir_path_list[0] / "POSCAR"), check_for_POTCAR=False
        ).structure
        n_atom = struct.frac_coords.shape[0]
        ev_data[:, 1] -= n_atom * config.atomic_energy

        outputs_dir_path = Path(config_file).parent
        ev_data_path = outputs_dir_path / "ev_data.txt"
        np.savetxt(ev_data_path, ev_data, header="volume(ang^3), energy(eV)")

        logging.info(" Start EOS fitting")
        logging.info(f"     EOS name  : {config.eos_name}")

        eos = EOS(eos_name=config.eos_name).fit(ev_data[:, 0], ev_data[:, 1])
        calc_info_dict["e0"] = eos.e0
        calc_info_dict["v0"] = eos.v0
        calc_info_dict["a0"] = eos.v0 ** (1 / 3)
        calc_info_dict["b0"] = eos.b0_GPa

        logging.info(" Dumping eos_analysis.json")

        eos_analysis_json_path = outputs_dir_path / "eos_analysis.json"
        with eos_analysis_json_path.open("w") as f:
            json.dump(calc_info_dict, f, indent=4)

        logging.info(" Dumping eos.png")

        plt = eos.plot()
        plt.savefig(outputs_dir_path / "eos.png")
