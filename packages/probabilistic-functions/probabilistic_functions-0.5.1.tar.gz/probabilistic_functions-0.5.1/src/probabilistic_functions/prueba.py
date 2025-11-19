from functools import singledispatchmethod
from sympy import (
    symbols,
    sympify,
    lambdify,
    factorial,
    simplify,
    factor,
    UnevaluatedExpr,
)
from scipy.special import gammaincc
from scipy.optimize import minimize
import numpy as np
import warnings
from scipy.special import gamma as gamma_func
from sympy import pretty
from scipy.special import gammaln, comb
from sympy import (
    exp,
    expand,
    Add,
    factorial2,
    Integer,
    Poly,
    Symbol,
    sqrt,
    pi,
    latex,
    integrate,
    S,
    summation,
    diff,
    limit,
    Max,
    Min,
    binomial,
    gamma,
    log,
    uppergamma,
    erf,
    Piecewise,
    floor,
    Contains,
    FiniteSet,
    Naturals,
    Interval,
    Range,
    solve,
    nsolve,
    Eq,
)
from sympy.stats import Normal as Norm
from sympy.stats import density, cdf
from sympy.stats import E, Expectation
import math
from scipy.special import gamma as gamma_scipy

from sympy import beta as beta_func

from sympy import oo
from sympy import pprint
import sympy
import matplotlib.pyplot as plt
import math
import numpy as np
from itertools import product
from typing import Callable, Dict, List, Tuple, Optional, Union
from IPython.display import display, Math

# ==============================================================
# Funciones globales (todas picklables)
# ==============================================================


def lindley1_pdf_func(raw_pdf, x_val, p):
    return raw_pdf(x_val, p)


def lindley1_sf_func(raw_sf, x_val, p):
    return raw_sf(x_val, p)


def lindley1_cdf_func(raw_cdf, x_val, params):
    return raw_cdf(x_val, *params)


def lindley2_pdf_func(raw_pdf, x_val, p, a, y_):
    x_val = np.asarray(x_val, dtype=float)
    vals = [float(raw_pdf(xv, p, a, y_)) for xv in x_val]
    return np.array(vals)


def lindley2_sf_func(raw_sf, x_val, p, a, y_):
    x_val = np.asarray(x_val, dtype=float)
    vals = [float(raw_sf(xv, p, a, y_)) for xv in x_val]
    return np.array(vals)


def lindley2_cdf_func(obj, x_val, params):
    x_val = np.asarray(x_val, dtype=float)
    vals = [float(obj.lindley2_cdf(xv, *params)) for xv in x_val]
    return np.array(vals)


# Envolturas simples que devuelven referencias directas
def build_lindley1_pdf(raw_pdf):
    def pdf_func(x_val, p):
        return lindley1_pdf_func(raw_pdf, x_val, p)

    return pdf_func


def build_lindley1_sf(raw_sf):
    def sf_func(x_val, p):
        return lindley1_sf_func(raw_sf, x_val, p)

    return sf_func


def build_lindley1_cdf(raw_cdf):
    def cdf_func(x_val, params):
        return lindley1_cdf_func(raw_cdf, x_val, params)

    return cdf_func


def build_lindley2_pdf(raw_pdf):
    def pdf_func(x_val, p, a, y_):
        return lindley2_pdf_func(raw_pdf, x_val, p, a, y_)

    return pdf_func


def build_lindley2_sf(raw_sf):
    def sf_func(x_val, p, a, y_):
        return lindley2_sf_func(raw_sf, x_val, p, a, y_)

    return sf_func


def build_lindley2_cdf(obj):
    def cdf_func(x_val, params):
        return lindley2_cdf_func(obj, x_val, params)

    return cdf_func


# ==============================================================


class Lindley:
    def __init__(self, type: int = 1):
        self.type = type
        if self.type not in [1, 2]:
            raise ValueError("Invalid type. Type only available 1 or 2")

        self.p = symbols("theta", real=True, positive=True)
        self.p_dummy = symbols("p")
        self.t = symbols("t")
        self.x = symbols("x")

        self._mode = "Continuous"
        self.method = None

        if self.type == 1:
            self.base_symbols = [self.p]
            self.bounds = [(1e-5, None)]
        else:
            self.a = symbols("alpha", real=True, positive=True)
            self.a_dummy = symbols("a")
            self.y = symbols("gamma", real=True, positive=True)
            self.y_dummy = symbols("y")
            self.base_symbols = (self.p, self.a, self.y_dummy)
            self.bounds = [(1e-5, None), (1e-5, None), (1e-5, None)]

        self._build_functions()

    def _build_functions(self):
        if self.type == 1:
            raw_pdf = lambdify(
                (self.x, self.p), self.PDF(), modules=["numpy", "mpmath"]
            )
            raw_sf = lambdify((self.x, self.p), self.SF(), modules=["numpy", "mpmath"])
            raw_cdf = lambdify(
                (self.x, self.p), self.CDF(), modules=["numpy", "mpmath"]
            )

            self._pdf = build_lindley1_pdf(raw_pdf)
            self._sf = build_lindley1_sf(raw_sf)
            self._cdf = build_lindley1_cdf(raw_cdf)

        else:
            expr_pdf = self.PDF().subs(self.y, self.y_dummy)
            raw_pdf = lambdify(
                (self.x, self.p, self.a, self.y_dummy),
                expr_pdf,
                modules=["numpy", "mpmath"],
            )
            expr_sf = self.SF().subs(self.y, self.y_dummy)
            raw_sf = lambdify(
                (self.x, self.p, self.a, self.y_dummy),
                expr_sf,
                modules=["numpy", "mpmath"],
            )

            self._pdf = build_lindley2_pdf(raw_pdf)
            self._sf = build_lindley2_sf(raw_sf)
            self._cdf = build_lindley2_cdf(self)

    def lindley2_cdf(self, x, alpha, theta, gamma_param):
        """
        CDF de la distribución Lindley tipo 2.
        """
        x = np.asarray(x, dtype=float)
        if np.any(x < 0):
            raise ValueError("x debe ser >= 0")
        if alpha <= 0 or theta <= 0 or gamma_param <= 0:
            raise ValueError("alpha, theta y gamma_param deben ser > 0")

        z = theta * x
        A = gammaincc(alpha, z)  # Q(alpha, z)
        B = gammaincc(alpha + 1, z)  # Q(alpha+1, z)
        denom = gamma_param + theta
        F = 1.0 - (theta * A + gamma_param * B) / denom
        return F

    def cdf_func(self, x, params):
        return self._cdf(x, params)

    def __call__(self, *args, **kwds):
        if self.type == 1:
            expr = rf"""
            \textbf{{\Large Lindley distribution}} \quad \textbf{{\Large {self.type}}}\\[6pt]
            \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
            \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
            \text{{Parameters support:}} \\[6pt]
            \quad {latex(Contains(symbols("theta"), Interval(0, oo)))} \\[6pt]
            \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
            \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
            \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
            \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
            \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
            \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
            \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).factor())}
            """
        elif self.type == 2:
            expr = rf"""
            \textbf{{\Large Lindley distribution}} \quad \textbf{{\Large {self.type}}}\\[6pt]
            \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
            \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
            \text{{Parameters support:}} \\[6pt]
            \quad {latex(Contains(symbols('alpha'), Interval(0, oo)))} \\[6pt] 
            \quad {latex(Contains(symbols('gamma'), Interval(0, oo)))} \\[6pt]
            \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
            \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
            \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
            \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
            \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
            \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
            \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).factor())}
            """
        display(Math(expr))

    @property
    def is_fuction(self):
        return True

    @property
    def get_mode(self):
        return self._mode

    @property
    def get_name(self) -> str:
        return f"Lindley {self.type}"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        if self.type == 1:
            return (self.p**2 / (1 + self.p)) * exp(-self.p * self.x) * (1 + self.x)
        elif self.type == 2:
            return (
                self.p**2
                * (self.p * self.x) ** (self.a - 1)
                * (self.a + self.y * self.x)
                * exp(-self.p * self.x)
            ) / ((self.y + self.p) * gamma(self.a + 1))

    def FGM(self):
        if self.type == 1:
            return (self.p**2 / (self.p + 1)) * (
                1 / (self.p - self.t) + 1 / (self.p - self.t) ** 2
            )
        elif self.type == 2:
            return (self.p ** (self.a + 1) / (self.y + self.p)) * (
                1 / (self.p - self.t) ** self.a
                + self.y / (self.p - self.t) ** (self.a + 1)
            )

    def CDF(self):
        return integrate(self.PDF(), (self.x, 0, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        params = {}
        if "p" in parameters:
            if parameters["p"] < 0:
                raise ValueError("p must be greater than 0")
            params[self.p] = self.p_dummy
        if self.type == 2:
            if parameters["a"] < 0:
                raise ValueError("a must be greater than 0")
            if parameters["y"] < 0:
                raise ValueError("y must be greater than 0")
            params[self.a] = self.a_dummy
            params[self.y] = self.y_dummy
        function_ = {
            "PDF": self.PDF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }
        if function.upper() in function_:
            return function_[function.upper()]().subs(params).subs(parameters)
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int, mode: str = "integrate"):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        if mode == "integrate":
            E = integrate(pow(self.x, n) * self.PDF(), (self.x, 0, oo)).rewrite(
                sympy.Piecewise
            )
        elif mode == "diff":
            E = limit(diff(self.FGM(), self.t, n).simplify(), self.t, 0)
        return E.simplify()

    def _negloglik(self, params, data):
        if self.type == 1:
            p = params
            if p <= 0:
                return np.inf
            n = len(data)
            term1 = n * (2 * np.log(p) - np.log(1 + p))
            term2 = -p * np.sum(data)
            term3 = np.sum(np.log(1 + data))
            return -(term1 + term2 + term3)
        elif self.type == 2:
            p, a, y = params
            if p <= 0 or a <= 0 or y <= 0:
                return np.inf
            data = np.array(data)
            n = len(data)
            term1 = n * (2 * np.log(p) - np.log(y + p) - gammaln(a + 1))
            term2 = (a - 1) * np.sum(np.log(p * data))
            term3 = np.sum(np.log(a + y * data))
            term4 = -p * np.sum(data)
            return -(term1 + term2 + term3 + term4)

    @singledispatchmethod
    def fit(self, data: List, initial: Tuple = None, method: str = "MLE"):
        """Estimate the parameters p and a using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (p, a).
            method (str): Optimization method to use (e.g., 'Nelder-Mead', 'BFGS', 'MLE'). If 'Default', uses default method of scipy's minimize.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x >= 0 for x in data):
            raise ValueError("All data points must be non-negative.")

        if method.upper() == "MLE":
            if self.type == 1:
                n = len(data)
                S = sum(data)
                num = -(S - n) + np.sqrt((S - n) ** 2 + 8 * n * S)
                self.method = method.upper()
                return {"p": float(num / (2 * S))}
            elif self.type == 2:
                raise ValueError("No analytical solution for type 2 with MLE method")

        bounds = [(1e-6, None)]
        if self.type == 2:
            if initial is None:
                sample_mean = np.mean(data)
                sample_var = np.var(data)
                initial = [1 / sample_mean, 1.0, 0.5 / sample_mean]  # heurística
            bounds = [(1e-6, None), (1e-6, None), (1e-6, None)]
        else:
            initial = initial if initial else (1,)

        minimize_kwargs = {
            "fun": (self._negloglik),
            "x0": initial,
            "bounds": bounds,
            "args": (np.array(data),),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method

        self.method = method.upper()
        res = minimize(**minimize_kwargs)

        if self.type == 1:
            return {"p": float(res.x[0])}
        elif self.type == 2:
            return {"p": float(res.x[0]), "a": float(res.x[1]), "y": float(res.x[2])}

    @fit.register
    def _(self, data: tuple, initial: Tuple = None, method: str = "Default"):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed times and event indicators.
            initial (Tuple): Initial guess for the parameters.
            method (str): Optimization method to use.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            if self.type == 1:
                p = params
                if p <= 0:
                    return np.inf
                f = self._pdf(times, p)
                S = self._sf(times, p)
            elif self.type == 2:
                p, a, y = params
                if p <= 0 or a <= 0 or y <= 0:
                    return np.inf
                f = self._pdf(times, p, a, y)
                S = self._sf(times, p, a, y)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if self.type == 2:
            if initial is None:
                sample_mean = np.mean(times)
                sample_var = np.var(times)
                initial = [1 / sample_mean, 1.0, 0.5 / sample_mean]  # heurística
        else:
            initial = initial if initial else (1,)

        minimize_kwargs = {
            "fun": negloglik_censored,
            "x0": initial,
            "bounds": self.bounds,
            "args": (times, events),
        }
        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        if self.type == 1:
            return {"p": float(res.x[0])}
        elif self.type == 2:
            return {"p": float(res.x[0]), "a": float(res.x[1]), "y": float(res.x[2])}
