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
from scipy.stats import weibull_min


class Weibull:
    def __init__(self):
        self.b, self.a = symbols("beta alpha", real=True, positive=True)
        self.base_symbols = (self.a, self.b)
        self.bounds = [(1e-6, None), (1e-6, None)]
        self.b_dummy = symbols("b")
        self.a_dummy = symbols("a")
        self.x = symbols("x")
        self.t = symbols("t")
        self._mode = "Continuous"
        self.method = None

        self._build_functions()

    # ------------------------------------------------------------
    # Construcción de funciones (recreadas tras deserialización)
    # ------------------------------------------------------------
    def _build_functions(self):

        self._pdf = self.pdf_func
        self._sf = self.sf_func
        self._cdf = self.cdf_func

    # ------------------------------------------------------------
    # Métodos vectorizados — pickeables y sin lambdas internas
    # ------------------------------------------------------------
    def pdf_func(self, x, a, b):
        return weibull_min.pdf(x, c=a, scale=1 / b)
        # x = np.asarray(x, dtype=float)
        # return np.array([float(self.raw_pdf(xv, a, b)) for xv in x])

    def sf_func(self, x, a, b):
        return weibull_min.sf(x, c=a, scale=1 / b)
        # x = np.asarray(x, dtype=float)
        # return np.array([float(self.raw_sf(xv, a, b)) for xv in x])

    def cdf_func(self, x, params):
        a, b = params
        return weibull_min.cdf(x, c=a, scale=1 / b)

    # ------------------------------------------------------------
    # Serialización segura
    # ------------------------------------------------------------
    def __getstate__(self):
        state = self.__dict__.copy()
        # Eliminar funciones lambdify no serializables
        for key in ("raw_pdf", "raw_sf", "raw_cdf"):
            if key in state:
                del state[key]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Recrear funciones lambdify al cargar el objeto
        self._build_functions()

    def __call__(self, *args, **kwds):

        expr = rf"""
        \textbf{{\Large Weibull distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(symbols("alpha"), Interval(0, oo)))} \\[6pt]
        \quad {latex(Contains(symbols("beta"), Interval(0, oo)))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
        \text{{\tiny To view the PDF, CDF, SF, HF, or the moments, please use the corresponding function separately.}} \\[3pt]
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
        return "Weibull"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            self.b
            * self.a
            * ((self.b * self.x) ** (self.a - 1))
            * exp(-((self.b * self.x) ** self.a))
        )

    def FGM(self):
        integral_expr = integrate(exp(self.t * self.x) * self.PDF(), (self.x, 0, oo))
        return integral_expr.simplify()

    def CDF(self):
        return integrate(self.PDF(), (self.x, 0, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        params = {}
        if "b" in parameters:
            if parameters["b"] < 0:
                raise ValueError("b must be greater than or equal to 0")
            params[self.b] = self.b_dummy
        if "a" in parameters:
            if parameters["a"] < 0:
                raise ValueError("a must be greater than or equal to 0")
            params[self.a] = self.a_dummy

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
        if mode == "integrate":
            E = integrate(pow(self.x, n) * self.PDF(), (self.x, 0, oo)).rewrite(
                sympy.Piecewise
            )
        elif mode == "diff":
            E = limit(diff(self.FGM(), self.t, n).simplify(), self.t, 0)
        return E.simplify()

    def _negloglik(self, params, data):
        a, b = params
        if a <= 0 or b <= 0:
            return np.inf
        x = np.array(data)
        loglik = (
            np.sum((a - 1) * np.log(x) - (b * x) ** a)
            + len(x) * np.log(a)
            + len(x) * a * np.log(b)
        )
        return -loglik

    @singledispatchmethod
    def fit(self, data: List, initial: tuple = None, method: str = "Default"):
        """Estimate the parameters alpha and beta using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.

        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x >= 0 for x in data):
            raise ValueError("All data points must be non-negative.")
        if initial is None:
            initial = (1.0, 1.0)

        minimize_kwargs = {
            "fun": self._negloglik,
            "args": (np.array(data),),
            "bounds": self.bounds,
            "x0": initial,
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        return {"a": float(res.x[0]), "b": float(res.x[1])}

    @fit.register
    def _(self, data: tuple, initial: tuple = None, method: str = "Default"):
        """Estimate the parameters alpha and beta using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed times and event indicators.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            a, b = params
            if a <= 0 or b <= 0:
                return np.inf

            f = self._pdf(times, a, b)
            S = self._sf(times, a, b)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if initial is None:
            initial = (1.0, 1.0)

        res = minimize(
            fun=negloglik_censored,
            x0=initial,
            args=(times, events),
            bounds=self.bounds,
            method=method if method.upper() != "DEFAULT" else "L-BFGS-B",
        )
        return {"a": float(res.x[0]), "b": float(res.x[1])}
