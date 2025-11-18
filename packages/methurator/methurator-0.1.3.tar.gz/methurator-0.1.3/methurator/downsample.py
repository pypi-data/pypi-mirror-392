from methurator.downsample_utils.run_processing import run_processing
from methurator.config_utils.config_formatter import ConfigFormatter
from methurator.config_utils.config_validator import validate_parameters
from methurator.config_utils.bam_dir_utils import bam_to_list
from methurator.config_utils.verbose_utils import vprint
import rich_click as click
from rich.console import Console
from rich.panel import Panel
import os
import shutil


console = Console()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--bam",
    type=click.Path(exists=True),
    required=False,
    help="BAM input file to compute methylation saturation.",
)
@click.option(
    "--bamdir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=False,
    help="Directory containing multiple BAM files.",
)
@click.option(
    "--outdir",
    type=click.Path(),
    default="output",
    help="Default ./output directory.",
)
@click.option(
    "--fasta",
    type=click.Path(exists=True),
    help="Fasta file of the reference genome used to align the samples. "
    "If not provided, it will download it according to the specified genome.",
)
@click.option(
    "--genome",
    type=click.Choice(["hg19", "hg38", "GRCh37", "GRCh38", "mm10", "mm39"]),
    default=None,
    help="Genome used to align the samples.",
)
@click.option(
    "--downsampling-percentages",
    "-ds",
    default="0.1,0.25,0.5,0.75",
    help="Percentages used to downsample the .bam file. Default: 0.1,0.25,0.5,0.75",
)
@click.option(
    "--minimum-coverage",
    "-mc",
    default="3",
    help="Minimum CpG coverage to estimate sequencing saturation. It can be either a single integer or a list of integers (e.g 1,3,5). Default: 3",
)
@click.option(
    "--threads",
    "-@",
    type=int,
    default=os.cpu_count() - 2,
    help="Number of threads to use. Default: all available threads - 2.",
)
@click.option(
    "--keep-temporary-files",
    "-k",
    is_flag=True,
    help="If set to True, temporary files will be kept after the analysis. Default: False",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
def downsample(**kwargs):

    # Import the parameters and validate them
    configs = ConfigFormatter(**kwargs)
    validate_parameters(configs)

    # Print I/O parameters
    params_text = ""
    params_text += f"[purple]Output directory:[/purple] [blue]{configs.outdir}[/blue]\n"
    if configs.fasta is not None:
        params_text += (
            f"[purple]Reference FASTA:[/purple] [blue]{configs.fasta}[/blue]\n"
        )
    if configs.genome is not None:
        params_text += f"[purple]Genome:[/purple] [blue]{configs.genome}[/blue]\n"
    params_text += f"[purple]Downsampling percentages:[/purple] [blue]{configs.downsampling_percentages}[/blue]\n"
    params_text += f"[purple]Minimum coverage values:[/purple] [blue]{configs.minimum_coverage}[/blue]\n"
    params_text += f"[purple]Threads:[/purple] [blue]{configs.threads}[/blue]\n"
    params_text += f"[purple]Keep temporary files:[/purple] [blue]{configs.keep_temporary_files}[/blue]"
    console.print(
        Panel(
            params_text,
            title="📌 [bold cyan]Input / Output Parameters[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )

    # Load bam file(s) and run the downsampling
    csorted_bams = bam_to_list(configs)
    cpgs_df, reads_df = run_processing(csorted_bams, configs)
    reads_df.to_csv(os.path.join(configs.outdir, "reads_summary.csv"), index=False)
    cpgs_df.to_csv(os.path.join(configs.outdir, "cpgs_summary.csv"), index=False)
    vprint(f"[bold] ✅ Dumped summary files to {configs.outdir}.[/bold]", True)

    # Clean-up
    if not configs.keep_temporary_files:
        shutil.rmtree(os.path.join(configs.outdir, "bams"))
        shutil.rmtree(os.path.join(configs.outdir, "covs"))
