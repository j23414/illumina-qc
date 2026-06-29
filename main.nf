include { FASTQC  } from './modules/nf-core/fastqc/main' 
include { MULTIQC } from './modules/nf-core/multiqc/main'

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

    // Run QC
    FASTQC(reads_ch)
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
    MULTIQC.out.report.view()
}
