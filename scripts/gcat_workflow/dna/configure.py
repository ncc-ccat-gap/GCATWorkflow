#! /usr/bin/env python

def main(gcat_conf, run_conf, sample_conf):
    
    # preparation
    import gcat_workflow.core.setup_common as setup
    input_stages = (sample_conf.bam_import, sample_conf.fastq, sample_conf.bam_tofastq)
    setup.create_directories(gcat_conf, run_conf, input_stages, 'dna/data/snakefile.txt')
    setup.touch_bam_tofastq(run_conf, (sample_conf.bam_tofastq, ))
    
    # dump conf.yaml
    import gcat_workflow.dna.resource.bwa_align as rs_align
    y = setup.dump_yaml_input_section(
        run_conf, 
        (sample_conf.bam_tofastq, ),
        sample_conf.fastq,
        sample_conf.bam_import, 
        rs_align.OUTPUT_FORMAT
    )

    # link fastq
    linked_fastqs = setup.link_input_fastq(run_conf, sample_conf.fastq, sample_conf.fastq_src)
    
    # link import bam
    output_bams = setup.link_import_bam(
        run_conf, 
        sample_conf.bam_import, 
        rs_align.BAM_POSTFIX, 
        rs_align.BAI_POSTFIX,
        rs_align.OUTPUT_FORMAT.split("/")[0]
    )

    # ######################
    # create scripts
    # ######################
    # bam to fastq
    import gcat_workflow.dna.resource.bamtofastq as rs_bamtofastq
    output_fastqs = rs_bamtofastq.configure(gcat_conf, run_conf, sample_conf)
    
    # bwa
    for sample in output_fastqs:
        sample_conf.fastq[sample] = output_fastqs[sample]
        sample_conf.fastq_src[sample] = [[], []]

    for sample in linked_fastqs:
        sample_conf.fastq[sample] = linked_fastqs[sample]["fastq"]
        sample_conf.fastq_src[sample] = linked_fastqs[sample]["src"]
    
    align_bams = rs_align.configure(gcat_conf, run_conf, sample_conf)
    output_bams.update(align_bams)

    # mutation
    import gcat_workflow.dna.resource.mutation_dummy as rs_mutation
    output_mutations = rs_mutation.configure(output_bams, gcat_conf, run_conf, sample_conf)
    
    # sv
    import gcat_workflow.dna.resource.sv_dummy as rs_sv
    output_svs = rs_sv.configure(output_bams, gcat_conf, run_conf, sample_conf)
    
    # qc
    import gcat_workflow.dna.resource.qc_bamstats as rs_qc_bamstats
    output_bamstats = rs_qc_bamstats.configure(output_bams, gcat_conf, run_conf, sample_conf)
    import gcat_workflow.dna.resource.qc_coverage as rs_qc_coverage
    output_coverage = rs_qc_coverage.configure(output_bams, gcat_conf, run_conf, sample_conf)
    import gcat_workflow.dna.resource.qc_merge as rs_qc_merge
    output_qc = rs_qc_merge.configure(output_bams, gcat_conf, run_conf, sample_conf)

    # ######################
    # dump conf.yaml
    # ######################
    def __to_relpath(fullpath):
        return fullpath.replace(run_conf.project_root + "/", "", 1)
        
    def __dic_values(dic):
        values = []
        for key in dic:
            if type(dic[key]) == list:
                for path in dic[key]:
                    values.append(__to_relpath(path))
            else:
                values.append(__to_relpath(dic[key]))
        return values
    
    y["output_files"].extend(__dic_values(output_mutations))
    y["output_files"].extend(__dic_values(output_svs))
    y["output_files"].extend(__dic_values(output_bamstats))
    y["output_files"].extend(__dic_values(output_coverage))
    y["output_files"].extend(__dic_values(output_qc))
    
    y["mutation_samples"] = {}
    for (sample, control, control_panel) in sample_conf.mutation_call:
        y["mutation_samples"][sample] = rs_align.OUTPUT_FORMAT.format(sample=sample)
        
    y["sv_samples"] = {}
    for (sample, control, control_panel) in sample_conf.sv_detection:
        y["sv_samples"][sample] = rs_align.OUTPUT_FORMAT.format(sample=sample)

    y["qc_samples"] = {}
    y["qc_merge"] = {}
    for sample in sample_conf.qc:
        y["qc_samples"][sample] = rs_align.OUTPUT_FORMAT.format(sample=sample)
        y["qc_merge"][sample] = [__to_relpath(output_coverage[sample]), __to_relpath(output_bamstats[sample])]

    import yaml
    open(run_conf.project_root + "/config.yml", "w").write(yaml.dump(y))
    
