#!/usr/bin/env python3
import re
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.io import write
from ase.calculators.singlepoint import SinglePointCalculator

BASE_DIR = Path(".")

RY_TO_EV = 13.605693122994
BOHR_TO_ANG = 0.529177210903
FORCE_CONV = RY_TO_EV / BOHR_TO_ANG


def get_distance(folder_name):
    m = re.match(r"^pt-ch3-(\d+(?:\.\d+)?)A$", folder_name)
    if m:
        return float(m.group(1))
    return None


def read_nat_from_file(path):
    text = path.read_text(errors="ignore")

    m = re.search(r"\bnat\s*=\s*(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    m = re.search(r"number of atoms/cell\s*=\s*(\d+)", text)
    if m:
        return int(m.group(1))

    raise RuntimeError(f"Não consegui ler nat em {path}")


def read_qe_input(in_file):
    lines = in_file.read_text(errors="ignore").splitlines()

    nat = read_nat_from_file(in_file)

    cell = []
    symbols = []
    positions = []

    for i, line in enumerate(lines):
        if line.strip().upper().startswith("CELL_PARAMETERS"):
            unit = line.lower()

            for k in range(1, 4):
                vals = [float(x) for x in lines[i + k].split()[:3]]
                cell.append(vals)

            cell = np.array(cell)

            if "bohr" in unit:
                cell *= BOHR_TO_ANG
            elif "angstrom" in unit:
                pass
            elif "alat" in unit:
                raise RuntimeError("CELL_PARAMETERS alat ainda não implementado.")

            break

    for i, line in enumerate(lines):
        if line.strip().upper().startswith("ATOMIC_POSITIONS"):
            unit = line.lower()

            for k in range(1, nat + 1):
                tok = lines[i + k].split()
                symbols.append(tok[0])
                positions.append([
                    float(tok[1]),
                    float(tok[2]),
                    float(tok[3]),
                ])

            positions = np.array(positions)

            if "bohr" in unit:
                positions *= BOHR_TO_ANG
            elif "angstrom" in unit:
                pass
            elif "crystal" in unit:
                positions = positions @ cell

            break

    if len(cell) != 3:
        raise RuntimeError("Não encontrei CELL_PARAMETERS no .in")

    if len(symbols) != nat:
        raise RuntimeError(
            f"Não encontrei ATOMIC_POSITIONS completo no .in: {len(symbols)}/{nat}"
        )

    return nat, symbols, positions, cell


def read_qe_output(out_file, nat):
    lines = out_file.read_text(errors="ignore").splitlines()

    energy = None
    forces = []

    for line in lines:
        if "!    total energy" in line:
            energy_ry = float(line.split()[-2])
            energy = energy_ry * RY_TO_EV

    i = 0
    while i < len(lines):
        if "Forces acting on atoms" in lines[i]:
            forces = []
            j = i + 1

            while j < len(lines) and len(forces) < nat:
                if "force =" in lines[j]:
                    vals = lines[j].split()[-3:]
                    forces.append([float(v) * FORCE_CONV for v in vals])
                j += 1

            break

        i += 1

    if energy is None:
        raise RuntimeError("Não encontrei energia total no .out")

    if len(forces) != nat:
        raise RuntimeError(f"Não encontrei forças completas no .out: {len(forces)}/{nat}")

    return energy, np.array(forces)


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

        in_file = folder / f"pt-ch3-{dist_str}A.in"
        out_file = folder / f"pt-ch3-{dist_str}A.out"
        out_traj = folder / f"pt-ch3-{dist_str}A-qe.traj"

        print("=" * 70)
        print(f"Pasta: {folder.name}")
        print(f"IN:    {in_file.name}")
        print(f"OUT:   {out_file.name}")
        print(f"TRAJ:  {out_traj.name}")

        if not in_file.exists():
            print(f"[AVISO] Não encontrei {in_file}")
            continue

        if not out_file.exists():
            print(f"[AVISO] Não encontrei {out_file}")
            continue

        try:
            nat, symbols, positions, cell = read_qe_input(in_file)
            energy, forces = read_qe_output(out_file, nat)

            atoms = Atoms(
                symbols=symbols,
                positions=positions,
                cell=cell,
                pbc=[True, True, True],
            )

            atoms.calc = SinglePointCalculator(
                atoms,
                energy=energy,
                forces=forces,
            )

            write(out_traj, atoms)

            print(f"N átomos: {nat}")
            print(f"Salvo: {out_traj}")
            print(f"Energia QE: {energy:.10f} eV")

        except Exception as e:
            print(f"[ERRO] {folder.name}: {e}")

    print()
    print("Finalizado.")


if __name__ == "__main__":
    main()
