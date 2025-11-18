import os
import glob
import rich_click as click
from methurator.config_utils.verbose_utils import vprint
from methurator.config_utils.validation_utils import ensure_coordinated_sorted


def bam_to_list(configs):

    # If both bamdir and bam are provided, use the bamdir parameter
    if configs.bamdir and configs.bam:
        vprint(
            "[yellow]⚠️ Warning: both --bam and --bamdir were provided. Only --bamdir will be considered.[/yellow]",
            True,
        )
    csorted_bams = []

    # If bamdir is provided, import all bam files in the directory
    if configs.bamdir:
        raw_bam_files = import_bam_files(configs.bamdir)
        vprint(
            f"[bold]Found {len(raw_bam_files)} BAM files in directory '{configs.bamdir}'.[/bold]",
            configs.verbose,
        )
        for bam in raw_bam_files:
            # Check if bam file coordinate-sorted or sort it
            try:
                csorted_bam = ensure_coordinated_sorted(configs)
                csorted_bams.append(csorted_bam)
            except ValueError as e:
                raise click.UsageError(f"{e}")
    else:
        try:
            csorted_bam = ensure_coordinated_sorted(configs)
            csorted_bams.append(csorted_bam)
        except ValueError as e:
            raise click.UsageError(f"{e}")

    return csorted_bams


def import_bam_files(bam_dir):

    # Get all BAM files inside directory
    bam_files_all = sorted(glob.glob(os.path.join(bam_dir, "*.bam")))

    # Check if any BAM files were found
    if not bam_files_all:
        raise click.UsageError(f"No BAM files found in directory: {bam_dir}")

    # Remove duplicates (based on filename) and warn
    seen_filenames = set()
    bam_files = []
    for bam in bam_files_all:
        fname = os.path.basename(bam)
        if fname in seen_filenames:
            vprint(
                f"[yellow]⚠️ Warning: Duplicate BAM file found and discarded: {fname}[/yellow].",
                True,
            )
        else:
            seen_filenames.add(fname)
            bam_files.append(bam)

    # bam_files now contains only the BAM files
    return bam_files
