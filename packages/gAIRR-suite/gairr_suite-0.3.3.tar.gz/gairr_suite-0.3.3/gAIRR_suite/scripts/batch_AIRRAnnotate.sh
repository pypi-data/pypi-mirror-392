#person_name="CHM13Y"
#asm_path_H1_index="/home/mlin77/data_blangme2/fasta/hprc-yr1/bwa/CHM13Y.fa"
#asm_path_H1="/home/mlin77/data_blangme2/fasta/hprc-yr1/CHM13Y.fa"
#
#outer_dir="hprc_annotation"
##list_allele_name="TCRV TCRJ BCRV BCRJ TCRD_plusHep BCRD_plusHep"
#list_allele_name="BCRV BCRJ BCRD_plusHep"
#allele_dir="./example/material/"
#allele_suffix="_alleles_parsed.fasta"
#
#mkdir -p ${outer_dir}
#mkdir -p ${outer_dir}/${person_name}
#for allele_name in ${list_allele_name}; do
#    echo "[AIRRAnnotate] Align IMGT ${allele_name} alleles to assembly..."
#    if [ ${allele_name} == "TCRD_plusHep" ] || [ ${allele_name} == "BCRD_plusHep" ]; then
#        echo "[AIRRAnnotate] Adjust BWA parameters for shorter alleles..."
#        bwa mem -t 16 -a -T 10 ${asm_path_H1_index} ${allele_dir}${allele_name}${allele_suffix} > ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H1.sam
#    else
#        bwa mem -t 16 -a ${asm_path_H1_index} ${allele_dir}${allele_name}${allele_suffix} > ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H1.sam
#    fi
#
#
#    echo "[AIRRAnnotate] Parse the ${allele_name} alleles sam files to annotation report..."
#    python3 scripts/annotation_with_asm.py -foa   ${outer_dir}/${person_name}/annotation_${person_name}_${allele_name}.txt \
#                                           -foma  ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_${allele_name}.txt \
#                                           -fom   ${outer_dir}/${person_name}/novel_${person_name}_${allele_name}.fasta \
#                                           -fof   ${outer_dir}/${person_name}/flanking_${person_name}_${allele_name}.fasta \
#                                           -fos   ${outer_dir}/${person_name}/summary_${person_name}_${allele_name}.rpt \
#                                           -ext   200 \
#                                           -fs1   ${outer_dir}/${person_name}/bwa_${person_name}_${allele_name}_alleles_to_asm_H1.sam \
#                                           -fp1   ${outer_dir}/${person_name}/dict_${person_name}_asm_H1.pickle \
#                                           -fasm1 ${asm_path_H1}
#done
#python3 scripts/analysis/bed_generator.py -rl \
#    ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRV.txt \
#    ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRJ.txt \
#    ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRD_plusHep.txt \
#    -o ${outer_dir}/${person_name}/group_genes
#python3 scripts/analysis/collect_gene_from_bed.py \
#    -b1 ${outer_dir}/${person_name}/group_genes.1.bed \
#    -b2 ${outer_dir}/${person_name}/group_genes.2.bed \
#    -fl ${allele_dir}/IGH_functional.txt \
#    > ${outer_dir}/${person_name}/IGH_functional.rpt
#echo "[ANNOTATION WITH ASM] ${person_name} Finished!"



gairr_annotate() {
    outer_dir="hprc_annotation"
    list_allele_name="BCRV BCRJ BCRD_plusHep"
    allele_dir="./example/material/"
    allele_suffix="_alleles_parsed.fasta"
    asm_dir="/home/mlin77/data_blangme2/fasta/hprc-yr1/"
    asm_idx="/home/mlin77/data_blangme2/fasta/hprc-yr1/bwa/"

    #outer_dir="hprc_annotation/IGHV3-30_loci"
    #list_allele_name="IGHV3-30_genes"
    #allele_dir="./example/material/"
    #allele_suffix="_rename.fasta"
    #asm_dir="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/IGHV3-30_contig/"
    #asm_idx="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/IGHV3-30_contig/bwa/"

    outer_dir="AIRRsembly/reassemble_trio/"
    list_allele_name="BCRV BCRJ BCRD_plusHep"
    allele_dir="./example/material/"
    allele_suffix="_alleles_parsed.fasta"
    #asm_dir="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/clipped_fasta/hifiasm_result/"
    #asm_idx="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/clipped_fasta/hifiasm_result/bwa/"
    asm_dir="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/parent_data/hifiasm_result_noclip/"
    asm_idx="/home/mlin77/scr4_blangme2/maojan/AIRRssembly/parent_data/hifiasm_result_noclip/bwa/"
    
    person_name=$1
    #asm_path_H1="${asm_dir}${person_name}.1.fa"
    #asm_path_H2="${asm_dir}${person_name}.2.fa"
    #asm_path_H1_index="${asm_idx}${person_name}.1.fa"
    #asm_path_H2_index="${asm_idx}${person_name}.2.fa"
    #asm_path_H1="${asm_dir}${person_name}_hifiasm/${person_name}.IGH.asm.bp.hap1.fa"
    #asm_path_H2="${asm_dir}${person_name}_hifiasm/${person_name}.IGH.asm.bp.hap2.fa"
    #asm_path_H1_index="${asm_idx}${person_name}.IGH.asm.bp.hap1.fa"
    #asm_path_H2_index="${asm_idx}${person_name}.IGH.asm.bp.hap2.fa"
    asm_path_H1="${asm_dir}${person_name}.IGH.asm.noclip.hap1.fa"
    asm_path_H2="${asm_dir}${person_name}.IGH.asm.noclip.hap2.fa"
    asm_path_H1_index="${asm_idx}${person_name}.IGH.IGH.asm.noclip.hap1.fa"
    asm_path_H2_index="${asm_idx}${person_name}.IGH.IGH.asm.noclip.hap2.fa"
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
    python3 scripts/analysis/bed_generator.py -rl \
        ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRV.txt \
        ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRJ.txt \
        ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_BCRD_plusHep.txt \
        -o ${outer_dir}/${person_name}/group_genes
    #python3 scripts/analysis/bed_generator.py -rl \
    #    ${outer_dir}/${person_name}/annotation_imperfect_${person_name}_IGHV3-30_genes.txt \
    #    -o ${outer_dir}/${person_name}/group_genes
    python3 scripts/analysis/collect_gene_from_bed.py \
        -b1 ${outer_dir}/${person_name}/group_genes.1.bed \
        -b2 ${outer_dir}/${person_name}/group_genes.2.bed \
        -fl ${allele_dir}/IGH_functional.txt \
        > ${outer_dir}/${person_name}/IGH_functional.rpt
    echo "[ANNOTATION WITH ASM] ${person_name} Finished!"
}
export -f gairr_annotate
parallel gairr_annotate ::: \
    HG00733 \
    HG01109 \
    HG01243 \
    HG01258 \
    HG01978 \
    HG02055 \
    HG02080 \
    HG02109 \
    HG02145 \
    HG02723 \
    HG02818 \
    HG02886 \
    HG03098 \
    HG03486 \
    HG03492 \
    NA18906 \
    NA19240 \
    NA20129
#    HG002 \
#    HG00438 \
#    HG005   \
#    HG00621 \
#    HG00673 \
#    HG00733 \
#    HG00735 \
#    HG00741 \
#    HG01071 \
#    HG01106 \
#    HG01109 \
#    HG01123 \
#    HG01175 \
#    HG01243 \
#    HG01258 \
#    HG01358 \
#    HG01361 \
#    HG01891 \
#    HG01928 \
#    HG01952 \
#    HG01978 \
#    HG02055 \
#    HG02080 \
#    HG02109 \
#    HG02145 \
#    HG02148 \
#    HG02257 \
#    HG02486 \
#    HG02559 \
#    HG02572 \
#    HG02622 \
#    HG02630 \
#    HG02717 \
#    HG02723 \
#    HG02818 \
#    HG02886 \
#    HG03098 \
#    HG03453 \
#    HG03486 \
#    HG03492 \
#    HG03516 \
#    HG03540 \
#    HG03579 \
#    NA18906 \
#    NA19240 \
#    NA20129 \
#    NA21309
