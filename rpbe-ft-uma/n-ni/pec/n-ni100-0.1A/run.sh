#!/bin/bash
#SBATCH --partition=SP2
#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --ntasks-per-node=20
#SBATCH --cpus-per-task=1
#SBATCH -J n-ni-0.1
#SBATCH --time=192:00:00
#SBATCH --mem=120G

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

echo "Job ID: $SLURM_JOB_ID"
echo "Submit dir: $SLURM_SUBMIT_DIR"
echo "Node list: $SLURM_JOB_NODELIST"
echo "Ntasks: $SLURM_NTASKS"

module purge
module load qe/7.4.1-gnu

echo "pw.x: $(which pw.x)"
echo "mpirun: $(which mpirun)"
mpirun --version

mpirun -n "$SLURM_NTASKS" \
       -hosts "$SLURM_JOB_NODELIST" \
       pw.x -in n-ni100-0.1A.in > n-ni100-0.1A.out
