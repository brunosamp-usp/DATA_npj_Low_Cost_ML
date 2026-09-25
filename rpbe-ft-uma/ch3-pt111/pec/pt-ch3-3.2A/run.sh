#!/bin/bash
#SBATCH --partition=SP2
#SBATCH --ntasks=20              # number of tasks / mpi processes
#SBATCH --cpus-per-task=1       # Number OpenMP Threads per process
#SBATCH --ntasks-per-node=20
#SBATCH -J pt-ch3-3.2A
#SBATCH --time=192:00:00         # Se voce nao especificar, o default é 8 horas. O limite é 192
#SBATCH --mem-per-cpu=24042

# OpenMP settings:
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

echo $SLURM_JOB_ID
echo $SLURM_SUBMIT_DIR
echo $SLURM_JOB_NODELIST
echo $SLURM_NTASKS

module purge
module load qe/7.4.1-gnu

mpirun -n $SLURM_NTASKS pw.x -in  pt-ch3-3.2A.in > pt-ch3-3.2A.out 


