import pandas as pd
import os
from methurator.plot_utils.plot_checker import plot_checker


def plot_curve(configs):

    # Takes in input the CpGs and Reads stats dataframes and merge them
    cpgs_file = pd.read_csv(configs.cpgs_file)
    reads_file = pd.read_csv(configs.reads_file)
    data = pd.merge(cpgs_file, reads_file, on=["Sample", "Percentage"])

    # Loop over each sample and minimum coverage value to create plots
    for sample in data["Sample"].unique():
        sample_data = data[data["Sample"] == sample]
        for min_val in sample_data["Coverage"].unique():

            # Subset and sort data for plotting
            subset = sample_data[sample_data["Coverage"] == min_val].sort_values(
                by="Percentage"
            )

            # Create output directory for plots if not exists
            plot_dir = os.path.join(configs.outdir, "plots")
            os.makedirs(plot_dir, exist_ok=True)

            # Define plot path
            plot_path = f"{plot_dir}/{sample}_{min_val}x_plot.svg"

            # Checks whether the model fits correctly, then generate plot
            plot_checker(subset, plot_path)
