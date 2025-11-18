import rich_click as click
import os
from methurator.config_utils.validation_utils import (
    mincoverage_checker,
    percentage_checker,
    validate_reference,
    validate_bamdir,
)
from methurator.config_utils.verbose_utils import vprint


def validate_parameters(configs):

    # Enforce that at least one of --fasta or --genome is provided
    if configs.fasta is None and configs.genome is None:
        raise click.UsageError(
            "Error: you must provide in input either --fasta or --genome"
        )

    # Enforce that at least one of --bam or --bamdir is provided
    if configs.bam is None and configs.bamdir is None:
        raise click.UsageError(
            "Error: you must provide in input either --bam or --bamdir"
        )

    # Check that downsampling percentages and minimum coverage values are valid
    try:
        configs.percentages = percentage_checker(configs.downsampling_percentages)
    except ValueError as e:
        raise click.UsageError(f"{e}")
    try:
        configs.coverages = mincoverage_checker(configs.minimum_coverage)
    except ValueError as e:
        raise click.UsageError(f"{e}")

    # Run checks on fasta file if provided or download it
    try:
        configs.fasta = validate_reference(configs)
    except ValueError as e:
        raise click.UsageError(f"{e}")

    # Run check on the bam directory if provided
    if configs.bamdir:
        validate_bamdir(configs.bamdir)

    # Create output directory if it doesn't exist
    if not os.path.exists(configs.outdir):
        os.makedirs(configs.outdir, exist_ok=True)
        vprint(
            f"[bold]Created output directory {configs.outdir}...[/bold]",
            configs.verbose,
        )
