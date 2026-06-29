#!/usr/bin/env python3

import argparse
import csv
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract and rename MultiQC FastQC columns into R1/R2 summary table"
    )

    parser.add_argument("-i", "--input", default="qc-results/multiqc/multiqc_data/multiqc_fastqc.txt", help="multiqc_fastqc.txt file from MultiQC")
    parser.add_argument("-o", "--output", required=True)

    parser.add_argument(
        "-c", "--columns",
        default="Total Sequences:readcount",
        help='Comma-separated mappings like "Total Sequences:readcount,total_deduplicated_percentage:duplicated"'
    )

    return parser.parse_args()


def parse_column_map(column_string):
    """
    Turns:
        "Total Sequences:readcount,%GC:gc"

    into:
        {
            "Total Sequences": "readcount",
            "%GC": "gc"
        }
    """
    mapping = {}

    for item in column_string.split(","):
        item = item.strip()

        if ":" in item:
            src, dst = item.split(":", 1)
        else:
            src = dst = item  # fallback: no rename

        mapping[src.strip()] = dst.strip()

    return mapping


def get_base_and_read(sample_name):
    base, read = sample_name.rsplit("_", 1)
    if read == "1":
        return base, "R1"
    elif read == "2":
        return base, "R2"
    return sample_name, None


def main():
    args = parse_args()
    colmap = parse_column_map(args.columns)

    data = defaultdict(lambda: defaultdict(dict))

    with open(args.input) as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            sample_raw = row["Sample"]
            base, read = get_base_and_read(sample_raw)

            if read is None:
                continue

            for src_col, new_name in colmap.items():
                if src_col not in row:
                    continue

                value = row[src_col]

                # try numeric conversion
                try:
                    if value not in ("", "NaN"):
                        value = float(value)
                except ValueError:
                    pass

                data[base][read][new_name] = value

    with open(args.output, "w", newline="") as out:
        writer = csv.writer(out)

        # header
        header = ["sample"]
        for _, new_name in colmap.items():
            header.append(f"R1_{new_name}")
            header.append(f"R2_{new_name}")

        writer.writerow(header)

        for sample in sorted(data.keys()):
            row_out = [sample]

            for _, new_name in colmap.items():
                r1 = data[sample].get("R1", {}).get(new_name, "")
                r2 = data[sample].get("R2", {}).get(new_name, "")
                row_out.extend([r1, r2])

            writer.writerow(row_out)


if __name__ == "__main__":
    main()
