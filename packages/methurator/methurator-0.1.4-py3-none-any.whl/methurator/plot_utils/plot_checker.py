import warnings
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning
from methurator.plot_utils.math_model import asymptotic_growth, find_asymptote
from methurator.plot_utils.plot_functions import plot_fitted_data, plot_fallback


class PlotObject:
    def __init__(self, output_path):
        self.x_data = []
        self.y_data = []
        self.asymptote = str
        self.params = []
        self.title = str
        self.reads = int
        self.error_msg = None
        self.output_path = output_path


def plot_checker(data, output_path):

    # Create the PlotObject
    plot_obj = PlotObject(output_path)

    # Add the zeros at the beginning of the data to fit the model
    plot_obj.x_data = np.array([0] + data["Percentage"].tolist())
    plot_obj.y_data = np.array([0] + data["CpG_Count"].tolist())

    # try to fit the asymptotic growth model to the data
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", OptimizeWarning)
            plot_obj.params, _ = curve_fit(
                asymptotic_growth, plot_obj.x_data, plot_obj.y_data, p0=[1, 1]
            )
            plot_obj.asymptote = find_asymptote(plot_obj.params)
            fit_success = True
    # If not enough data points or fitting fails, handle the exception
    except (RuntimeError, OptimizeWarning) as e:
        fit_success = False
        plot_obj.params, plot_obj.asymptote, plot_obj.error_msg = None, None, str(e)

    # Prepare title and reads information
    plot_obj.title = data["Sample"].iloc[0]
    plot_obj.reads = int(data["Read_Count"].iloc[-1])

    # If fitting was successful, plot the fitted curve;
    # otherwise, plot the dots with the error message
    if fit_success:
        plot_fitted_data(plot_obj)
    else:
        plot_fallback(plot_obj)
