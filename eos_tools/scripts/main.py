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


@click.command()
@click.argument("config_file", nargs=1)
def main(config_file):
    """Usefull tools to perform EOS calculation by DFT"""
    logging.basicConfig(level=logging.INFO)
    logging.info(" Load config file")
    config = load_config(config_file)

    if config.mode == "preprocess":
        pass

    if config.mode == "postprocess":
        logging.info(" Start EOS postprocessing")
        logging.info(f"     inputs dir: {config.inputs_dir}")

        calc_info_dict = {}
        calc_info_dict["inputs_dir"] = config.inputs_dir
        calc_info_dict["eos_name"] = config.eos_name

        input_dir_path_list = [
            dir_path for dir_path in Path(config.inputs_dir).glob("**/*[0-9][0-9][0-9]")
        ]
        ev_data = np.array(
            [
                parse_volume_and_energy(input_dir_path)
                for input_dir_path in tqdm(input_dir_path_list)
            ]
        )

        # Calculate cohesive energy using n_atom obtained from some structure
        struct = Poscar.from_file(str(input_dir_path_list[0] / "POSCAR")).structure
        n_atom = struct.frac_coords.shape[0]
        ev_data[:, 1] -= n_atom * config.atomic_energy

        dump_dir_path = Path(config_file).parent
        ev_data_path = dump_dir_path / "ev_data.txt"
        np.savetxt(ev_data_path, ev_data, header="volume(ang^3), energy(eV)")

        logging.info(" Start EOS fitting")
        logging.info(f"     EOS name  : {config.eos_name}")

        eos = EOS(eos_name=config.eos_name).fit(ev_data[:, 0], ev_data[:, 1])
        calc_info_dict["e0"] = eos.e0
        calc_info_dict["v0"] = eos.v0
        calc_info_dict["a0"] = eos.v0 ** (1 / 3)
        calc_info_dict["b0"] = eos.b0_GPa

        logging.info(" Dumping eos_analysis.json")

        eos_analysis_json_path = dump_dir_path / "eos_analysis.json"
        with eos_analysis_json_path.open("w") as f:
            json.dump(calc_info_dict, f, indent=4)

        logging.info(" Dumping eos.png")

        plt = eos.plot()
        plt.savefig(dump_dir_path / "eos.png")
