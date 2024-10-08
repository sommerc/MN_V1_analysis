#!/bin/bash

#SBATCH --job-name=frog_analysis
#SBATCH --output=logs/%A_%a.out

#SBATCH --time=10:00:00
#SBATCH --mem=180G
#SBATCH --array=0-5 

#SBATCH --ntasks=1
#SBATCH --mail-user=christoph.sommer@ist.ac.at
#SBATCH --mail-type=ALL
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --no-requeue
#SBATCH --export=TQDM_DISABLE=1

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

ANALYSIS_TYPES=(F L P AE AC AR)
SETTINGS_YAML=$1

RUN_TYPE="${ANALYSIS_TYPES[${SLURM_ARRAY_TASK_ID}]}"

echo RUN $RUN_TYPE
echo srun --cpu_bind=verbose python ../analysis/analysis_cluster.py -t $RUN_TYPE -s $SETTINGS_YAML 
echo ---------------------------------------------------------------------------------------------
echo
srun --cpu_bind=verbose python ../analysis/analysis_cluster.py -t $RUN_TYPE -s $SETTINGS_YAML 
 








