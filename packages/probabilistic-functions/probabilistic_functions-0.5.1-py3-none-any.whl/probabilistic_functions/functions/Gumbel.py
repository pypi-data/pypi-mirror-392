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
from scipy.stats import gumbel_r


class Gumbel:
    def __init__(self):
        self.m, self.b = symbols("mu", real=True), symbols(
            "beta", real=True, positive=True
        )
        self.base_symbols = (self.m, self.b)
        self.bounds = [(None, None), (1e-5, None)]
        self.m_dummy = symbols("m")
        self.b_dummy = symbols("b")
        self.x = symbols("x")
        self.t = symbols("t")
        self._mode = "Continuous"
        self.method = None

        self._build_functions()

    def _build_functions(self):
        self._pdf = self._pdf_func
        self._sf = self._sf_func
        self._cdf = self._cdf_func

    def _pdf_func(self, x, m, b):
        return gumbel_r.pdf(x, loc=m, scale=b)
        # return np.vectorize(lambda xv: float(self.raw_pdf(xv, m, b)))(x)

    def _sf_func(self, x, m, b):
        return gumbel_r.sf(x, loc=m, scale=b)
        # return np.vectorize(lambda xv: float(self.raw_sf(xv, m, b)))(x)

    def _cdf_func(self, x, params):
        m, b = params
        return gumbel_r.cdf(x, loc=m, scale=b)

    def cdf_func(self, x, params):
        return self._cdf_func(x, params)

    # ------------------------------------------------------------------
    # Soporte para serialización
    # ------------------------------------------------------------------
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
        \textbf{{\Large Gumbel distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, sympy.Reals))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(symbols("mu"), sympy.Reals))} \\[6pt]
        \quad {latex(Contains(symbols("beta"), Interval(0, oo)))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
        \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
        \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
        \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
        \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
        \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
        \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).simplify())}
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
        return "Gumbel"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            (1 / self.b)
            * exp((self.x - self.m) / self.b)
            * exp(-exp((self.x - self.m) / self.b))
        )

    def FGM(self):
        return gamma(1 - self.b * self.t) * exp(self.m * self.t)

    def CDF(self):
        return integrate(self.PDF(), (self.x, -oo, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        params = {}
        if "b" in parameters:
            if parameters["b"] < 0:
                raise ValueError("b must be greater than 0")
            params[self.b] = self.b_dummy
        if "m" in parameters:
            params[self.m] = self.m_dummy

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

    def calculate_moments(self, n: int, mode: str = "diff"):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        if mode == "integrate":
            # z = (x-m)/b
            self.z = symbols("z", real=True)
            new_fdp = (self.b * self.z + self.m) ** n * exp(self.z - exp(self.z))
            E = integrate(new_fdp, (self.z, -oo, oo), meijerg=True)
        elif mode == "diff":
            E = limit(diff(self.FGM(), self.t, n).simplify(), self.t, 0)
        return E.simplify()

    def _negloglik(self, params, data):
        m, b = params
        if b <= 0:
            return np.inf

        x = np.array(data)
        z = (x - m) / b
        loglik = np.sum(-np.log(b) + z - np.exp(z))  # log f(x) = -log(b) + z - exp(z)
        return -loglik

    @singledispatchmethod
    def fit(self, data: List, initial: Tuple = None, method: str = "Default"):
        """Estimate the parameters mu and beta using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            method (str): Optimization method to use (e.g., 'Nelder-Mead', 'BFGS'). If 'Default', uses default method of scipy's minimize.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in data):
            raise ValueError("All data points must be real numbers.")

        if initial is None:
            GAMMA_EULER = 0.5772156649015329
            SQ6_OVER_PI = np.sqrt(6) / np.pi
            mean = np.mean(data)
            std = np.std(data, ddof=1)
            beta0 = std / SQ6_OVER_PI
            mu0 = mean - GAMMA_EULER * beta0
            initial = (float(mu0), float(beta0))

        minimize_kwargs = {
            "fun": self._negloglik,
            "x0": initial,
            "bounds": [(None, None), (1e-6, None)],
            "args": (np.array(data),),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method

        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        return {"m": float(res.x[0]), "b": float(res.x[1])}

    @fit.register
    def _(self, data: tuple, initial: Tuple = None, method: str = "Default"):
        """Estimate the parameters mu and beta using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed times and event indicators.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            m, b = params
            if b <= 0:
                return np.inf

            f = self._pdf(times, m, b)
            S = self._sf(times, m, b)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if initial is None:
            GAMMA_EULER = 0.5772156649015329
            SQ6_OVER_PI = np.sqrt(6) / np.pi
            mean = np.mean(times)
            std = np.std(times, ddof=1)
            beta0 = std / SQ6_OVER_PI
            mu0 = mean - GAMMA_EULER * beta0
            initial = (float(mu0), float(beta0))

        minimize_kwargs = {
            "fun": negloglik_censored,
            "x0": initial,
            "bounds": [(None, None), (1e-6, None)],
            "args": (times, events),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method

        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        return {"m": float(res.x[0]), "b": float(res.x[1])}
