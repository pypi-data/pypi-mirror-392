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
from scipy.stats import pareto, genpareto, lomax


class Pareto:
    def __init__(self, type: int = 1):
        self.type = type
        self.t = symbols("t")
        self._mode = "Continuous"
        self.x = symbols("x")
        self.x_dummy = symbols("x")
        self.r = symbols("r", real=True, positive=True)
        self.method = None

        if self.type not in [1, 2, 9]:
            raise ValueError("Invalid type. Type must be 1, 2 or 9 (Generalized).")

        self._configure_symbols()
        self._build_functions()

    def _configure_symbols(self):
        if self.type == 1:
            self.x_m, self.a = symbols("x_m alpha", real=True, positive=True)
            self.base_symbols = (self.x_m, self.a)
            self.x_m_dummy = symbols("x_m")
            self.a_dummy = symbols("a")
            self.bounds = [(1e-5, None), (1e-5, None)]

        elif self.type == 2:
            self.a, self.l = symbols("alpha lambda", real=True, positive=True)
            self.base_symbols = (self.a, self.l)
            self.a_dummy = symbols("a")
            self.l_dummy = symbols("l")
            self.bounds = [(1e-5, None), (1e-5, None)]

        elif self.type == 9:
            self.s = symbols("sigma", real=True, positive=True)
            self.s_dummy = symbols("s")
            self.e = symbols("epsilon", real=True)
            self.e_dummy = symbols("e")
            self.base_symbols = (self.s, self.e)
            self.bounds = [(1e-5, None), (None, None)]

    def _build_functions(self):
        if self.type == 1:

            def _pdf_func(x, x_m, a):
                return pareto.pdf(x, a, scale=x_m)
                # return np.vectorize(lambda xv: float(self.raw_pdf(xv, *params)))(x)

            def _sf_func(x, x_m, a):
                return pareto.sf(x, a, scale=x_m)
                # return np.vectorize(lambda xv: float(self.raw_sf(xv, *params)))(x)

            def _cdf_func(x, params):
                x_m, a = params
                return pareto.cdf(x, a, scale=x_m)
                # return np.vectorize(lambda xv: float(self.raw_cdf(xv, *params)))(x)

            self._pdf = _pdf_func
            self._sf = _sf_func
            self._cdf = _cdf_func
        elif self.type == 2:

            def _pdf_func(x, a, l):
                return lomax.pdf(x, c=a, scale=l)

            def _sf_func(x, a, l):
                return lomax.sf(x, c=a, scale=l)

            def _cdf_func(x, params):
                a, l = params
                return lomax.cdf(x, c=a, scale=l)

            self._pdf = _pdf_func
            self._sf = _sf_func
            self._cdf = _cdf_func

        elif self.type == 9:

            def _pdf_func(x, s, e):
                return genpareto.pdf(x, c=1 / e, scale=s)

            def _sf_func(x, s, e):
                return genpareto.sf(x, c=1 / e, scale=s)

            def _cdf_func(x, params):
                s, e = params
                return genpareto.cdf(x, c=1 / e, scale=s)

            self._pdf = _pdf_func
            self._sf = _sf_func
            self._cdf = _cdf_func

    def _pdf_func(self, x, *params):
        return np.vectorize(lambda xv: float(self.raw_pdf(xv, *params)))(x)

    def _sf_func(self, x, *params):
        return np.vectorize(lambda xv: float(self.raw_sf(xv, *params)))(x)

    def _cdf_func(self, x, params):
        return np.vectorize(lambda xv: float(self.raw_cdf(xv, *params)))(x)

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
        self._configure_symbols()
        self._build_functions()

    def __call__(self, *args, **kwds):
        if self.type == 1:
            expr = rf"""
            \textbf{{\Large Pareto distribution}} \quad \textbf{{\Large {self.type}}}\\[6pt]
            \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
            \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
            \text{{Support:}} \quad {latex(Contains(self.x, Interval(self.x_m, oo)))} \\[6pt]
            \text{{Parameters support:}} \\[6pt]
            \quad {latex(Contains(symbols("x_m"), Interval(0, oo)))} \\[6pt]
            \quad {latex(Contains(symbols("alpha"), Interval(0, oo)))} \\[6pt]
            \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
            \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
            \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
            \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
            \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
            \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).simplify())}
            """
        elif self.type == 2:
            expr = rf"""
            \textbf{{\Large Pareto distribution}} \quad \textbf{{\Large {self.type}}}\\[6pt]
            \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
            \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
            \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
            \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
            \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
            \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
            \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
            \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
            \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).simplify())}
            """
        elif self.type == 9:
            expr = rf"""
            \textbf{{\Large Generalized Pareto distribution}} \quad \textbf{{\Large {self.type}}}\\[6pt]
            \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
            \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
            \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
            \text{{Parameters support:}} \\[6pt]
            \quad {latex(Contains(symbols("sigma"), Interval(0, oo)))} \\[6pt]
            \quad {latex(Contains(symbols("epsilon"), sympy.Reals))} \\[6pt]
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
        return "Continuous"

    @property
    def get_name(self) -> str:
        return f"Pareto {self.type}"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        if self.type == 1:
            return (self.a * self.x_m**self.a) / self.x ** (self.a + 1)

        elif self.type == 2:
            return (self.a / self.l) * (1 + self.x / self.l) ** -(self.a + 1)

        elif self.type == 9:
            return (1 / self.s) * (1 + self.e * (self.x / self.s)) ** (-1 / self.e - 1)

    def FGM(self):
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )
        if self.type == 1:
            return (self.a * self.x_m**self.r) / (self.a - self.r)
        elif self.type == 2:
            return self.l**self.r * (
                gamma(self.r + 1) * gamma(self.a - self.r) / gamma(self.a)
            )
        elif self.type == 9:
            return (
                ((self.s**self.r) / (self.e**self.r))
                * (gamma(1 + self.r) * gamma(1 / self.e - self.r))
                / (gamma(1 / self.e + 1))
            )

    def CDF(self):
        return integrate(
            self.PDF(), (self.x, self.x_m if self.type == 1 else 0, self.x)
        ).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "pdf"):
        params = {}
        if self.type == 1:
            if "x_m" in parameters:
                if parameters["x_m"] <= 0:
                    raise ValueError("x_m must be greater than 0")
                params[self.x_m] = self.x_m_dummy
            if "a" in parameters:
                if parameters["a"] <= 0:
                    raise ValueError("a must be greater than 0")
                params[self.a] = self.a_dummy

        elif self.type == 2:
            if parameters["l"] <= 0:
                raise ValueError("l must be greater than 0")
            params[self.l] = self.l_dummy
            if parameters["a"] <= 0:
                raise ValueError("a must be greater than 0")
            params[self.a] = self.a_dummy
        elif self.type == 9:
            if parameters["s"] <= 0:
                raise ValueError("s must be greater than 0")
            params[self.s] = self.s_dummy
            params[self.e] = self.e_dummy
        functions_ = {
            "PDF": self.PDF,
            "FGM": self.FGM,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
        }
        if function.upper() in functions_:
            return functions_[function.upper()]().subs(params).subs(parameters)
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int, mode: str = "integrate"):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")

        if self.type == 1 or self.type == 2:
            E = Piecewise(
                (self.FGM().subs(self.r, n).simplify(), self.a > n),
                (sympy.nan, True),
            )
        elif self.type == 9:
            E = Piecewise(
                (
                    self.FGM().subs(self.r, n).doit().simplify(),
                    self.e < 1 / n,
                ),
                (sympy.nan, True),
            )

        return E.simplify()

    def _negloglik(self, params, data):
        if self.type == 1:
            x_m, alpha = params
            if alpha <= 0 or x_m <= 0:
                return np.inf

            x = np.array(data)
            if np.any(x < x_m):
                return np.inf  # Pareto no está definida para x < x_m

            # log f(x) = log(alpha) + alpha * log(x_m) - (alpha + 1) * log(x)
            loglik = np.sum(
                np.log(alpha) + alpha * np.log(x_m) - (alpha + 1) * np.log(x)
            )
            return -loglik

        elif self.type == 2:
            alpha, lmbda = params
            if alpha <= 0 or lmbda <= 0:
                return np.inf

            x = np.array(data)
            if np.any(x < 0):
                return np.inf  # soporte de Pareto tipo II: x >= 0

            # log f(x) = log(alpha) - log(lambda) - (alpha + 1) * log(1 + x / lambda)
            loglik = np.sum(
                np.log(alpha) - np.log(lmbda) - (alpha + 1) * np.log(1 + x / lmbda)
            )
            return -loglik

        elif self.type == 9:
            s, e = params
            if s <= 0:
                return np.inf

            x = np.array(data)
            if np.any(x < 0):
                return np.inf  # soporte: x >= 0

            # log f(x) = -log(s) + (-1/e - 1) * log(1 + e * x / s)
            loglik = np.sum(-np.log(s) + (-1 / e - 1) * np.log(1 + e * x / s))
            return -loglik

    @singledispatchmethod
    def fit(
        self, data: List, initial: Union[int | Tuple] = None, method: str = "Default"
    ):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters.

        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x > 0 for x in data):
            raise ValueError("All data points must be positive.")

        if self.type == 1:
            n = len(data)
            x_m_hat = np.min(data)  # fijo
            alpha_hat = n / np.sum(np.log(data / x_m_hat))
            self.method = method.upper()
            return {"x_m": float(x_m_hat), "a": float(alpha_hat)}

        elif self.type == 2:
            if initial is None:
                initial = (1, 1)
            minimize_kwargs = {
                "fun": self._negloglik,
                "x0": initial,
                "bounds": [(1e-6, None), (1e-6, None)],
                "args": (np.array(data),),
            }

            if method.upper() != "DEFAULT":
                minimize_kwargs["method"] = method
            self.method = method.upper()
            res = minimize(**minimize_kwargs)

            return {"a": float(res.x[0]), "l": float(res.x[1])}

        elif self.type == 9:
            if initial is None:
                initial = (1, 0.1)
            minimize_kwargs = {
                "fun": self._negloglik,
                "x0": initial,
                "bounds": [(1e-6, None), (None, None)],
                "args": (np.array(data),),
            }

            if method.upper() != "DEFAULT":
                minimize_kwargs["method"] = method
            self.method = method.upper()
            res = minimize(**minimize_kwargs)

            return {"s": float(res.x[0]), "e": float(res.x[1])}

    @fit.register
    def _(
        self, data: tuple, initial: Union[int | Tuple] = None, method: str = "Default"
    ):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed times and event indicators.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            if self.type == 1:
                x_m, a = params
                if a <= 0 or x_m < min(times) or x_m > min(times) + 1e-6:
                    return np.inf

                f = self._pdf(times, x_m, a)
                S = self._sf(times, x_m, a)

            elif self.type == 2:
                a, l = params
                if a <= 0 or l <= 0:
                    return np.inf

                f = self._pdf(times, a, l)
                S = self._sf(times, a, l)
            elif self.type == 9:
                s, e = params
                if s <= 0:
                    return np.inf

                f = self._pdf(times, s, e)
                S = self._sf(times, s, e)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if self.type == 1:
            if initial is None:
                initial = (min(times), 1)
            minimize_kwargs = {
                "fun": negloglik_censored,
                "x0": initial,
                "bounds": [(min(times), min(times) + 1e-6), (1e-6, None)],
                "args": (times, events),
            }

        if self.type == 2:
            if initial is None:
                initial = (1, 1)
            minimize_kwargs = {
                "fun": negloglik_censored,
                "x0": initial,
                "bounds": [(1e-6, None), (1e-6, None)],
                "args": (times, events),
            }

        elif self.type == 9:
            if initial is None:
                initial = (1, 0.1)
            minimize_kwargs = {
                "fun": negloglik_censored,
                "x0": initial,
                "bounds": [(1e-6, None), (None, None)],
                "args": (times, events),
            }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        res = minimize(**minimize_kwargs)

        if self.type == 1:
            return {"x_m": float(res.x[0]), "a": float(res.x[1])}
        elif self.type == 2:
            return {"a": float(res.x[0]), "l": float(res.x[1])}
        elif self.type == 9:
            return {"s": float(res.x[0]), "e": float(res.x[1])}
