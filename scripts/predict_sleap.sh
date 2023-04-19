#!/bin/bash

#SBATCH --job-name=slp_37
#SBATCH --output=logs/%j_%a.out

#SBATCH --array=0-0
#SBATCH --time=10:00:00
#SBATCH --mem=128G

#SBATCH --ntasks=1
#SBATCH --mail-user=christoph.sommer@ist.ac.at
#SBATCH --mail-type=ALL
#SBATCH --no-requeue
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --export=NONE

unset SLURM_EXPORT_ENV
export OMP_NUM_THREADS=1

# get conda ready
source /nfs/scistore08/imagegrp/csommer/.bashrc
conda activate sleap
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/

# print cluster node
echo Cluster node:
hostname
echo


if [ -z "$1" ]
  then
	echo "No MOVIE_ROOT_DIR supplied"
	exit 1
fi

if [ -z "$2" ]
  then
	echo "No centroid model supplied"
	exit 1
fi

if [ -z "$3" ]
  then
	echo "No instance model supplied"
	exit 1
fi

if [ -z "$4" ]
  then
	echo "No target instance count (e.g. 1 or 11) specified"
	exit 1
fi

if [ -z "$5" ]
  then
	echo "No overwrite flag set, choose true for overwriting existing files, false for skipping. Default is false"
	OVERWRITE=false 
  else
    if [ "$5" = true ]; then                                                                                                                                                        │
	  OVERWRITE=true                                                                                                                                                                  │
	else                                                                                                                                                                            │
	  OVERWRITE=false                                                                                                                                                                 │
	fi
fi

MOVIE_ROOT_DIR=$1
MODEL_1=$2
MODEL_2=$3
MAX_N_ANIMALS=$4

# enable recursive glob
shopt -s globstar nullglob
FILES=("$MOVIE_ROOT_DIR"/**/*.mp4)

echo  - Found "${#FILES[@]}" movies in $MOVIE_ROOT_DIR

input_mp4="${FILES[${SLURM_ARRAY_TASK_ID}]}"
output_slp="${input_mp4}.predictions.slp"
output_h5="${input_mp4}.predictions.analysis.h5"

echo  - Processing array ID ${SLURM_ARRAY_TASK_ID}	
echo  - File: $input_mp4 
echo  - Output: $output_slp
echo  - Centroid Model: $MODEL_1
echo  - Instance Model: $MODEL_2


if [ -f "$output_h5" ] && ["$OVERWRITE" = false]
  then
	echo "Output h5 file already present, and overwrite is false skipping"
	exit 0
fi


#################################################################################
#################################################################################
#Example
# Run on two movies in the 'incoming' folder
# sbatch --array=0-1 --time=5:00:00 predict_sleap.sh "/nfs/scistore14/sweengrp/zharring/paper_videos/Juv/incoming/" /nfs/scistore14/sweengrp/zharring/paper_videos/Juv/models/230208.centroid.n\=405/ /nfs/scistore14/sweengrp/zharring/paper_videos/Juv/models/230302.centered_instance.n\=410/ 1

srun --cpu_bind=verbose sleap-track "$input_mp4" -m "$MODEL_1" -m "$MODEL_2" -o "$output_slp" --tracking.tracker simple --tracking.match greedy --tracking.similarity centroid --tracking.target_instance_count "$MAX_N_ANIMALS" --tracking.pre_cull_to_target 1  --tracking.post_connect_single_breaks 1 --tracking.clean_instance_count "$MAX_N_ANIMALS" --verbosity rich --batch_size 8 

srun --cpu_bind=verbose sleap-convert "$output_slp" --format analysis -o "$output_h5" 








