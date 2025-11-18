workspace="target_call"
path_SPAdes="spades.py"
list_allele_name="TCRJ TCRV BCRV BCRJ"
#list_allele_name="BCRJ"
allele_dir="./example/material/"
allele_suffix="_alleles_parsed.fasta"
person_name="HG002-part"
read_path_1="./example/samples/HG002_part_gAIRR-seq_R1.fastq.gz"
read_path_2="./example/samples/HG002_part_gAIRR-seq_R2.fastq.gz"

#list_allele_name="TCRJ TCRD_plusHep BCRD_plusHep"
#person_name="PL_B_0225"
#read_path_1="experiment/PL_S12_L001_R1_001.fastq.gz"
#read_path_2="experiment/PL_S12_L001_R2_001.fastq.gz"

list_allele_name="TCRV BCRV BCRJ"
person_name="HG001-test"
read_path_1="experiment/NA12878_S46_L001_R1_001.fastq.gz"
read_path_2="experiment/NA12878_S46_L001_R2_001.fastq.gz"

#person_name="HG002"
#read_path_1="experiment/GM24385_S42_L001_R1_001.fastq.gz"
#read_path_2="experiment/GM24385_S42_L001_R2_001.fastq.gz"

#person_name="HG003"
#read_path_1="experiment/GM24149_S41_L001_R1_001.fastq.gz"
#read_path_2="experiment/GM24149_S41_L001_R2_001.fastq.gz"

#person_name="HG004"
#read_path_1="experiment/GM24143_S40_L001_R1_001.fastq.gz"
#read_path_2="experiment/GM24143_S40_L001_R2_001.fastq.gz"

#person_name="HG005"
#read_path_1="experiment/GM24631_S43_L001_R1_001.fastq.gz"
#read_path_2="experiment/GM24631_S43_L001_R2_001.fastq.gz"

#person_name="HG006"
#read_path_1="experiment/GM24694_S44_L001_R1_001.fastq.gz"
#read_path_2="experiment/GM24694_S44_L001_R2_001.fastq.gz"

#person_name="HG007"
#read_path_1="experiment/GM24695_S45_L001_R1_001.fastq.gz"
#read_path_2="experiment/GM24695_S45_L001_R2_001.fastq.gz"

#person_name="PL-B"
#read_path_1="experiment/PL-B_S1_L001_R1_001.fastq.gz"
#read_path_2="experiment/PL-B_S1_L001_R2_001.fastq.gz"

#person_name="PL-S"
#read_path_1="experiment/PL-S_S2_L001_R1_001.fastq.gz"
#read_path_2="experiment/PL-S_S2_L001_R2_001.fastq.gz"

#person_name="HG002-novaseq-30x"
#read_path_1="/home/mlin77/data_blangme2/reads/HG002.novaseq.pcr-free.30x.R1.fq.gz"
#read_path_2="/home/mlin77/data_blangme2/reads/HG002.novaseq.pcr-free.30x.R2.fq.gz"

#person_name="Insertion_test"
#read_path_1="/home/mlin77/scr4_blangme2/maojan/gAIRRsuite/novel_insertion_test/Test_merge.1.fq"
#read_path_2="/home/mlin77/scr4_blangme2/maojan/gAIRRsuite/novel_insertion_test/Test_merge.2.fq"

# environment settings
mkdir -p ${workspace}
mkdir -p ${workspace}/${person_name}

# call novel alleles
for allele_name in ${list_allele_name}; do
    allele_path=${allele_dir}${allele_name}${allele_suffix}
    echo "[AIRRCall] ${person_name} ${allele_name} novel allele calling..."
    ./scripts/novel_allele.sh ${workspace}/${person_name} ${allele_name} ${allele_path} ${person_name} ${read_path_1} ${read_path_2}
    
    allele_path=${workspace}/${person_name}/${person_name}_${allele_name}_novel/${allele_name}_with_novel.fasta
    echo "[AIRRCall] ${person_name} ${allele_name} allele calling..."
    ./scripts/allele_calling.sh ${workspace}/${person_name} ${allele_name} ${allele_path} ${person_name} ${read_path_1} ${read_path_2}
    
    #echo "[AIRRCall] ${person_name} ${allele_name} flanking sequence calling..."
    #./scripts/flanking_sequence.sh ${workspace}/${person_name} ${allele_name} ${allele_path} ${person_name} ${read_path_1} ${read_path_2} ${path_SPAdes}
done

#for allele_name in ${list_allele_name}; do
#    allele_path=${workspace}/${person_name}/${person_name}_${allele_name}_novel/${allele_name}_with_novel.fasta
#    
#    echo "[AIRRCall] ${person_name} ${allele_name} flanking sequence calling..."
#    ./scripts/flanking_sequence.sh ${workspace}/${person_name} ${allele_name} ${allele_path} ${person_name} ${read_path_1} ${read_path_2} ${path_SPAdes}
#done
