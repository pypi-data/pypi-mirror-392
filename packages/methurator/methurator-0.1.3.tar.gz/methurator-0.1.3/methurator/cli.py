import rich_click as click
from methurator.plot import plot
from methurator.downsample import downsample


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point():
    pass


# Register the 2 subcommands: downsample and plot
entry_point.add_command(plot)
entry_point.add_command(downsample)

if __name__ == "__main__":
    entry_point()
