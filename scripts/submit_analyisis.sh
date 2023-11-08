#!/bin/bash

#SBATCH --job-name=frog_analysis
#SBATCH --output=logs/%j.out

#SBATCH --time=3:00:00
#SBATCH --mem=240G

#SBATCH --ntasks=6
#SBATCH --mail-user=christoph.sommer@ist.ac.at
#SBATCH --mail-type=ALL
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --no-requeue
#SBATCH --export=NONE

unset SLURM_EXPORT_ENV
export OMP_NUM_THREADS=1

# get conda ready
source ~/.bashrc
conda activate frog_analysis
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/

# print cluster node
echo Cluster node:
hostname
echo


if [ -z "$1" ]
  then
	echo "No settings yaml supplied supplied"
	exit 1
fi


SETTINGS_YAML=$1

srun --cpu_bind=verbose --ntasks=1 --mem-per-cpu=40 python ../analysis/analysis_cluster.py -t L -s $SETTINGS_YAML &
srun --cpu_bind=verbose --ntasks=1 --mem-per-cpu=40 python ../analysis/analysis_cluster.py -t F -s $SETTINGS_YAML &
srun --cpu_bind=verbose --ntasks=1 --mem-per-cpu=40 python ../analysis/analysis_cluster.py -t P -s $SETTINGS_YAML &
srun --cpu_bind=verbose --ntasks=1 --mem-per-cpu=40 python ../analysis/analysis_cluster.py -t AE -s $SETTINGS_YAML &
srun --cpu_bind=verbose --ntasks=1 --mem-per-cpu=40 python ../analysis/analysis_cluster.py -t AC -s $SETTINGS_YAML &
srun --cpu_bind=verbose --ntasks=1 --mem-per-cpu=40 python ../analysis/analysis_cluster.py -t AR -s $SETTINGS_YAML &
wait
 








