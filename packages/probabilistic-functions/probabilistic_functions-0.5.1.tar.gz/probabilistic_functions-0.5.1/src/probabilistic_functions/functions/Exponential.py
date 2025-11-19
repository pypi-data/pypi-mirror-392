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


class Exponential:
    def __init__(self):
        self.l = symbols("lambda", real=True, positive=True)
        self.base_symbols = [self.l]
        self.bounds = [(1e-6, None)]
        self.l_dummy = symbols("l")
        self.x = symbols("x", real=True, positive=True)
        self.t = symbols("t", positive=True)
        self._mode = "Continuous"
        self.method = None

        # Compilación inicial (se puede volver a hacer tras deserializar)
        self._build_functions()

    # ----------------------------------------------------------------------
    # Funciones simbólicas del modelo
    # ----------------------------------------------------------------------
    def PDF(self):
        return self.l * exp(-self.l * self.x)

    def SF(self):
        return exp(-self.l * self.x)

    def CDF(self):
        return 1 - exp(-self.l * self.x)

    # ----------------------------------------------------------------------
    # Construcción de las funciones numéricas
    # ----------------------------------------------------------------------
    def _build_functions(self):
        """Construye las funciones numéricas del modelo."""
        self._pdf = lambdify((self.x, self.l), self.PDF(), modules=["numpy"])
        self._sf = lambdify((self.x, self.l), self.SF(), modules=["numpy"])
        raw_cdf = lambdify((self.x, self.l), self.CDF(), modules=["numpy"])

        # Se evita lambda anónima para compatibilidad con pickle
        def cdf_func(x, lmbda):
            return raw_cdf(x, lmbda)

        self._cdf = cdf_func

    # ----------------------------------------------------------------------
    # Métodos públicos de evaluación
    # ----------------------------------------------------------------------
    def pdf_func(self, x, params):
        return self._pdf(x, *params)

    def sf_func(self, x, params):
        return self._sf(x, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, *params)

    # ----------------------------------------------------------------------
    # Métodos especiales para serialización
    # ----------------------------------------------------------------------
    def __getstate__(self):
        """Prepara el estado para serialización."""
        state = self.__dict__.copy()
        # No serializamos funciones numéricas (las reconstruimos al cargar)
        for key in ("_pdf", "_sf", "_cdf"):
            if key in state:
                del state[key]
        return state

    def __setstate__(self, state):
        """Reconstruye el estado tras la deserialización."""
        self.__dict__.update(state)
        self._build_functions()  # reconstrucción segura de las funciones

    # ----------------------------------------------------------------------
    # Métodos auxiliares
    # ----------------------------------------------------------------------
    @property
    def get_name(self):
        return "Exponential"

    @property
    def get_mode(self):
        return self._mode

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Exponential distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
        \text{{Parameters support:}} \quad {latex(Contains(symbols("lambda"), Interval(0, oo)))} \\[6pt]
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
        return "Exponential"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return self.l * exp(-self.l * self.x)

    def FGM(self):
        return self.l / (self.l - self.t)

    def CDF(self):
        return integrate(self.PDF(), (self.x, 0, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return exp(-self.l * self.x)

    def HF(self):
        return self.PDF() / self.SF()

    def replace(
        self,
        parameters,
        function: str = "PDF",
    ):
        if "l" not in parameters:
            parameters["l"] = self.l
        else:
            if parameters["l"] < 0:
                raise ValueError("l must be greater than 0")

        function_ = {
            "PDF": self.PDF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }

        if function.upper() in function_:
            return (
                function_[function.upper()]()
                .subs({self.l: self.l_dummy})
                .subs(parameters)
            )
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

    def _negloglik(self, lam, data):
        if lam <= 0:
            return np.inf
        x = np.array(data)
        loglik = np.sum(np.log(lam) - lam * x)
        return -loglik

    @singledispatchmethod
    def fit(self, data: List, method: str = "MLE"):
        """Estimate the parameter lambda using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.

        Returns:
            dict: A dictionary containing the estimated parameter.
        """
        if not all(x >= 0 for x in data):
            raise ValueError("All data points must be non-negative.")

        if method == "MLE":
            self.method = method.upper()
            return {"l": float(1 / (np.mean(data) + 1e-10))}
        else:
            minimize_kwargs = {
                "fun": self._negloglik,
                "x0": np.array([1.0]),
                "args": (np.array(data),),
                "bounds": self.bounds,
            }

            if method.upper() != "DEFAULT":
                minimize_kwargs["method"] = method

            self.method = method.upper()
            res = minimize(**minimize_kwargs)

            return {"l": res.x[0]}

    @fit.register
    def _(self, data: tuple, method: str = "DEFAULT"):
        """Estimate the parameter lambda using Maximum Likelihood Estimation (MLE).

        Args:
            times (list): A list of observed data points.
            events (list, optional): A list indicating if the event was observed (1) or censored (0). Defaults to None.

        Returns:
            dict: A dictionary containing the estimated parameter.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(lam, times, events):
            lam = lam[0]
            if lam <= 0:
                return np.inf

            f = self._pdf(times, lam)
            S = self._sf(times, lam)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        res = minimize(
            fun=negloglik_censored,
            x0=np.array([1.0]),
            args=(times, events),
            bounds=[(1e-6, None)],
            method=method if method.upper() != "DEFAULT" else "L-BFGS-B",
        )
        return {"l": res.x[0]}
