#! /usr/bin/env python

import gcat_workflow.core.stage_task_abc as stage_task

class Mutation_dummy(stage_task.Stage_task):
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

mkdir -p $(dirname {OUTPUT_FILE})
samtools view -H {INPUT_BAM} > {OUTPUT_FILE}
"""

def configure(input_bams, gcat_conf, run_conf, sample_conf):
    params = {
        "work_dir": run_conf.project_root,
        "stage_name": "mutation_dummy",
        "image": gcat_conf.path_get("mutation_dummy", "image"),
        "qsub_option": gcat_conf.get("mutation_dummy", "qsub_option"),
        "singularity_option": gcat_conf.get("mutation_dummy", "singularity_option")
    }
    stage_class = Mutation_dummy(params)
    
    output_files = {}
    for (sample, control, control_panel) in sample_conf.mutation_call:
        output_file = "%s/mutation/%s/%s.txt" % (run_conf.project_root, sample, sample)
        output_files[sample] = output_file
        
        arguments = {
            "SAMPLE": sample,
            "INPUT_BAM": input_bams[sample],
            "OUTPUT_FILE": output_file,
        }
       
        singularity_bind = [run_conf.project_root]
        if sample in sample_conf.bam_import_src:
            singularity_bind += sample_conf.bam_import_src[sample]
            
        stage_class.write_script(arguments, singularity_bind, run_conf, sample = sample)
    
    return output_files
