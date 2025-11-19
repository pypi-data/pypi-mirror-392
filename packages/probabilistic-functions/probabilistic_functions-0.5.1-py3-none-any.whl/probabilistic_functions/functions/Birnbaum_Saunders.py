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
from scipy.stats import fatiguelife


class Birnbaum_Saunders:
    def __init__(self):
        self.m, self.a, self.b = symbols("mu alpha beta", real=True, positive=True)
        self.base_symbols = (self.m, self.a, self.b)
        self.a_dummy = symbols("a")
        self.m_dummy = symbols("m")
        self.b_dummy = symbols("b")
        self.x = symbols("x")
        self.t = symbols("t")
        self.r = symbols("r")
        self._mode = "Continuous"
        self.Z = Norm("Z", mean=0, std=1)
        self.method = None
        self._build_functions()

    def _build_functions(self):
        self._pdf = self._pdf_func
        self._sf = self._sf_func
        self._cdf = self._cdf_func

    def _pdf_func(self, x, a, b, m):
        return fatiguelife.pdf(x, c=a, scale=b, loc=m)
        # return self.raw_pdf(x, a, b, m)

    def _sf_func(self, x, a, b, m):
        return fatiguelife.sf(x, c=a, scale=b, loc=m)
        # return self.raw_sf(x, a, b, m)

    def _cdf_func(self, x, params):
        a, b, m = params
        return fatiguelife.cdf(x, c=a, scale=b, loc=m)

    def cdf_func(self, x, params):
        return self._cdf_func(x, params)

    # ================================================================
    # Serialización segura (para usar con joblib, pickle, etc.)
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
        \textbf{{\Large Birnbaum-Saunders distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(symbols("alpha"), Interval(0, oo)))} \\[6pt]
        \quad {latex(Contains(symbols("beta"), Interval(0, oo)))} \\[6pt]
        \quad {latex(Contains(symbols("mu"), Interval(0, oo)))} \\[6pt]
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
        return "Birnbaum-Saunders"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            (sqrt((self.x - self.m) / self.b) + sqrt(self.b / (self.x - self.m)))
            / (2 * self.a * (self.x - self.m))
        ) * density(self.Z)(
            (sqrt((self.x - self.m) / self.b) - sqrt(self.b / (self.x - self.m)))
            / self.a
        )

    def FGM(self):
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )

        return (self.b**self.r) * (
            self.a * self.Z / 2 + sqrt(1 + (self.a * self.Z / 2) ** 2)
        ) ** (2 * self.r)

    def CDF(self):
        return cdf(self.Z)((sqrt(self.x) - sqrt(1 / self.x)) / (self.a))

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        params = {}
        if "a" in parameters:
            if parameters["a"] < 0:
                raise ValueError("a must be greater than 0")
            params[self.a] = self.a_dummy
        if "b" in parameters:
            if parameters["b"] < 0:
                raise ValueError("b must be greater than 0")
            params[self.b] = self.b_dummy

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
            raise ValueError("n must be >= 1")
        return (
            Expectation(Birnbaum_Saunders().FGM().subs(Birnbaum_Saunders().r, n))
            .factor()
            .doit()
        )

    def _negloglik(self, params, data):
        a, b, m = params
        if a <= 0 or b <= 0:
            return np.inf

        x = np.array(data)
        y = (np.sqrt((x - m) / b) - np.sqrt(b / (x - m))) / a

        log_phi = -0.5 * y**2 - 0.5 * np.log(2 * np.pi)
        log_factor = np.log(np.sqrt((x - m) / b) + np.sqrt(b / (x - m))) - np.log(
            2 * a * (x - m)
        )

        loglik = np.sum(log_factor + log_phi)
        return -loglik

    @singledispatchmethod
    def fit(
        self,
        data: List,
        initial: tuple = None,
        method: str = "Default",
    ):
        """Estimate the parameters alpha and beta using Maximum Likelihood Estimation (MLE).
        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (alpha, beta).
            tol (float, optional): Tolerance for the numerical solver. Defaults to None.
            verify (bool, optional): Whether to verify the solution. Defaults to False.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x > 0 for x in data):
            raise ValueError("All data points must be positive.")

        if initial is None:
            mean = np.mean(data)
            var = np.var(data, ddof=1)

            # Inicial para m: un poco menor que el mínimo de los datos
            m0 = np.min(data) - 1e-6
            # Inicial para a (forma)
            alpha0 = max(1e-6, min(5.0, np.sqrt(var) / (mean - m0)))
            # Inicial para b (escala)
            beta0 = max(1e-6, (mean - m0) / (1.0 + 0.5 * alpha0**2))
            initial = (alpha0, beta0, m0)
        minimize_kwargs = {
            "fun": self._negloglik,
            "x0": initial,
            "bounds": [(1e-6, None), (1e-6, None), (None, min(data) - 1e-6)],
            "args": (np.array(data),),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method

        self.method = method.upper()
        res = minimize(**minimize_kwargs)  # parámetros > 0

        return {"a": res.x[0].item(), "b": res.x[1].item(), "m": res.x[2].item()}

    @fit.register
    def _(self, data: tuple, initial: tuple = None, method: str = "Default"):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE)
        for censored data.
        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters.
            method (str): Optimization method to use.

        Returns:
            dict: A dictionary containing the estimated parameters.
        """

        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            a, b, m = params
            if a <= 0 or b <= 0:
                return np.inf

            f = self._pdf(times, a, b, m)
            S = self._sf(times, a, b, m)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if initial is None:
            mean = np.mean(times)
            var = np.var(times, ddof=1)

            # Inicial para m: un poco menor que el mínimo de los datos
            m0 = np.min(times) - 1e-6
            # Inicial para a (forma)
            alpha0 = max(1e-6, min(5.0, np.sqrt(var) / (mean - m0)))
            # Inicial para b (escala)
            beta0 = max(1e-6, (mean - m0) / (1.0 + 0.5 * alpha0**2))
            initial = (alpha0, beta0, m0)

        minimize_kwargs = {
            "fun": negloglik_censored,
            "x0": initial,
            "bounds": [(1e-6, None), (1e-6, None), (None, min(times) - 1e-6)],
            "args": (times, events),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method

        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        return {"a": res.x[0].item(), "b": res.x[1].item(), "m": res.x[2].item()}
