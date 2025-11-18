#the out most directory
outer_dir="target_annotation/"
#list_allele_name="TCRV TCRJ BCRV BCRJ TCRD_plusHep BCRD_plusHep"
list_allele_name="BCRV BCRJ BCRD_plusHep"
allele_dir="./example/material/"
allele_suffix="_alleles_parsed.fasta"
flag_annotate=$true

#person_name="HG002"
#asm_path_H1="../../asm/NA24385/HG002-H1.fa"
#asm_path_H2="../../asm/NA24385/HG002-H2.fa"

#person_name="HG002-part"
#asm_path_H1="./example/samples/HG002-S22-H1-000000F_1900000-2900000.fasta"

#person_name="grch37"
#asm_path_H1_index="/home/mlin77/data_blangme2/fasta/grch37/bwa/hg19.fa"
#asm_path_H1="/home/mlin77/data_blangme2/fasta/grch37/hg19.fa"

#person_name="HG002"
#asm_path_H1_index="/home/mlin77/data_blangme2/fasta/hg002/bwa/NA24385.HiFi.hifiasm-0.12.hap1.fa"
#asm_path_H1="/home/mlin77/data_blangme2/fasta/hg002/NA24385.HiFi.hifiasm-0.12.hap1.fa"
#asm_path_H2_index="/home/mlin77/data_blangme2/fasta/hg002/bwa2/NA24385.HiFi.hifiasm-0.12.hap2.fa"
#asm_path_H2="/home/mlin77/data_blangme2/fasta/hg002/NA24385.HiFi.hifiasm-0.12.hap2.fa"

person_name="HG002-denovo"
asm_path_H1="/home/mlin77/data_blangme2/fasta/hg001/NA24385-denovo-H1.fa"
asm_path_H1_index="/home/mlin77/data_blangme2/fasta/hg001/bwa/NA24385-denovo-H1.fa"
asm_path_H2="/home/mlin77/data_blangme2/fasta/hg001/NA24385-denovo-H2.fa"
asm_path_H2_index="/home/mlin77/data_blangme2/fasta/hg001/bwa/NA24385-denovo-H2.fa"

person_name="HG00733"
asm_path_H1="/home/mlin77/data_blangme2/fasta/hg00733/HG00733.HiFi.hifiasm-0.12.hap1.fa"
asm_path_H1_index="/home/mlin77/data_blangme2/fasta/hg00733/bwa/HG00733.HiFi.hifiasm-0.12.hap1.fa"
asm_path_H2="/home/mlin77/data_blangme2/fasta/hg00733/HG00733.HiFi.hifiasm-0.12.hap2.fa"
asm_path_H2_index="/home/mlin77/data_blangme2/fasta/hg00733/bwa/HG00733.HiFi.hifiasm-0.12.hap2.fa"

person_name="HG002-curated"
asm_path_H1="/home/mlin77/data_blangme2/fasta/hprc-yr1/curated/ncbi-genomes-2022-10-24/GCA_021950905.1_HG002.pat.cur.20211005_genomic.fna"
asm_path_H1_index=${asm_path_H1}.gz
asm_path_H2="/home/mlin77/data_blangme2/fasta/hprc-yr1/curated/ncbi-genomes-2022-10-24/GCA_021951015.1_HG002.mat.cur.20211005_genomic.fna"
asm_path_H2_index=${asm_path_H2}.gz

outer_dir="AIRRsembly/"
person_name="HG002-10k-IGK"
asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/extract_bam/HG002.10kb.IGK.fasta"
asm_path_H1_index=${asm_path_H1}

outer_dir="hprc_annotation"
person_name="T2T-HG002"
asm_path_H1="/home/mlin77/data_blangme2/fasta/hg002/assembly.v0.7.fasta"
asm_path_H1_index=${asm_path_H1}

outer_dir="AIRRsembly/"
person_name="HG03486-IGH"
asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/extract_unmapped_bam/HG03486.hprc.IGH.fasta"
asm_path_H1_index=${asm_path_H1}

outer_dir="AIRRsembly/"
person_name="HG03492-IGH-depleted-spades-asm"
asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/depleted_fasta/HG03492_hifiasm/HG03492.IGH.boost.asm.p_ctg.fa"
asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/depleted_fasta/HG03492_hifiasm/HG03492.IGH.spade/contigs.fasta"
asm_path_H1_index=${asm_path_H1}

outer_dir="AIRRsembly/"
person_name="HG01258_unique"
asm_path_H1='/scratch4/blangme2/maojan/AIRRssembly/recombine_results/bad_reference.fasta'
asm_path_H1="/scratch4/blangme2/maojan/AIRRssembly/HG01258_unique/grch37.HG01258.unique.fa"
asm_path_H1_index=${asm_path_H1}

outer_dir="AIRRsembly/"
#person_name="HG01978-IGH-depleted-asm"
#person_name="HG01258-IGH-with-ONT-asm"
#person_name="HG002-hprc-IGH"
person_name="HG02886-IGH-depleted-asm-trio"
#asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/depleted_fasta/HG01978_hifiasm/HG01978.IGH.asm.p_ctg.fa"
#asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/assembly_with_nanopore/HG01258_hifiasm/HG01258.IGH.asm.bp.hap1.fa"
#asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/extract_assembly/HG002_hifiasm/HG002.IGH.asm.bp.hap1.fa"
#asm_path_H1_index=${asm_path_H1}
#asm_path_H2="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/assembly_with_nanopore/HG01258_hifiasm/HG01258.IGH.asm.bp.hap2.fa"
#asm_path_H2="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/extract_assembly/HG002_hifiasm/HG002.IGH.asm.bp.hap2.fa"
#asm_path_H2_index=${asm_path_H2}
asm_path_H1="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/parent_data/HG02886/HG02886.IGH.asm.hap1.fa"
asm_path_H1_index=${asm_path_H1}
asm_path_H2="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/parent_data/HG02886/HG02886.IGH.asm.hap2.fa"
asm_path_H2_index=${asm_path_H2}


#outer_dir="target_annotation/"
#list_allele_name="BCRV BCRJ BCRD_plusHep"
#allele_dir="./example/material/"
#allele_suffix="_alleles_parsed.fasta"
#person_name="HG001-test"
#asm_path_H1="/home/mlin77/data_blangme2/fasta/hg001/NA12878-denovo-H1.fa"
#asm_path_H1_index="/home/mlin77/data_blangme2/fasta/hg001/bwa/NA12878-denovo-H1.fa"
#asm_path_H2="/home/mlin77/data_blangme2/fasta/hg001/NA12878-denovo-H2.fa"
#asm_path_H2_index="/home/mlin77/data_blangme2/fasta/hg001/bwa/NA12878-denovo-H2.fa"


# setting for the data
echo "[AIRRAnnotate] Indexing assembly..."
#bwa index ${asm_path_H1}
#bwa index ${asm_path_H2}
if [ ! -f "${asm_path_H1_index}.bwt" ]; then 
    bwa index ${asm_path_H1} -p ${asm_path_H1_index}
fi
if [ ! -f "${asm_path_H2_index}.bwt" ]; then 
    bwa index ${asm_path_H2} -p ${asm_path_H2_index}
fi

mkdir -p ${outer_dir}
mkdir -p ${outer_dir}/${person_name}
for allele_name in ${list_allele_name}; do
    echo "[AIRRAnnotate] Align IMGT ${allele_name} alleles to assembly..."
    if [ ${allele_name} == "TCRD_plusHep" ] || [ ${allele_name} == "BCRD_plusHep" ]; then
        echo "[AIRRAnnotate] Adjust BWA parameters for shorter alleles..."
        bwa mem -t 16 -a -T 10 ${asm_path_H1_index} ${allele_dir}${allele_name}${allele_suffix} > ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H1.sam
        bwa mem -t 16 -a -T 10 ${asm_path_H2_index} ${allele_dir}${allele_name}${allele_suffix} > ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H2.sam
    else
        bwa mem -t 16 -a ${asm_path_H1_index} ${allele_dir}${allele_name}${allele_suffix} > ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H1.sam
        bwa mem -t 16 -a ${asm_path_H2_index} ${allele_dir}${allele_name}${allele_suffix} > ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H2.sam
    fi


    echo "[AIRRAnnotate] Parse the ${allele_name} alleles sam files to annotation report..."
    python3 scripts/annotation_with_asm.py -foa   ${outer_dir}/${person_name}/annotation_${person_name}_${allele_name}.txt \
                                           -foma  ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_${allele_name}.txt \
                                           -fom   ${outer_dir}/${person_name}/novel_${person_name}_${allele_name}.fasta \
                                           -fof   ${outer_dir}/${person_name}/flanking_${person_name}_${allele_name}.fasta \
                                           -fos   ${outer_dir}/${person_name}/summary_${person_name}_${allele_name}.rpt \
                                           -ext   200 \
                                           -fs1   ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H1.sam \
                                           -fp1   ${outer_dir}/${person_name}/dict_${person_name}_asm_H1.pickle \
                                           -fasm1 ${asm_path_H1} \
                                           -fs2   ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H2.sam \
                                           -fp2   ${outer_dir}/${person_name}/dict_${person_name}_asm_H2.pickle \
                                           -fasm2 ${asm_path_H2}
done
if ${flag_annotate}; then
    python3 scripts/analysis/bed_generator.py -rl \
        ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRV.txt \
        ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRJ.txt \
        ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRD_plusHep.txt \
        -o ${outer_dir}/${person_name}/group_genes
    python3 scripts/analysis/collect_gene_from_bed.py \
        -b1 ${outer_dir}/${person_name}/group_genes.1.bed \
        -b2 ${outer_dir}/${person_name}/group_genes.2.bed \
        -fl ${allele_dir}/IGH_functional.txt \
        > ${outer_dir}/${person_name}/IGH_functional.rpt
    echo "[ANNOTATION WITH ASM] ${person_name} Finished!"
fi
echo "[ANNOTATION WITH ASM] Finished!"
