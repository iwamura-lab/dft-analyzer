import json
import logging
import re
from pathlib import Path

import click
from pymatgen.analysis.eos import EOS
from pymatgen.io.vasp import Vasprun
from tqdm import tqdm


@click.group()
def main():
    """
    analyzer for DFT calculation to compare with machine learning potential
    calculation
    """
    pass


@main.command()
@click.argument("inputs_dir")
@click.option("--eos_name", default="vinet", show_default=True, help="name of EOS")
def eos(inputs_dir, eos_name):
    """analyse the outputs of VASP EOS calculation"""
    logging.basicConfig(level=logging.INFO)

    logging.info(" Start EOS fitting")
    logging.info(f"     inputs dir: {inputs_dir}")
    logging.info(f"     EOS name   : {eos_name}")

    calc_info_dict = {}
    calc_info_dict["inputs_dir"] = inputs_dir
    calc_info_dict["eos_name"] = eos_name
    volumes, energies = [], []
    lattice_constant_pattern = re.compile(r"\d+")

    input_dir_path_list = [
        dir_path for dir_path in Path(inputs_dir).glob("**/*[0-9][0-9][0-9]")
    ]
    for input_dir_path in tqdm(input_dir_path_list):

        logging.info(f" Analysing {input_dir_path.stem}")

        m = lattice_constant_pattern.search(input_dir_path.stem)
        lattice_constant = float(m.group(0)) / 100
        volume = lattice_constant**3
        volumes.append(volume)

        logging.info(f"     lattice constant (ang): {lattice_constant}")
        logging.info(f"     volume (ang^3)        : {volume}")

        vasprun_xml_json_path = input_dir_path / "vasprun_xml.json"
        if vasprun_xml_json_path.exists():
            with vasprun_xml_json_path.open("r") as f:
                vasprun_dict = json.load(f)
        else:
            vasprun_xml_path = input_dir_path / "vasprun.xml"
            vasprun = Vasprun(str(vasprun_xml_path), parse_potcar_file=False)
            vasprun_dict = vasprun.as_dict()
            with vasprun_xml_json_path.open("w") as f:
                json.dump(vasprun_dict, f, indent=4)
        energy = vasprun_dict["output"]["final_energy"]
        energies.append(energy)

        logging.info(f"     energy (eV)           : {energy}")

    eos = EOS(eos_name=eos_name).fit(volumes, energies)
    calc_info_dict["e0"] = eos.e0
    calc_info_dict["v0"] = eos.v0
    calc_info_dict["a0"] = eos.v0 ** (1 / 3)
    calc_info_dict["b0"] = eos.b0_GPa

    outputs_dir_path = Path("data/outputs")
    existing_dir_path_list = [
        dir_path for dir_path in outputs_dir_path.glob("[0-9][0-9][0-9]")
    ]
    dump_dir_path = outputs_dir_path / str(len(existing_dir_path_list) + 1).zfill(3)
    dump_dir_path.mkdir(parents=True)

    logging.info("Dumping eos_analysis.json")

    eos_analysis_json_path = dump_dir_path / "eos_analysis.json"
    with eos_analysis_json_path.open("w") as f:
        json.dump(calc_info_dict, f, indent=4)

    logging.info("Dumping eos.png")

    plt = eos.plot()
    plt.savefig(dump_dir_path / "eos.png")
