from sympy import factorial, nan, Piecewise
from typing import List, Union, Any, Callable
import numpy as np
from scipy.special import logit, expit


def binomial_coefficient(n, x):
    return factorial(n) / (factorial(x) * factorial(n - x))


def is_expr_nan(expr):
    # Método para detectar si expr es nan
    # Aquí usamos expr.equals(nan) que devuelve True si expr es nan
    try:
        return expr.equals(nan)
    except:
        return False


def primera_expr_cond(pw):
    if isinstance(pw, Piecewise):
        return primera_expr_cond(pw.args[0][0]), pw.args[0][1]
    else:
        return pw, True  # True como condición trivial si ya no es Piecewise


def dict_values_to_list(dic, as_array=False):
    vals = list(dic.values())
    return np.array(vals) if as_array else vals


def to_float(val):
    if isinstance(val, (np.floating,)):  # np.float32, np.float64, etc.
        return float(val)
    elif isinstance(val, (tuple, list)):
        return tuple(float(v) if isinstance(v, (np.floating,)) else v for v in val)
    elif isinstance(val, float):
        return val
    else:
        # Intenta convertir directamente
        try:
            return float(val)
        except Exception:
            return val


def make_transforms_from_bounds(bounds):
    fw_funcs, inv_funcs = [], []
    for low, high in bounds:
        if low is None and high is None:
            fw_funcs.append(lambda x: x)
            inv_funcs.append(lambda y: y)
        elif low is not None and high is None:
            L = float(low)
            fw_funcs.append(lambda x, L=L: np.log(np.maximum(x - L, 1e-300)))
            inv_funcs.append(lambda z, L=L: L + np.exp(z))
        elif low is None and high is not None:
            U = float(high)
            fw_funcs.append(lambda x, U=U: -np.log(np.maximum(U - x, 1e-300)))
            inv_funcs.append(lambda z, U=U: U - np.exp(-z))
        else:
            a, b = float(low), float(high)
            fw_funcs.append(lambda x, a=a, b=b: logit((x - a) / (b - a)))
            inv_funcs.append(lambda z, a=a, b=b: a + (b - a) * expit(z))

    def to_internal(theta_nat):
        return np.array(
            [fw(theta_nat[i]) for i, fw in enumerate(fw_funcs)], dtype=float
        )

    def from_internal(theta_int):
        return np.array(
            [inv(theta_int[i]) for i, inv in enumerate(inv_funcs)], dtype=float
        )

    return to_internal, from_internal
