#!/usr/bin/env bash

source $(conda info --json | awk '/conda_prefix/ { gsub(/"|,/, "", $2); print $2 }')/bin/activate /appdev/aerijman/.local/share/mamba/envs/bwa
source /appdev/aerijman/projects/artifacts/base_quality_recalibration/tasmanian-mismatch/tasmanian_env/bin/activate

if [ ${#} -lt 1 ]; then echo -e "./run_simulations.sh <\033[1mparameters_file.info\033[0m>"; exit; fi

parameters_file=$1
prefix=$(cat $parameters_file | grep prefix | awk '{print $2}')


simulations_folder=${prefix}_simulations
mkdir -p ${simulations_folder}
cp ${parameters_file} ${simulations_folder}
cp variants_proposed.tsv ${simulations_folder}

cd ${simulations_folder}
python ../generate_reference_and_reads.py ${parameters_file}
genome_fa=$(realpath *fa) 
bwa index ${genome_fa}

bwa mem -t4 ${genome_fa} simulated_reads_R1.fastq simulated_reads_R2.fastq > aligned.sam
samtools sort --write-index aligned.sam -o aligned_sorted.bam
samtools view aligned_sorted.bam | awk '{arr[$2]++}END{for (i in arr) {print i"\t"arr[i]} }'
samtools view aligned_sorted.bam | run_tasmanian -r ${genome_fa} > aligned_sorted_tasmanianed.csv
