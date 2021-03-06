#! /usr/bin/env python

import os
import gcat_workflow.core.stage_task_abc as stage_task

class Gridss(stage_task.Stage_task):
    def __init__(self, params):
        super().__init__(params)
        self.shell_script_template = """#!/bin/bash
#
# Set SGE
#
#$ -S /bin/bash         # set shell in UGE
#$ -cwd                 # execute at the submitted dir
pwd                     # print current working directory
hostname                # print hostname
date                    # print date
set -o errexit
set -o nounset
set -o pipefail
set -x

output_dir=$(dirname {OUTPUT_VCF})
mkdir -p ${{output_dir}}

output_pref=${{output_dir}}/{SAMPLE}

/tools/samtools-1.9/samtools view \\
    -T {REFERENCE} \\
    -h \\
    -b \\
    {SAMTOOLS_OPTION} \\
    {INPUT_TUMOR_CRAM} > ${{output_pref}}.tumor.temp.bam

/tools/samtools-1.9/samtools view \\
    -T {REFERENCE} \\
    -h \\
    -b \\
    {SAMTOOLS_OPTION} \\
    {INPUT_NORMAL_CRAM} > ${{output_pref}}.normal.temp.bam

/tools/samtools-1.9/samtools index \\
    ${{output_pref}}.tumor.temp.bam
    
/tools/samtools-1.9/samtools index \\
    ${{output_pref}}.normal.temp.bam

/opt/gridss/gridss.sh \\
    -o {OUTPUT_VCF}  \\
    -a ${{output_pref}}.gridss-assembly.bam \\
    -r {REFERENCE}  \\
    -j /opt/gridss/{GRIDSS_JAR} \\
    -w ${{output_dir}} \\
    {GRIDSS_OPTION} \\
    ${{output_pref}}.normal.temp.bam \\
    ${{output_pref}}.tumor.temp.bam

rm ${{output_pref}}.tumor.temp.bam
rm ${{output_pref}}.tumor.temp.bam.bai
rm ${{output_pref}}.normal.temp.bam
rm ${{output_pref}}.normal.temp.bam.bai
"""

def configure(input_bams, gcat_conf, run_conf, sample_conf):
    
    STAGE_NAME = "gridss"
    CONF_SECTION = STAGE_NAME
    params = {
        "work_dir": run_conf.project_root,
        "stage_name": STAGE_NAME,
        "image": gcat_conf.path_get(CONF_SECTION, "image"),
        "qsub_option": gcat_conf.get(CONF_SECTION, "qsub_option"),
        "singularity_option": gcat_conf.get(CONF_SECTION, "singularity_option")
    }
    stage_class = Gridss(params)
    
    output_files = {}
    for (tumor, normal) in sample_conf.gridss:
        output_vcf = "%s/gridss/%s/%s.gridss.vcf" % (run_conf.project_root, tumor, tumor)
        output_files[tumor] = output_vcf
        arguments = {
            "SAMPLE": tumor,
            "INPUT_TUMOR_CRAM": input_bams[tumor],
            "INPUT_NORMAL_CRAM": input_bams[normal],
            "OUTPUT_VCF":  output_vcf,
            "REFERENCE": gcat_conf.path_get(CONF_SECTION, "reference"),
            "GRIDSS_OPTION": gcat_conf.get(CONF_SECTION, "gridss_option") + " " + gcat_conf.get(CONF_SECTION, "gridss_threads_option"),
            "GRIDSS_JAR": gcat_conf.get(CONF_SECTION, "gridss_jar"),
            "SAMTOOLS_OPTION": gcat_conf.get(CONF_SECTION, "samtools_option") + " " + gcat_conf.get(CONF_SECTION, "samtools_threads_option")
        }
       
        singularity_bind = [run_conf.project_root, os.path.dirname(gcat_conf.path_get(CONF_SECTION, "reference"))]
        if tumor in sample_conf.bam_import_src:
            singularity_bind += sample_conf.bam_import_src[tumor]
            
        stage_class.write_script(arguments, singularity_bind, run_conf, sample = tumor)
    
    return output_files
