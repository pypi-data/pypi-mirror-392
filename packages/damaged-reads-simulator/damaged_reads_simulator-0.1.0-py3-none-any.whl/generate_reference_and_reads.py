import sys, os
sys.path.append(os.path.realpath("./"))
from sys import stderr, argv
import os
import re
import argparse
from libs.simulations_libs import *
import numpy as np


def read_parameters_file(parameters_info_file):

    with open(parameters_info_file, 'r') as f:
        specifications = [i.strip().split(":") for i in f if i[0] != "#" and len(i) > 2]

    GC_pct = contig_lengths = n_reads = read_length = insert_length = insert_length_var = None
    library_type = methylated_genome = pct_methylation = None

    for key, value in specifications:
        value = value.strip()
        match key:
            case 'generate reference':          make_reference = True
            case 'reference file path':         reference_fasta_path = value
            case 'GC percentage':               GC_pct = int(value)
            case 'length of contigs':           contig_lengths = np.array(value.split(",")).astype(int)
            case 'number of reads':             n_reads = int(value)
            case 'read_length':                 read_length = int(value)
            case 'insert length':               insert_length = int(value)
            case 'insert length variations':    insert_length_var = int(value)
            case 'type of library':             library_type = value
            case 'methylation library':         methylated_genome = bool(value.lower() == 'true');
            case 'percent methylation':         pct_methylation = float(value)
            case 'random seed':                 random_seed = int(value)
            case 'prefix':                      prefix = value
            case _: print(f"Unknown parameter: {key}")

    return (make_reference, reference_fasta_path, GC_pct, contig_lengths, n_reads, read_length, insert_length, insert_length_var,
            library_type, methylated_genome, pct_methylation, random_seed, prefix)


def main():
    if len(argv) > 1:
        parameters_info_file = argv[1]
    else:
        parameters_info_file = "parameters.info"
        if not os.path.isfile(parameters_info_file):
            print(f"{parameters_info_file} not found. If you renamed it, add it as an argument: ./read_simulator parameters.file.info")
            sys.exit()

    (make_reference, reference_fasta_path, GC_pct, contig_lengths, n_reads, read_length, insert_length, insert_length_var,
     library_type, methylated_genome, pct_methylation, random_seed, prefix) = read_parameters_file(parameters_info_file=sys.argv[1] if len(sys.argv) > 1 else "parameters.info")

    abs_path = os.path.realpath(parameters_info_file)
    stderr.write(f"parameters_file = {abs_path}\n")

    simulations_folder = prefix + '_simulations'
    os.makedirs(simulations_folder, exist_ok=True)


    if make_reference:
        reference_file_path = 'simulated_reference_genome.fa'
        stderr.write(f"generating a new reference and saving it as {reference_file_path} \n")
        genome_dict = make_reference_genome(num_contigs=len(contig_lengths), GC_pct=GC_pct, contig_lengths=contig_lengths, seed=random_seed)

        # write to disk for reproducibility?
        g = '\n'.join( [">" + k + "\n" + v for k,v in genome_dict.items()] )
        with open(reference_file_path, 'w') as f:
            f.write( g )
    else:
        stderr.write(f"using {reference_fasta_path} as the reference\n")
        genome_dict = load_reference_genome(reference_fasta_path)

    # if libraries are bisulfite or EM-seq reads should contain conversions (r1:C->T & r2:G->A)
    if methylated_genome == True:
        stderr.write("genome is treated as methylated - bisulfite/emseq converted\n")
        genome_dict = make_reference_bisulfite(genome_dict, pct_methylation=pct_methylation, seed=random_seed)

    # Variants can be simulated into the genome
    variants_list = read_proposed_variants('variants_proposed.tsv')
    variants_dict = assign_contigs_to_variants(variants_list, genome_dict, seed=random_seed)

    # First generate reads where variants are allegedly present at the proper allele frequencies
    reads = generate_reads(
        genome_dict=genome_dict,
        variants_dict=variants_dict,
        read_length=read_length,
        n_reads=n_reads,
        insert_length=insert_length,
        insert_length_var=insert_length_var,
        seed=random_seed
    )

    # Generate the positional pattern (of damage) that simulated reads should contain
    probs = generate_probabilities(read_length=read_length, seed=random_seed, library_type='FFPE')

    # Include positional damage into the reads
    mutated_reads = mutate_reads(reads=reads, probabilities=probs, read_length=read_length)

    assert reads != mutated_reads, "HEY!!! reads and mutated reads are the same!!!"

    # Save reads containing variants and positional damage.
    reads_dict = print_reads(mutated_reads, seed=random_seed)
    stderr.write(f"fastq reads sved in simulation_folder \n")

    with open('simulated_reads_R1.fastq', 'w') as f:
        f.write(reads_dict[0])

    with open('simulated_reads_R2.fastq', 'w') as f:
        f.write(reads_dict[1])

if __name__ == "__main__":
    main()
