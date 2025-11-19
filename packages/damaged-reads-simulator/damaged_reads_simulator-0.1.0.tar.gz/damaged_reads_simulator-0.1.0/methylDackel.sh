# ba

in1=$1
in2=$2
prefix=$3 #$(echo $1 | sed 's/.fastq//')
genome=$4

rg="@RG\tID:NB552.1\\tSM:XH_10ng_R2\\tLB:XH_10ng_R2\\tBC:GAACTGCC-GGCTGGGA\\tPL:ILLUMINA\\tPU:NB552064:NB552064:HM7KFBGYX.1.GAACTGCC-GGCTGGGA\\tCN:New_England_Biolabs"



bwameth.py -p -t 1 \
    --read-group "@RG\tID:NB552.1\tBC:GAACTGCC-GGCTGGGA\tPL:ILLUMINA" \
    --reference ${genome} $in1 $in2 \
    2> "${prefix}.log.bwamem" 1> ${prefix}.aln.sam


#cat ${prefix}.aln.sam | sed "s/@RG.*/$rg/" \
#    | sed 's/\t97/\t99/' \
#    | sed 's/\t145/\t147/' \
#    | sed 's/\t81/\t83/' \
#    | sed 's/\t161/\t163/' \
#    | samtools view -hb | samtools sort -o ${prefix}.aln.bam

cat ${prefix}.aln.sam | sed "s/@RG.*/$rg/" | samtools view -hb | samtools sort -write-index -o ${prefix}.aln.bam 
# samtools index ${prefix}.aln.bam


MethylDackel extract --methylKit -q 0 -@1 --CHH --CHG -o dackelextract.${prefix} ${genome} ${prefix}.aln.bam
