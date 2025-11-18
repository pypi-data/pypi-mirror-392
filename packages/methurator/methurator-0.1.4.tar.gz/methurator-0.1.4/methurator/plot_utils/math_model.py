import numpy as np

# ===============================================================
# Mathematical Model
# ===============================================================


def asymptotic_growth(x, beta0, beta1):
    """Asymptotic growth model using the arctangent function."""
    return beta0 * np.arctan(beta1 * x)


def derivative_asymptotic_growth(x, beta0, beta1):
    """Derivative of the asymptotic growth model."""
    return beta0 * beta1 / (1 + (beta1 * x) ** 2)


def find_asymptote(params):
    """Return the asymptote value (y-limit as x → ∞)."""
    beta0, _ = params
    return beta0 * np.pi / 2
