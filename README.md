# basic-illumina-qc

* Preferentially use nf-core modules where available
* Loads St Jude LSF config by default
* Separate QC from downstream analysis

```bash
nextflow run j23414/illumina-qc \
  --reads "data/*_{R1,R2}_*.fastq.gz" \
  -profile stjude \
  -resume
```