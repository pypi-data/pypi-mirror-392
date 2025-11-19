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
from scipy.stats import burr


class Burr:
    def __init__(self):
        self.x = symbols("x")
        self.t = symbols("t")
        self._mode = "Continuous"
        self.a, self.c, self.l = symbols("alpha c lambda", real=True, positive=True)
        self.base_symbols = (self.a, self.c, self.l)
        self.bounds = [(1e-5, None), (1e-5, None), (1e-5, None)]
        self.c_dummy = symbols("c")
        self.a_dummy = symbols("a")
        self.l_dummy = symbols("l")
        self.method = None
        self._build_functions()

    def _build_functions(self):

        self._pdf = self._pdf_func
        self._sf = self._sf_func
        self._cdf = self._cdf_func

    def _pdf_func(self, x, a, c, l):
        return burr.pdf(x, c, a, scale=l)
        # return self.raw_pdf(x, a, c, l)

    def _sf_func(self, x, a, c, l):
        return burr.sf(x, c, a, scale=l)
        # return self.raw_sf(x, a, c, l)

    def _cdf_func(self, x, params):
        a, c, l = params
        return burr.cdf(x, c, a, scale=l)

    def cdf_func(self, x, params):
        return self._cdf_func(x, params)

    # ================================================================
    # Serialización segura
    # ================================================================
    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ("raw_pdf", "raw_sf", "raw_cdf"):
            if key in state:
                del state[key]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._build_functions()

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Burr distribution Type}} \quad {7} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(symbols("alpha"), Interval(0, oo)))} \\[6pt]
        \quad {latex(Contains(symbols("c"), Interval(0, oo)))}
        \quad {latex(Contains(symbols("lambda"), Interval(0, oo)))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
        \text{{Cumulative distribution:}} \quad {latex(self.CDF())} \\[6pt]
        \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
        \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
        \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
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
        return f"Burr 7"

    @property
    def get_method(self):
        return self.method

    def PDF(self):
        return (
            ((self.a * self.c) / self.l)
            * (self.x / self.l) ** (self.a - 1)
            * (1 + (self.x / self.l) ** self.a) ** (-self.c - 1)
        )

    def CDF(self):
        return integrate(self.PDF(), (self.x, 0, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def FGM(self):
        self.r = symbols("r")
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )
        return self.l**self.r * (
            (gamma(1 + (self.r / self.a)) * gamma(self.c - self.r / self.a))
            / (gamma(self.c))
        )

    def replace(self, parameters, function: str = "pdf"):
        params = {}
        if parameters["c"] < 0:
            raise ValueError("c must be greater than 0")
        if parameters["l"] < 0:
            raise ValueError("l must be greater than 0")
        if parameters["a"] < 0:
            raise ValueError("a must be greater than 0")

        params = {
            self.c: self.c_dummy,
            self.l: self.l_dummy,
            self.a: self.a_dummy,
        }
        functions_ = {
            "PDF": self.PDF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }

        if function.upper() in functions_:
            return functions_[function.upper()]().subs(params).subs(parameters)
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")

        expr = self.FGM().subs(self.r, n).simplify()
        return E(expr).simplify()

    def _negloglik(self, params, data):
        a, c, l = params
        if a <= 0 or c <= 0 or l <= 0:
            return np.inf
        n = len(data)
        term1 = n * (np.log(a) + np.log(c) - np.log(l))
        term2 = (a - 1) * np.sum(np.log(data / l))
        term3 = -(c + 1) * np.sum(np.log(1 + (data / l) ** a))
        return -(term1 + term2 + term3)

    @singledispatchmethod
    def fit(self, data: List, initial: Tuple = (1, 1, 1), method: str = "Default"):
        """Estimate the parameters alpha, c and lambda using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (alpha, c, lambda).
            method (str): Optimization method to use (e.g., 'Nelder-Mead', 'BFGS'). If 'Default', uses default method of scipy's minimize.

        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x > 0 for x in data):
            raise ValueError("All data points must be positive.")

        if initial is None:
            initial = (1.5, 1.5, np.mean(data))
        minimize_kwargs = {
            "fun": self._negloglik,
            "x0": initial,
            "bounds": [(1e-6, None), (1e-6, None), (1e-6, None)],
            "args": (np.array(data),),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method

        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        return {"a": float(res.x[0]), "c": float(res.x[1]), "l": float(res.x[2])}

    @fit.register
    def _(self, data: tuple, initial: Tuple = (1, 1, 1), method: str = "Default"):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed times and event indicators.
            initial (Tuple): Initial guess for the parameters (alpha, c, lambda).
            method (str): Optimization method to use.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            a, c, l = params
            if a <= 0 or c <= 0 or l <= 0:
                return np.inf

            f = self._pdf(times, a, c, l)
            S = self._sf(times, a, c, l)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if initial is None:
            initial = (1.5, 1.5, np.mean(times))
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
        return {"a": float(res.x[0]), "c": float(res.x[1]), "l": float(res.x[2])}
