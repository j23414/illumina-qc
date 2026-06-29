# illumina-qc



* Preferentially use nf-core modules where available
* Loads St Jude LSF config by default
* Separate QC from downstream analysis
* Accept either a samplesheet CSV (sample,R1,R2) or a FASTQ glob pattern
* Allow QC to complete for valid samples even if one or more samples fail

## samplesheet input

```
sample,R1,R2
Alice,data/alice_R1.fastq.gz,data/alice_R2.fastq.gz
Bill,data/billion_R1.fastq.gz,data/billion_R2.fastq.gz
Mark,data/mark_R1_001.fastq.gz,data/mark_R2_001.fastq.gz
```

```bash
nextflow run j23414/illumina-qc \
  --samplesheet samplesheet.tsv \
  -profile stjude
```

## glob input

```bash
nextflow run j23414/illumina-qc \
  --reads "data/*_{R1,R2}_*.fastq.gz" \
  -profile stjude
```
