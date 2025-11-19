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
from scipy.stats import lognorm
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


class LogNormal:
    def __init__(self):
        self.m, self.v = symbols("mu sigma^2", real=True)
        self.base_symbols = (self.m, self.v)
        self.bounds = [(None, None), (1e-5, None)]
        self.m_dummy = symbols("m")
        self.v_dummy = symbols("v")
        self.x, self.t = symbols("x t")
        self.r = symbols("r")
        self._mode = "Continuous"
        self.method = None

        self._build_functions()

    def _build_functions(self):
        self._pdf = self._pdf_func
        self._sf = self._sf_func
        self._cdf = self._cdf_func

    def _pdf_func(self, x, m, v):
        return lognorm.pdf(x, s=v, scale=np.exp(m))
        # return np.vectorize(lambda xv: float(self.raw_pdf(xv, m, v)))(x)

    def _sf_func(self, x, m, v):
        return lognorm.sf(x, s=v, scale=np.exp(m))
        # return np.vectorize(lambda xv: float(self.raw_sf(xv, m, v)))(x)

    def _cdf_func(self, x, params):
        m, v = params
        return lognorm.cdf(x, s=v, scale=np.exp(m))

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
        \textbf{{\Large Log-Normal distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(symbols("mu"), sympy.Reals))} \\[6pt]
        \quad {latex(Contains(symbols("sigma^2"), Interval(0, oo)))} \\[6pt]
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
        return "LogNormal"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (1 / (self.x * sqrt(2 * pi * self.v))) * exp(
            -((log(self.x) - self.m) ** 2) / (2 * self.v)
        )

    def FGM(self):
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )
        return exp(self.r * self.m + ((self.r**2 * self.v) / (2)))

    def CDF(self):
        return 0.5 * (1 + erf((log(self.x) - self.m) / (sqrt(2 * self.v))))

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        params = {}
        if "v" in parameters:
            if parameters["v"] < 0:
                raise ValueError("v must be greater than 0")
            params[self.v] = self.v_dummy
        if "m" in parameters:
            params[self.m] = self.m_dummy
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
        return self.FGM().subs(self.r, n).simplify()

    def _negloglik(self, params, data):
        m, v = params
        if v <= 0:
            return np.inf
        x = np.array(data)
        loglik = np.sum(
            -np.log(x) - 0.5 * np.log(2 * np.pi * v) - ((np.log(x) - m) ** 2) / (2 * v)
        )
        return -loglik

    @singledispatchmethod
    def fit(self, data: List):
        """Estimate the parameters mu and sigma^2 using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.

        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x > 0 for x in data):
            raise ValueError("All data points must be positive.")

        logs = np.log(data)
        m = np.mean(logs)
        v = np.mean((logs - m) ** 2)
        self.method = "MLE"
        return {"m": float(m), "v": float(v)}

    @fit.register
    def _(self, data: tuple):
        """Estimate the parameters mu and sigma^2 using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed times and event indicators.

        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            m, v = params
            if v <= 0:
                return np.inf

            f = self._pdf(times, m, v)
            S = self._sf(times, m, v)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        res = minimize(
            fun=negloglik_censored,
            x0=[0, 1],
            args=(times, events),
            bounds=self.bounds,
        )

        return {"m": res.x[0], "v": res.x[1]}
