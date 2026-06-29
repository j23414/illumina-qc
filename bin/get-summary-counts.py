#!/usr/bin/env python3

import argparse
import csv
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract R1/R2 read counts from MultiQC FastQC summary table"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="multiqc_fastqc.txt file from MultiQC"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output CSV file"
    )
    return parser.parse_args()


def clean_sample(sample):
    """
    Remove trailing _1 / _2 from FastQC sample names
    """
    if sample.endswith("_1") or sample.endswith("_2"):
        return sample[:-2]
    return sample


def infer_read_direction(sample):
    if sample.endswith("_1"):
        return "R1"
    elif sample.endswith("_2"):
        return "R2"
    else:
        return None


def main():
    args = parse_args()

    counts = defaultdict(lambda: {"R1": None, "R2": None})

    with open(args.input, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            sample_raw = row["Sample"]
            total = row["Total Sequences"]

            if not total or total == "NaN":
                continue

            total = int(float(total))

            if sample_raw.endswith("_1"):
                base = sample_raw[:-2]
                counts[base]["R1"] = total
            elif sample_raw.endswith("_2"):
                base = sample_raw[:-2]
                counts[base]["R2"] = total

    with open(args.output, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["sample", "R1_readcount", "R2_readcount"])

        for sample in sorted(counts.keys()):
            r1 = counts[sample]["R1"]
            r2 = counts[sample]["R2"]
            writer.writerow([sample, r1, r2])


if __name__ == "__main__":
    main()