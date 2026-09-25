#!/usr/bin/env python3

import re
from pathlib import Path

from ase.io import read, write
from ase.calculators.singlepoint import SinglePointCalculator
from fairchem.core import pretrained_mlip, FAIRChemCalculator


# ==========================================
# CONFIGURAÇÕES
# ==========================================

BASE_DIR = Path(".")
MODEL_NAME = "uma-s-1p1"
TASK_NAME = "oc20"


# ==========================================
# CARREGA UMA UMA VEZ SÓ
# ==========================================

print("Carregando UMA-s-1p1...")

predictor = pretrained_mlip.get_predict_unit(MODEL_NAME)

calc = FAIRChemCalculator(
    predictor,
    task_name=TASK_NAME,
)

print("Modelo carregado.")
print()


def get_distance(folder_name):
    m = re.match(r"^pt-ch3-(\d+(?:\.\d+)?)A$", folder_name)
    if m:
        return float(m.group(1))
    return None


def process_traj(qe_traj: Path, uma_traj: Path):
    frames = read(qe_traj, ":")

    if not isinstance(frames, list):
        frames = [frames]

    print(f"Frames encontrados: {len(frames)}")

    out_frames = []

    for i, atoms in enumerate(frames):
        atoms_uma = atoms.copy()

        atoms_uma.set_cell(atoms.cell.copy())
        atoms_uma.set_pbc(atoms.pbc.copy())

        atoms_uma.calc = calc

        energy = atoms_uma.get_potential_energy()
        forces = atoms_uma.get_forces()

        atoms_out = atoms.copy()

        atoms_out.calc = SinglePointCalculator(
            atoms_out,
            energy=energy,
            forces=forces,
        )

        out_frames.append(atoms_out)

        print(f"  Frame {i:4d} | E_UMA = {energy:14.8f} eV")

    write(uma_traj, out_frames)


def main():
    folders = sorted(
        [
            p for p in BASE_DIR.iterdir()
            if p.is_dir() and get_distance(p.name) is not None
        ],
        key=lambda p: get_distance(p.name),
    )

    print(f"Pastas pt-ch3-*A encontradas: {len(folders)}")
    print()

    for folder in folders:
        dist = get_distance(folder.name)
        dist_str = f"{dist:.1f}"

        qe_traj = folder / f"pt-ch3-{dist_str}A-qe.traj"
        uma_traj = folder / f"pt-ch3-{dist_str}A-uma.traj"

        print("=" * 70)
        print(f"Pasta: {folder.name}")
        print(f"QE traj:  {qe_traj}")
        print(f"UMA traj: {uma_traj}")

        if not qe_traj.exists():
            print(f"[AVISO] Não encontrei {qe_traj.name}. Pulando.")
            continue

        try:
            process_traj(qe_traj, uma_traj)
            print(f"Salvo: {uma_traj}")

        except Exception as e:
            print(f"[ERRO] Falhou em {folder.name}: {e}")

    print()
    print("Finalizado.")


if __name__ == "__main__":
    main()
