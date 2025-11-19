from typing import Union, Callable, Dict, List, Any
from sympy import symbols, latex
import matplotlib.pyplot as plt
import math
import numpy as np
from itertools import product


def _get_parameter_combinations(parameters: Dict[str, Any]):
    """Convert parameters dict to a list of parameter combinations."""
    param_values = {k: v if isinstance(v, list) else [v] for k, v in parameters.items()}
    combinations = list(product(*param_values.values()))
    return [dict(zip(param_values.keys(), combo)) for combo in combinations]


def _get_support_bernulli(distribution, params_list):
    """Calculate support for Bernulli distribution."""
    if any(isinstance(params.get("p"), list) for params in params_list):
        return [np.arange(0, 2) for _ in params_list]
    return np.arange(0, 2)


def _get_support_binomial(distribution, params_list):
    """Calculate support for Binomial distribution."""
    supports = [np.arange(0, elem["n"] + 1) for elem in params_list]
    return supports[0] if len(supports) == 1 else supports


def _get_support_hypergeometric(distribution, params_list):
    """Calculate support for HyperGeometric distribution."""
    supports = [np.arange(0, elem["N"] + 1) for elem in params_list]
    return supports[0] if len(supports) == 1 else supports


def _get_support_uniform(distribution, params_list):
    """Calculate support for Uniform distribution."""
    supports = [np.arange(elemt["a"], elemt["b"]) for elemt in params_list]
    return supports[0] if len(supports) == 1 else supports


def _get_support_normal(distribution, params_list):
    """Calculate support for Normal distribution."""
    supports = [
        np.linspace(
            elemt["m"] - math.sqrt(elemt["v"]) * 3,
            elemt["m"] + math.sqrt(elemt["v"]) * 3,
            80,
        )
        for elemt in params_list
    ]
    return supports[0] if len(supports) == 1 else supports


def _get_support_probability_threshold(distribution, params_list, threshold=0.001):
    """Calculate support based on probability threshold."""
    support_max = []
    for param in params_list:
        support = []
        i = 0 if distribution.get_name == "Poisson" else 1
        while True:
            prob = distribution.replace(param).subs(distribution.x, i).evalf()
            if prob < threshold:
                break
            support.append(i)
            i += 1
        support_max.append(support)

    if len(support_max) == 1:
        return support_max[0]
    else:
        max_index = max(range(len(support_max)), key=lambda i: len(support_max[i]))
        longest_list = support_max[max_index]
        return [longest_list[:] for _ in support_max]


def _get_support_continuous_threshold_loc(
    distribution, params_list, threshold=0.001, start=0.01, end=None, min_value=1
):
    """Calculate support for continuous distributions based on threshold."""
    support_max = []
    for param in params_list:
        i = min_value + 1e-6
        max_num = 0
        while True:
            prob = distribution.replace(param).subs(distribution.x, i).evalf()
            if prob < threshold:
                max_num = i
                break
            i *= 2
        support_max.append(
            np.linspace(min_value, max_num if end is None else end, 2000)
        )

    if len(support_max) == 1:
        return support_max[0]
    else:
        max_index = max(range(len(support_max)), key=lambda i: len(support_max[i]))
        longest_list = support_max[max_index]
        return [longest_list[:] for _ in support_max]


def _get_support_continuous_threshold(
    distribution, params_list, threshold=0.001, start=0.01, end=None
):
    """Calculate support for continuous distributions based on threshold."""
    support_max = []
    for param in params_list:
        i = 1
        max_num = 0
        while True:
            prob = distribution.replace(param).subs(distribution.x, i).evalf()
            if prob < threshold:
                max_num = i
                break
            i *= 2
        support_max.append(np.linspace(start, max_num if end is None else end, 2000))

    if len(support_max) == 1:
        return support_max[0]
    else:
        max_index = max(range(len(support_max)), key=lambda i: len(support_max[i]))
        longest_list = support_max[max_index]
        return [longest_list[:] for _ in support_max]


def _get_support_exponential(distribution, params_list, start=None, end=None):
    """Calculate support for Exponential distribution."""
    support_max = []
    for param in params_list:
        i = 0
        max_num = 0
        while True:
            prob = distribution.replace(param).subs(distribution.x, i).evalf()
            if prob < 0.001:
                max_num = i
                break
            i += 1
        support_max.append(
            np.linspace(
                0 if start is None else start, max_num if end is None else end, 2000
            )
        )

    if len(support_max) == 1:
        return support_max[0]
    else:
        max_index = max(range(len(support_max)), key=lambda i: len(support_max[i]))
        longest_list = support_max[max_index]
        return [longest_list[:] for _ in support_max]


def _get_support_for_distribution(
    distribution, params_list, start=None, end=None, min_value=0
):
    """Determine appropriate support based on distribution type."""
    dist_name = distribution.get_name

    if dist_name == "Bernulli":
        return _get_support_bernulli(distribution, params_list)
    elif dist_name == "Binomial":
        return _get_support_binomial(distribution, params_list)
    elif dist_name == "HyperGeometric":
        return _get_support_hypergeometric(distribution, params_list)
    elif dist_name == "Uniform":
        return _get_support_uniform(distribution, params_list)
    elif dist_name == "Normal":
        return _get_support_normal(distribution, params_list)
    elif dist_name == "Exponential":
        return _get_support_exponential(distribution, params_list, start=start, end=end)
    elif dist_name == "Geometric" or dist_name == "Poisson":
        return _get_support_probability_threshold(distribution, params_list)
    elif dist_name in [
        "Weibull",
        "Gamma",
        "Beta",
        "Lindley 1",
        "Lindley 2",
        "Gumbel",
        "Birnbaum-Saunders",
        "Inverse-Weibull",
        "Nadarajah-Haghighi",
    ]:
        return _get_support_continuous_threshold(
            distribution, params_list, start=start, end=end
        )
    elif dist_name in ["LogNormal", "Weibull 3-Parameters"]:
        return _get_support_continuous_threshold_loc(
            distribution, params_list, start=start, end=end, min_value=min_value
        )
    elif dist_name in ["Burr 7", "Pareto 1", "Pareto 2", "Pareto 9"]:
        return _get_support_continuous_threshold(
            distribution, params_list, start=0.1 if start is None else start, end=end
        )

    return np.linspace(0.1, 10, 50)


def _plot_discrete_distribution(
    ax: plt.Axes,
    support: List,
    probs: List,
    color=None,
    params: Dict = None,
    distribution: Callable = None,
    mode: str = None,
    label: str = None,
):
    """Plot a discrete distribution."""

    if mode.lower() in ["cdf", "sf", "hf"]:
        for i in range(len(list(support)) - 1):
            ax.hlines(
                y=probs[i],
                xmin=list(support)[i],
                xmax=list(support)[i + 1],
                color=color if color else "r",
                linestyle="-",
            )

    if label == "Function":
        l = (
            r"$"
            + latex(distribution.replace(params, mode))
            + (f", {params}" if params else "")
            + r"$"
        )
    else:
        l = distribution.get_name

    markerline, stemlines, baseline = ax.stem(
        list(support),
        probs,
        linefmt="",
        markerfmt="o",
        basefmt=" ",
        label=l,
    )
    stemlines.set_visible(False)
    baseline.set_visible(False)

    if color:
        markerline.set_color(color)

    return ax


def _plot_continuous_distribution(
    ax: plt.Axes,
    support: List,
    probs: List,
    color=None,
    params: Dict = None,
    distribution: Callable = None,
    mode: str = None,
    label: str = None,
):
    """Plot a continuous distribution."""
    if label == "Function":
        l = r"$" + (f"{params}" if params else "") + r"$"
    else:
        l = distribution.get_name

    ax.plot(
        support,
        probs,
        color=color,
        label=l,
    )

    return ax


def plot_function(
    ax: plt.Axes, function: Union[str, Callable], mode: str, parameters, *args, **kwargs
):
    """
    Plot a probabilistic function with given parameters.

    Args:
        function: The probabilistic function to plot
        mode: Mode of the function
        parameters: Dictionary of parameters for the function
        *args, **kwargs: Additional arguments for the plot
    """
    legend = kwargs.get("legend", True)
    if legend:
        label = kwargs.get("label", "Name")
    print_ = kwargs.get("debug", False)
    title = kwargs.get("title", True)
    colors_con = kwargs.get("color_con", None)
    start = kwargs.get("start", None)
    end = kwargs.get("end", None)
    colors = kwargs.get("color", plt.cm.tab10.colors)
    distribution = function
    # Get all parameter combinations
    param_combinations = _get_parameter_combinations(parameters)

    # Get appropriate supports for this distribution
    distribution._support = _get_support_for_distribution(
        distribution,
        param_combinations,
        start=start,
        end=end,
        min_value=kwargs.get("min_value", 0),
    )
    if print_:
        print(f"Support: {distribution._support}")

    # Handle multiple parameter sets
    if len(param_combinations) > 1:
        for i, (params, color, support) in enumerate(
            zip(
                param_combinations,
                colors[: len(param_combinations)],
                (
                    distribution._support
                    if isinstance(distribution._support, list)
                    else [distribution._support] * len(param_combinations)
                ),
            )
        ):
            if mode.upper() == "SF":
                print(**params)
                probs = distribution.sf(support, **params)
            else:
                dis = distribution.replace(params, mode)
            probs = [dis.subs(distribution.x, i).evalf() for i in support]
            if print_:
                print(f"Parameters: {params}, Probabilities: {probs}")
            if distribution.get_mode == "Discrete":
                ax = _plot_discrete_distribution(
                    ax,
                    support,
                    probs,
                    color=color,
                    params=params,
                    distribution=distribution,
                    mode=mode,
                    label=label if legend else None,
                )
            elif distribution.get_mode == "Continuous":
                ax = _plot_continuous_distribution(
                    ax,
                    support,
                    probs,
                    color=color,
                    params=params,
                    distribution=distribution,
                    mode=mode,
                    label=label if legend else None,
                )
    else:
        # Single parameter set
        dis = distribution.replace(param_combinations[0], mode)
        if print_:
            print(f"Using parameters: {param_combinations[0]}")
            print(dis)
        support = distribution._support
        probs = [dis.subs(distribution.x, i).evalf() for i in support]
        if print_:
            print(f"Parameters: {param_combinations[0]}, Probabilities: {probs}")
        if distribution.get_mode == "Discrete":
            ax = _plot_discrete_distribution(
                ax,
                support,
                probs,
                params=parameters,
                distribution=distribution,
                mode=mode,
                color=colors_con,
                label=label if legend else None,
            )
        elif distribution.get_mode == "Continuous":
            ax = _plot_continuous_distribution(
                ax,
                support,
                probs,
                color=colors_con,
                params=parameters,
                distribution=distribution,
                mode=mode,
                label=label if legend else None,
            )
    if legend:
        ax.legend()

    if title:
        t = {
            "cdf": "Cumulative Distribution Function",
            "pdf": "Probability Density Function",
            "pmf": "Probability Mass Function",
            "sf": "Survival Function",
            "hf": "Hazard Function",
        }
        ax.set_title(f"{t[mode.lower()]} of {distribution.get_name} Distribution")
    return ax


def multi_plot_function(
    ax: plt.Axes, distributions: Dict[Callable, Dict], mode: str, *args, **kwargs
):
    """
    Plot multiple probabilistic functions with given parameters.

    Args:
        distributions: A dictionary where keys are distribution instances and values are parameter dictionaries
        mode: Mode of the function
        *args, **kwargs: Additional arguments for the plot
    """
    colors = kwargs.get("color", plt.cm.tab20.colors)
    for i, (distribution, parameters) in enumerate(distributions.items()):
        color = colors[i % len(colors)]
        kwargs["color_con"] = color
        plot_function(ax, distribution, mode, parameters, *args, **kwargs)

    return ax


# Import distributions based on context
if __name__ == "__main__":
    from probabilistic_functions.core import (
        Bernulli,
        Binomial,
        Geometric,
        HyperGeometric,
        Poisson,
        Uniform,
        Exponential,
        Normal,
        Weibull,
    )
else:
    from .core import (
        Bernulli,
        Binomial,
        Geometric,
        HyperGeometric,
        Poisson,
        Uniform,
        Exponential,
        Normal,
        Weibull,
    )
