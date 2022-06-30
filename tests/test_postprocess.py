import pytest

from eos_tools.postprocess import parse_volume_and_energy


def test_parse_volume_and_energy(inputs_dir_path):
    vasp_dir_path = inputs_dir_path / "ismear_1" / "new_potcar" / "1" / "fccFe_704"
    volume, energy = parse_volume_and_energy(vasp_dir_path)

    expected_volume = 348.913664
    expected_energy = -259.37161

    assert volume == expected_volume
    assert energy == pytest.approx(expected_energy, 1e-5)
