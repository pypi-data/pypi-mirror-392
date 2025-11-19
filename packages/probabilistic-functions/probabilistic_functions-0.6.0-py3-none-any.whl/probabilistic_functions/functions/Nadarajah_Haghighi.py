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


class Nadarajah_Haghighi:
    def __init__(self):
        self.a, self.b = symbols("alpha beta", real=True, positive=True)
        self.base_symbols = (self.a, self.b)
        self.bounds = [(1e-5, None), (1e-5, None)]
        self.a_dummy = symbols("a")
        self.b_dummy = symbols("b")
        self.x = symbols("x", real=True, positive=True)
        self.r = symbols("r")
        self._mode = "Continuous"
        self.method = None

        self._build_functions()

    # ----------------------------------------------------------------------
    # Funciones simbólicas del modelo
    # ----------------------------------------------------------------------
    def PDF(self):
        return (
            self.a
            * self.b
            * (1 + self.b * self.x) ** (self.a - 1)
            * exp(1 - (1 + self.b * self.x) ** self.a)
        )

    def CDF(self):
        return 1 - exp(1 - (1 + self.b * self.x) ** self.a)

    def SF(self):
        return exp(1 - (1 + self.b * self.x) ** self.a)

    # ----------------------------------------------------------------------
    # Construcción de funciones numéricas
    # ----------------------------------------------------------------------
    def _build_functions(self):
        """Construye las funciones numéricas (sin lambdas anidadas)."""
        raw_cdf = lambdify(
            (self.x, self.a, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )

        def pdf_func(x_val, a, b):
            return (
                a
                * b
                * ((a * x_val + 1) ** (b - 1))
                * np.exp(1 - ((a * x_val + 1) ** b))
            )
            # vec_func = np.vectorize(lambda xv: float(raw_pdf(xv, a, b)))
            # return vec_func(x_val)

        def sf_func(x_val, a, b):
            return np.exp(1 - ((a * x_val + 1) ** b))
            # vec_func = np.vectorize(lambda xv: float(raw_sf(xv, a, b)))
            # return vec_func(x_val)

        def cdf_func(x_val, params):
            a, b = params
            vec_func = np.vectorize(lambda xv: float(raw_cdf(xv, a, b)))
            return vec_func(x_val)

        self._pdf = pdf_func
        self._sf = sf_func
        self._cdf = cdf_func

    # ----------------------------------------------------------------------
    # Métodos públicos
    # ----------------------------------------------------------------------
    def pdf_func(self, x, params):
        return self._pdf(x, *params)

    def sf_func(self, x, params):
        return self._sf(x, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

    # ----------------------------------------------------------------------
    # Serialización segura
    # ----------------------------------------------------------------------
    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ("_pdf", "_sf", "_cdf"):
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
        return f"Nadarajah-Haghighi"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            self.a
            * self.b
            * (1 + self.a * self.x) ** (self.b - 1)
            * exp(-((1 + self.a * self.x) ** self.b - 1))
        )

    def CDF(self):
        return 1 - exp(-((1 + self.a * self.x) ** self.b - 1))

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def FGM(self):
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )
        return self.b * integrate(
            (((log(self.x) ** (1 / self.a) - 1)) ** (self.r))
            * exp(-self.b * (self.x - exp(1))),
            (self.x, exp(1), oo),
        )

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
        a, b = params
        if a <= 0 or b <= 0:
            return np.inf
        n = len(data)
        term1 = -n * np.log(a)
        term2 = -n * np.log(b)
        term3 = -(a - 1) * np.sum(np.log(1 + b * data))
        term4 = -n
        term5 = np.sum((1 + b * data) ** a)
        return term1 + term2 + term3 + term4 + term5

    @singledispatchmethod
    def fit(self, data: List, initial: Tuple = (1, 1), method: str = "Default"):
        """Estimate the parameters alpha and beta using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (alpha, beta).
            method (str): Optimization method to use (e.g., 'Nelder-Mead', 'BFGS'). If 'Default', uses default method of scipy's minimize.

        """
        if not all(x >= 0 for x in data):
            raise ValueError("All data points must be non-negative.")

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
            data (tuple): A tuple containing two lists - observed times and event indicators.
            initial (Tuple): Initial guess for the parameters (alpha, beta).
            method (str): Optimization method to use.
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
            initial = (1, 1)
        minimize_kwargs = {
            "fun": negloglik_censored,
            "x0": initial,
            "bounds": [(1e-6, None), (1e-6, None)],
            "args": (times, events),
        }
        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        return {"a": float(res.x[0]), "b": float(res.x[1])}
