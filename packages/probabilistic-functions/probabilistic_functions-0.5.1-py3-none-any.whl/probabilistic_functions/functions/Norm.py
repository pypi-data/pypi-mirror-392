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
from scipy.stats import norm as normal_dist


class Normal:
    def __init__(self):
        self.x = symbols("x")
        self.v = symbols("sigma^2", real=True, positive=True)
        self.v_dummy = symbols("v")
        self.m = symbols("mu", real=True)
        self.m_dummy = symbols("m")
        self.t = symbols("t")

        self._mode = "Continuous"
        self.method = None
        self.bounds = [(None, None), (1e-6, None)]
        self.base_symbols = [self.m, self.v]

        self._build_functions()

    # ------------------------------------------------------------
    # Construcción de funciones (recreadas tras deserialización)
    # ------------------------------------------------------------
    def _build_functions(self):
        self._pdf = self.pdf_func
        self._sf = self.sf_func
        self._cdf = self.cdf_func

    # ------------------------------------------------------------
    # Funciones públicas pickeables (sin lambdas internas)
    # ------------------------------------------------------------
    def pdf_func(self, x, m, v):
        return normal_dist.pdf(x, loc=m, scale=np.sqrt(v))

    def sf_func(self, x, m, v):
        return normal_dist.sf(x, loc=m, scale=np.sqrt(v))

    def cdf_func(self, x, params):
        m, v = params
        return normal_dist.cdf(x, loc=m, scale=np.sqrt(v))

    # ------------------------------------------------------------
    # Soporte para serialización con pickle/joblib
    # ------------------------------------------------------------
    def __getstate__(self):
        state = self.__dict__.copy()
        # Eliminar objetos lambdify no serializables
        for key in ("raw_pdf", "raw_sf", "raw_cdf"):
            if key in state:
                del state[key]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Recrear funciones lambdify al deserializar
        self._build_functions()

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Normal distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, sympy.Reals))} \\[6pt]
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
        return "Normal"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (1 / sqrt(2 * pi * self.v)) * exp(
            (-((self.x - self.m) ** 2)) / (2 * (self.v))
        )

    def FGM(self):
        return exp(self.m * self.t + 0.5 * (self.v) * (self.t**2))

    def CDF(self):
        return integrate(self.PDF(), (self.x, -oo, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        if "v" in parameters:
            if parameters["v"] < 0:
                raise ValueError("v must be greater than 0")

        functions_ = {
            "PDF": self.PDF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }

        if function.upper() in functions_:
            return (
                functions_[function.upper()]()
                .subs({self.v: self.v_dummy, self.m: self.m_dummy})
                .subs(parameters)
            )
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int, mode: str = "integrate"):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        if mode == "integrate":
            E = integrate(pow(self.x, n) * self.PDF(), (self.x, -oo, oo)).rewrite(
                sympy.Piecewise
            )
        elif mode == "diff":
            E = limit(diff(self.FGM(), self.t, n).simplify(), self.t, 0)
        return E.simplify()

    def _negloglik(self, params, data):
        mu, sigma2 = params
        if sigma2 <= 0:
            return np.inf
        x = np.array(data)
        n = len(x)
        loglik = (
            -0.5 * n * np.log(2 * np.pi)
            - 0.5 * n * np.log(sigma2)
            - np.sum((x - mu) ** 2) / (2 * sigma2)
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
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in data):
            raise ValueError("All data points must be real numbers.")

        self.method = "MLE"
        return {"m": float(np.mean(data).item()), "v": float(np.var(data).item())}

    @fit.register
    def _(self, data: tuple, method: str = "L-BFGS-B"):
        """
        Estimate the parameters mu and sigma^2 using Maximum Likelihood Estimation (MLE).

        Args:
            times (list): A list of observed data points.
            events (list, optional): A list indicating if the event was observed (1) or censored (0). Defaults to None.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            mu, sigma2 = params
            if sigma2 <= 0:
                return np.inf

            f = self._pdf(times, mu, sigma2)
            S = self._sf(times, mu, sigma2)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        initial_mu = np.mean(times)
        initial_sigma2 = np.var(times)

        res = minimize(
            fun=negloglik_censored,
            x0=np.array([initial_mu, initial_sigma2]),
            args=(times, events),
            bounds=[(None, None), (1e-6, None)],
            method=method if method.upper() != "L-BFGS-B" else "L-BFGS-B",
        )
        return {"m": res.x[0], "v": res.x[1]}
