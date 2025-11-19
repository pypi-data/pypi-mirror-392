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
from scipy.stats import invweibull


class Inverse_Weibull:
    def __init__(self):
        self.a, self.b = symbols("alpha beta", real=True, positive=True)
        self.base_symbols = (self.a, self.b)
        self.bounds = [(1e-5, None), (1e-5, None)]
        self.a_dummy = symbols("a")
        self.b_dummy = symbols("b")
        self.x = symbols("x")
        self.r = symbols("r")
        self._mode = "Continuous"
        self.method = None

        self._build_functions()

    def _build_functions(self):
        self._pdf = self._pdf_func
        self._sf = self._sf_func
        self._cdf = self._cdf_func

    def _pdf_func(self, x, a, b):
        return invweibull.pdf(x, a, scale=b)
        # return np.vectorize(lambda xv: float(self.raw_pdf(xv, a, b)))(x)

    def _sf_func(self, x, a, b):
        return invweibull.sf(x, a, scale=b)
        # return np.vectorize(lambda xv: float(self.raw_sf(xv, a, b)))(x)

    def _cdf_func(self, x, params):
        a, b = params
        return invweibull.cdf(x, a, scale=b)

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
        pass

    @property
    def is_fuction(self):
        return True

    @property
    def get_mode(self):
        return self._mode

    @property
    def get_name(self) -> str:
        return f"Inverse-Weibull"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            self.a
            * self.b
            * self.x ** (-(self.a + 1))
            * exp(-((self.b / self.x) ** self.a))
        )

    def CDF(self):
        return exp(-((self.b / self.x) ** self.a))

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def FGM(self):
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )
        return self.b**self.r * gamma(1 - self.r / self.a)

    def replace(self, parameters, function: str = "pdf"):
        params = {}
        if parameters["a"] < 0:
            raise ValueError("a must be greater than 0")
        if parameters["b"] < 0:
            raise ValueError("b must be greater than 0")

        params = {
            self.a: self.a_dummy,
            self.b: self.b_dummy,
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
        alpha, beta = params
        if alpha <= 0 or beta <= 0:
            return np.inf
        n = len(data)
        term1 = -n * np.log(alpha) - n * alpha * np.log(beta)
        term2 = (alpha + 1) * np.sum(np.log(data))
        term3 = np.sum((beta / data) ** alpha)
        return term1 + term2 + term3

    @singledispatchmethod
    def fit(self, data: List, initial: Tuple = (1, 1), method: str = "Default"):
        """Estimate the parameters alpha and beta using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (alpha, beta).
            method (str): Optimization method to use (e.g., 'Nelder-Mead', 'BFGS'). If 'Default', uses default method of scipy's minimize.

        """
        if not all(x > 0 for x in data):
            raise ValueError("All data points must be positive.")

        minimize_kwargs = {
            "fun": self._negloglik,
            "x0": initial,
            "bounds": [(1e-6, None), (1e-6, None)],
            "args": (np.array(data),),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        result = minimize(**minimize_kwargs)

        if result.success:
            return {"a": float(result.x[0]), "b": float(result.x[1])}
        else:
            print(result)
            raise ValueError("Parameter estimation failed")

    @fit.register
    def _(self, data: tuple, initial: Tuple = (1, 1), method: str = "Default"):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed
            times and event indicators.
            initial (Tuple): Initial guess for the parameters (alpha, beta).
            method (str): Optimization method to use.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            alpha, beta = params
            if alpha <= 0 or beta <= 0:
                return np.inf

            f = self._pdf(times, alpha, beta)
            S = self._sf(times, alpha, beta)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if initial is None:
            initial = (1, 1)
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

        return {"a": float(res.x[0]), "b": float(res.x[1])}
