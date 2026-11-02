include { FASTP } from './modules/nf-core/fastp/main'
include { FASTQC  } from './modules/nf-core/fastqc/main'
include { MULTIQC } from './modules/nf-core/multiqc/main'

process SUMMARYCOUNT {
  conda 'conda-forge::python=3.12'
  input:
    tuple val(meta), path(multiqc_tsv)

  output:
    path("summary_counts.csv")

  script:
  """
  python ${workflow.projectDir}/bin/get-summary-counts.py \
  --columns "${params.summary_columns}" \
  --input $multiqc_tsv \
  --output summary_counts.csv
  """
}

workflow {
    main:
    // Illumina Reads
    if (params.samplesheet) {
      reads_ch = channel.fromPath(params.samplesheet)
        | splitCsv(header: true)
        | map { row ->
            tuple([id: row.sample], [file(row.R1), file(row.R2)])
          }
    } else if (params.reads) {
        reads_ch = channel.fromFilePairs(params.reads, checkIfExists: true)
          | map { name, reads -> tuple([id: name], reads) }
    } else {
        error "Please specify either --samplesheet samplesheet.csv or --reads 'data/*_{R1,R2}.fastq.gz'"
    }

    if(params.trim_adaptors == "fastp") {
      adapter_ch = params.adapter_fasta ? file(params.adapter_fasta) : []

      FASTP(
        reads_ch.map { meta, reads -> tuple(meta, reads, adapter_ch)},
        false,
        false,
        false)
      trimmed_reads_ch = FASTP.out.reads

      // Generate new samplesheet for next pipeline
      trimmed_reads_ch
      .map { meta, reads -> "${meta.id},fastp/${reads[0].fileName},fastp/${reads[1].fileName}" }
      .collectFile(
        name: "${params.outdir}_${params.trim_adaptors}/processed_samplesheet.csv",
        seed: "sample,R1,R2",
        newLine: true,
      )
    } else {
      trimmed_reads_ch=reads_ch
    }

    // Run QC
    FASTQC(trimmed_reads_ch)
    FASTQC.out.html

      multiqc_input = FASTQC.out.html.map{meta, files -> files}
      | mix(FASTQC.out.zip.map{meta, files -> files})
      | flatten
      | collect
      | map {
        n ->
        def meta = [id: 'all']
        return tuple(meta, n, [], [], [], [])
      }


    MULTIQC(multiqc_input)
    SUMMARYCOUNT(MULTIQC.out.tsv)
}
