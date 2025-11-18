import rich_click as click
from methurator.config_utils.verbose_utils import vprint
from methurator.config_utils.download_reference import get_reference
import os
import subprocess
import pysam
import pandas as pd


def mincoverage_checker(coverages):
    """
    Converts a comma-separated string into a list of integers.
    """
    values = coverages.split(",")
    list_coverages = []

    for x in values:
        x = x.strip()
        if not x.isdigit():
            raise click.UsageError(
                f"Invalid minimum coverage value: '{x}'. All minimum coverage must be integers."
            )
        if int(x) == 0:
            vprint(
                f"[yellow]⚠️ Warning: coverage values must be at least >=1, '{x}' was ignored.[/yellow]",
                True,
            )
        else:
            list_coverages.append(int(x))

    return list_coverages


def percentage_checker(percentages):
    """
    Converts a comma-separated string into a list of floats.
    """
    list_percentages = [float(x.strip()) for x in percentages.split(",")]

    if any(p == 0 for p in list_percentages):
        raise click.UsageError("Percentages must be between > 0.")

    if len(list_percentages) < 4:
        raise click.UsageError("At least four percentages must be provided.")

    # And now add 1 if not persent to the list
    # to calculate CpG number on original sample
    if 1 not in list_percentages:
        list_percentages = list_percentages + [1]

    return list_percentages


def validate_reference(configs):

    if configs.fasta and configs.genome:
        vprint(
            "[yellow]⚠️ Both --fasta and --genome provided. Using the provided fasta file.[/yellow]",
            configs.verbose,
        )

    if configs.fasta:
        if not (configs.fasta.endswith(".fa") or configs.fasta.endswith(".fasta")):
            raise click.UsageError(
                "The fasta file provided must end with .fa or .fasta."
            )
        if not os.path.exists(configs.fasta):
            raise click.UsageError(f"The fasta file '{configs.fasta}' does not exist.")
        return configs.fasta
    else:
        fasta_file = get_reference(configs)
        return fasta_file


def validate_bamdir(bam_dir):
    # Check if directory exists
    if not os.path.exists(bam_dir):
        raise click.UsageError(f"Directory does not exist: {bam_dir}")

    if not os.path.isdir(bam_dir):
        raise click.UsageError(f"Path is not a directory: {bam_dir}")


def ensure_coordinated_sorted(configs):

    # Check if file exists
    if not os.path.exists(configs.bam):
        raise click.UsageError(f"The file '{configs.bam}' does not exist.")

    # Check if file ends with .bam
    if not configs.bam.endswith(".bam"):
        raise click.UsageError("The input file must end with .bam")

    with pysam.AlignmentFile(configs.bam, "rb") as bam:
        sort_order = bam.header.get("HD", {}).get("SO", None)

    if sort_order == "coordinate":
        return configs.bam

    vprint("🔄 BAM file is not coordinate-sorted. Sorting now...", configs.verbose)
    out = configs.bam.replace(".bam", ".csorted.bam")
    cmd = ["samtools", "sort", "-o", out, configs.bam]

    # Run samtools
    subprocess.run(cmd)

    return out


def validate_read_summary(read_summary):
    REQUIRED_COLUMNS = {"Sample", "Percentage", "Read_Count"}
    # Check if file is CSV by extension
    if not read_summary.lower().endswith(".csv"):
        raise click.UsageError(f"The file '{read_summary}' is not a CSV file.")

    # Check file exists
    if not os.path.isfile(read_summary):
        raise click.UsageError(f"File '{read_summary}' does not exist.")

    # Try reading file
    df = pd.read_csv(read_summary, nrows=0)

    # Validate required columns
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise click.UsageError(
            f"Missing required columns in the reads summary file: {', '.join(missing_cols)}"
        )


def validate_cpgs_summary(cpgs_summary):
    REQUIRED_COLUMNS = {"Sample", "Percentage", "Coverage", "CpG_Count"}
    # Check if file is CSV by extension
    if not cpgs_summary.lower().endswith(".csv"):
        raise click.UsageError(f"The file '{cpgs_summary}' is not a CSV file.")

    # Check file exists
    if not os.path.isfile(cpgs_summary):
        raise click.UsageError(f"File '{cpgs_summary}' does not exist.")

    # Try reading file
    df = pd.read_csv(cpgs_summary, nrows=0)

    # Validate required columns
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise click.UsageError(
            f"Missing required columns in the CpGs summary file: {', '.join(missing_cols)}"
        )
