from methurator.plot_utils.plot_curve import plot_curve
import rich_click as click
from methurator.config_utils.config_formatter import ConfigFormatter
from methurator.config_utils.validation_utils import (
    validate_read_summary,
    validate_cpgs_summary,
)
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--cpgs_file",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="File containing CpGs coverage information.",
)
@click.option(
    "--reads_file",
    "-r",
    type=click.Path(exists=True),
    required=True,
    help="File containing reads coverage information.",
)
@click.option(
    "--outdir",
    type=click.Path(),
    default="output",
    help="Default output directory.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
def plot(**kwargs):

    # Import and validate params
    configs = ConfigFormatter(**kwargs)
    validate_cpgs_summary(configs.cpgs_file)
    validate_read_summary(configs.reads_file)

    # Print I/O parameters
    params_text = ""
    params_text += (
        f"[purple]CpGs summary file:[/purple] [blue]{configs.cpgs_file}[/blue]\n"
    )
    params_text += (
        f"[purple]Reads summary file:[/purple] [blue]{configs.reads_file}[/blue]\n"
    )
    params_text += f"[purple]Output directory:[/purple] [blue]{configs.outdir}[/blue]"
    console.print(
        Panel(
            params_text,
            title="📌 [bold cyan]Input / Output Parameters[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )

    # Fit the model and plot the saturation curve
    plot_curve(configs)
