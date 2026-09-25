#!/bin/bash
#SBATCH --partition=SP2
#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --ntasks-per-node=20
#SBATCH --cpus-per-task=1
#SBATCH -J pt-h-pec
#SBATCH --time=08-00:00:00
#SBATCH --mem=100G
#SBATCH --output=slurm-%j.out

module purge

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

export PATH=/temporario2/apps/gnu/mpich-4.2.0/bin:/temporario2/apps/gnu/qe-7.4.1/bin:/usr/bin:/bin

export LD_LIBRARY_PATH=/temporario2/apps/gnu/mpich-4.2.0/lib:/temporario2/apps/gnu/qe-7.4.1/lib:/opt/ohpc/pub/compiler/gcc/8.3.0/lib64

echo "mpirun:"
which mpirun
mpirun --version

echo "pw.x:"
which pw.x
pw.x -version

echo "libs:"
ldd $(which pw.x) | grep -i mpi

mkdir -p output

mpirun -np $SLURM_NTASKS pw.x -in pt-h-6.in > pt-h-6out
