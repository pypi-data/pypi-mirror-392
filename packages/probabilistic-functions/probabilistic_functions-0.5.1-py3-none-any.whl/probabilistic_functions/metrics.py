from typing import List, Union, Any, Callable, Dict, Tuple
import numpy as np
import numdifftools as nd
from math import log
from sympy import lambdify, symbols
from scipy.stats import kstest, anderson
from .utils import dict_values_to_list, to_float


def calculate_variance_by_hessian(
    distribution: Any,
    params: Union[List, np.ndarray],
    data: Union[List, np.ndarray],
) -> np.ndarray:
    if isinstance(params, dict):
        params = dict_values_to_list(params, as_array=True)
    hess_fun = nd.Hessian(lambda p: distribution._negloglik(p, np.array(data)))
    H = hess_fun(params)
    cov_matrix = np.linalg.inv(H)
    var_params = np.diag(cov_matrix)
    return var_params


def calculate_variance_by_boostrap(
    distribution: Any,
    params: Union[List, np.ndarray],
    data: Union[List, np.ndarray],
    n_bootstrap: int = 1000,
    *args,
    **kwargs,
) -> np.ndarray:
    if isinstance(params, dict):
        params = dict_values_to_list(params, as_array=True)
    n = len(data)
    bootstrap_estimates = np.zeros((n_bootstrap, len(params)))

    for i in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        est_params = distribution.fit(sample, *args, **kwargs)
        est_params = dict_values_to_list(est_params, as_array=True)
        bootstrap_estimates[i, :] = est_params

    var_params = np.var(bootstrap_estimates, axis=0)
    return var_params


def calculate_variance(
    distribution: Any,
    params: Union[List, np.ndarray],
    data: Union[List, np.ndarray],
    *args,
    **kwargs,
) -> np.ndarray:
    try:
        var_params = calculate_variance_by_hessian(distribution, params, data)
    except Exception as e:
        print(f"Error calculating variance by Hessian: {e}")
        print("Falling back to bootstrap method.")
        var_params = calculate_variance_by_boostrap(
            distribution, params, data, *args, **kwargs
        )

    if np.all(np.isnan(var_params)):
        print("Hessian method failed, using bootstrap method for variance.")
        var_params = calculate_variance_by_boostrap(
            distribution, params, data, *args, **kwargs
        )
    return var_params


def calculate_bias_by_bootstrap(
    distribution: Any,
    params: Union[List, np.ndarray],
    data: Union[List, np.ndarray],
    n_bootstrap: int = 1000,
    *args,
    **kwargs,
) -> np.ndarray:
    if isinstance(params, dict):
        params = dict_values_to_list(params, as_array=True)
    n = len(data)
    bootstrap_estimates = np.zeros((n_bootstrap, len(params)))

    for i in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        est_params = distribution.fit(sample, *args, **kwargs)
        est_params = dict_values_to_list(est_params, as_array=True)
        bootstrap_estimates[i, :] = est_params

    bias = np.mean(bootstrap_estimates, axis=0) - params
    return bias


def calculate_metrics(
    distribution: Callable,
    data: Union[List, np.ndarray],
    params: Union[List, np.ndarray] = None,
    test: List[str] = ["KS"],
    *args,
    **kwargs,
) -> Dict[str, Any]:
    results = {}
    results["Distribution"] = distribution.get_name
    results["Method"] = distribution.get_method

    params = dict_values_to_list(params, as_array=True)

    nll = distribution._negloglik(params, np.array(data))
    results["log_likelihood"] = float(-nll)

    Bias_params = calculate_bias_by_bootstrap(
        distribution, params, data, n_bootstrap=100, *args, **kwargs
    )
    var_params = calculate_variance(
        distribution, params, np.array(data), *args, **kwargs
    )

    results["bias_params"] = to_float(Bias_params)
    results["var_params"] = to_float(var_params)
    results["MCE"] = to_float(Bias_params**2 + var_params)

    k = len(params)
    n = len(data)
    aic, bic = aic_bic(-nll, k, n)
    results["AIC"] = float(aic)
    results["BIC"] = float(bic)

    if "KS" in test:
        ks_stat, p_value = KS_test(distribution.cdf_func, np.array(data), params)
        results["KS_statistic"] = float(ks_stat)
        results["KS_p_value"] = float(p_value)
    if "AD" in test:
        ad_stat, p_value = AD_test(distribution, np.array(data), params)
        results["AD_statistic"] = float(ad_stat)
        results["AD_p_value"] = float(p_value)
    return results


def aic_bic(ll, k, n) -> Tuple[float, float]:
    """Calcula AIC y BIC a partir de la log-verosimilitud."""
    aic = 2 * k - 2 * ll
    bic = k * log(n) - 2 * ll
    return aic, bic


def KS_test(
    cdf: Callable,
    data: Union[List, np.ndarray],
    params: Union[List, np.ndarray],
) -> Tuple[float, float]:
    """Calcula el estadístico de Kolmogorov-Smirnov para los datos y la CDF dada."""
    d_statistic, p_value = kstest(data, lambda x: cdf(x, params))
    return d_statistic, p_value


def AD_test(
    distribution: Callable,
    data: Union[List, np.ndarray],
    params: Union[List, np.ndarray],
    n_bootstrap: int = 1000,
) -> Tuple[float, float]:
    data_sorted = np.sort(data)
    n = len(data)
    cdf_values = np.array([distribution.cdf_func(x, params) for x in data_sorted])

    # Calcular el estadístico de Anderson-Darling
    i = np.arange(1, n + 1)
    A2 = -n - (1 / n) * np.sum(
        (2 * i - 1) * (np.log(cdf_values) + np.log(1 - cdf_values[::-1]))
    )

    # Bootstrap para p-valor aproximado
    bootstrap_stats = []
    for _ in range(n_bootstrap):
        sim_sample = np.random.choice(data_sorted, size=n, replace=True)
        sim_sorted = np.sort(sim_sample)
        sim_cdf = np.array([distribution.cdf_func(x, params) for x in sim_sorted])
        stat = -n - (1 / n) * np.sum(
            (2 * i - 1) * (np.log(sim_cdf) + np.log(1 - sim_cdf[::-1]))
        )
        bootstrap_stats.append(stat)

    bootstrap_stats = np.array(bootstrap_stats)
    p_value = np.mean(bootstrap_stats >= A2)

    return A2, p_value


import numpy as np
from typing import Dict, Union, Callable


def top_distributions(
    results: Dict[Callable, Dict[str, float]],
    metrics: Union[List[str], Dict[str, float]] = [
        "AIC",
        "BIC",
        "KS_statistic",
        "AD_statistic",
    ],
    top: int = 3,
) -> Dict[Callable, Dict[str, float]]:
    """
    Ordena y devuelve las mejores distribuciones usando múltiples métricas ponderadas.

    Args:
        results: Diccionario {distribución: {métrica: valor}}.
        metrics: Lista de métricas o diccionario {métrica: peso} para ponderación.

    Returns:
        Diccionario con las distribuciones ordenadas por score global descendente.
    """
    # Si es lista, convertimos a diccionario con peso 1
    if isinstance(metrics, list):
        metrics = {m: 1.0 for m in metrics}

    # Extraer nombres de métricas y pesos
    metric_names = list(metrics.keys())
    weights = np.array(list(metrics.values()))

    # Crear matriz de métricas: filas = distribuciones, columnas = métricas
    dist_names = list(results.keys())
    values = np.array(
        [[results[d][m] for m in metric_names] for d in dist_names], dtype=float
    )

    # Normalización global de métricas
    norm_values = np.zeros_like(values)
    for i, m in enumerate(metric_names):
        col = values[:, i]
        # Para métricas donde menor es mejor (AIC, BIC, KS, AD), invertimos
        if "AIC" in m or "BIC" in m or "KS" in m or "AD" in m:
            norm_values[:, i] = 1 - (col - np.min(col)) / (
                np.max(col) - np.min(col) + 1e-12
            )
        else:  # Para métricas donde mayor es mejor
            norm_values[:, i] = (col - np.min(col)) / (
                np.max(col) - np.min(col) + 1e-12
            )

    # Score ponderado
    scores = norm_values @ weights

    # Ordenar distribuciones
    sorted_idx = np.argsort(-scores)
    sorted_distributions = {
        dist_names[i]: results[dist_names[i]] for i in sorted_idx[:top]
    }

    return sorted_distributions
