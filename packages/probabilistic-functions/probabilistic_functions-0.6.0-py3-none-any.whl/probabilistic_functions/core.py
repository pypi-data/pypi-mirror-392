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


class Bernulli:
    def __init__(self):
        self.p = symbols("theta", real=True, positive=True)
        self.x = symbols("x", integer=True, nonnegative=True)
        self._mode = "Discrete"
        self.t = symbols("t")
        self._support = {0, 1}
        self.method = None

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Bernoulli distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x,FiniteSet(0,1)))} \\[6pt]
        \text{{Parameters support:}} \quad {latex(Contains(self.p, Interval(0,1)))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PMF())} \\[6pt]
        \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
        \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
        \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
        \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
        \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
        \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).simplify())}
        """
        display(Math(expr))

    @property
    def get_mode(self) -> str:
        return self._mode

    @property
    def is_fuction(self) -> bool:
        return True

    @property
    def get_soport(self) -> set:
        return self._support

    @property
    def get_name(self) -> str:
        return "Bernulli"

    @property
    def get_method(self) -> str:
        return self.method

    def PMF(self):
        return pow(self.p, self.x) * pow(1 - self.p, 1 - self.x)

    def FGM(self):
        return self.p * exp(self.t) + 1 - self.p

    def CDF(self):
        return (summation(self.PMF(), (self.x, 0, floor(self.x)))).simplify()

    def SF(self):
        return (1 - self.CDF().subs(self.x, self.x - 1)).simplify()

    def HF(self):
        return (self.PMF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PMF"):
        if parameters["p"] < 0 or parameters["p"] > 1:
            raise ValueError("p must be between 0 and 1")

        parameters = {self.p: parameters["p"]}

        functions_ = {
            "PMF": self.PMF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }
        if function.upper() in functions_:
            return functions_[function.upper()]().subs(parameters)
        else:
            raise ValueError(
                "Invalid function type. Choose from 'PMF', 'CDF', 'SF', or 'HF'."
            )

    def calculate_moments(self, n: int):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")

        return diff(self.FGM(), self.t, n).subs(self.t, 0).simplify()

    def _negloglik(self, p, data):
        if p <= 0 or p >= 1:
            return np.inf
        x = np.array(data)
        loglik = np.sum(x * np.log(p) + (1 - x) * np.log(1 - p))
        return -loglik

    def fit(self, data: list, method: str = "MLE"):
        """Estimate the parameter p using Maximum Likelihood Estimation (MLE).

        Args:
            data (list): A list of observed data points (0s and 1s).

        Returns:
            dict: A dictionary containing the estimated parameter.
        """
        if not all(x in [0, 1] for x in data):
            raise ValueError("All data points must be either 0 or 1.")

        if method.upper() == "MLE":
            self.method = method.upper()
            return {"p": float(np.mean(data))}
        else:
            minimize_kwargs = {
                "fun": self._negloglik,
                "x0": 0.5,
                "args": (np.array(data),),
                "bounds": [(1e-6, 1 - 1e-6)],
            }
            if method.upper() != "DEFAULT":
                minimize_kwargs["method"] = method
            self.method = method.upper()
            res = minimize(**minimize_kwargs)
            return {"p": float(res.x[0])}


class Binomial:
    def __init__(self):
        self.p = symbols("theta")
        self.x = symbols("x")
        self.n = symbols("n")
        self.t = symbols("t")
        self._mode = "Discrete"
        self._support = None
        self.method = None

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Binomial distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x,Range(0,self.n)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(self.p, Interval(0,1)))} \\[6pt]
        \quad {latex(Contains(self.n,Naturals))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PMF())} \\[6pt]
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
        return "Binomial"

    @property
    def get_method(self) -> str:
        return self.method

    def PMF(self):
        return (
            (binomial(self.n, self.x))
            * pow(self.p, self.x)
            * pow(1 - self.p, self.n - self.x)
        )

    def FGM(self):
        return pow(((self.p * exp(self.t)) + 1 - self.p), self.n)

    def CDF(self):
        return (summation(self.PMF(), (self.x, 0, floor(self.x)))).simplify()

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PMF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PMF"):
        if "p" in parameters:
            if parameters["p"] < 0 or parameters["p"] > 1:
                raise ValueError("p must be between 0 and 1")
            parameters["theta"] = parameters.pop("p")
        if "n" in parameters:
            if parameters["n"] <= 0:
                raise ValueError("n must be greater than 0")

        functions_ = {
            "PMF": self.PMF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }
        if function.upper() in functions_:
            return functions_[function.upper()]().subs(parameters)
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        return diff(self.FGM(), self.t, n).subs(self.t, 0).simplify()

    def _negloglik(self, p, data, n):
        if p <= 0 or p >= 1:
            return np.inf
        x = np.array(data)
        # usando gammaln para estabilidad numérica: log(n!) = gammaln(n+1)
        loglik = np.sum(x * np.log(p) + (n - x) * np.log(1 - p))
        return -loglik

    def fit(self, data: list, n: int, method: str = "MLE"):
        """Estimate the parameters p and n using Maximum Likelihood Estimation (MLE).
        Args:
            data (list): A list of observed data points (0s and 1s).
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(isinstance(x, int) and x >= 0 for x in data):
            raise ValueError("All data points must be non-negative integers.")

        if method.upper() == "MLE":
            if n <= 0:
                raise ValueError("n must be greater than 0")
            if any(x > n for x in data):
                raise ValueError("All data points must be less than or equal to n.")

            self.method = method.upper()
            return {"p": float(np.mean(data) / n), "n": n}
        else:
            minimize_kwargs = {
                "fun": self._negloglik,
                "x0": 0.5,
                "args": (np.array(data), n),
                "bounds": [(1e-6, 1 - 1e-6)],
            }
            if method.upper() != "DEFAULT":
                minimize_kwargs["method"] = method

            self.method = method.upper()
            res = minimize(**minimize_kwargs)
            return {"p": float(res.x[0]), "n": n}


class Geometric:
    def __init__(self):

        self.p = symbols("theta", real=True, positive=True)
        self.x = symbols("x", integer=True, nonnegative=True)
        self.t = symbols("t")
        self._mode = "Discrete"
        self.method = None

    def __call__(self, *args, **kwds):
        Nplus = symbols(r"\mathbb{N}^{+}", real=True)
        expr = rf"""
        \textbf{{\Large Geometric distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PMF())} \\[6pt]
        \text{{Support:}} \quad {latex(self.x)} \in \mathbb{{N}}^+ \\[6pt]
        \text{{Parameters support:}} \quad {latex(Contains(self.p, Interval(0,1)))} \\[6pt]
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
        return "Geometric"

    @property
    def get_method(self) -> str:
        return self.method

    def PMF(self):
        return pow(1 - self.p, self.x - 1) * self.p

    def FGM(self):
        return (self.p * exp(self.t)) / (1 - (1 - self.p) * exp(self.t))

    def CDF(self):
        return (summation(self.PMF(), (self.x, 1, floor(self.x)))).simplify()

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PMF() / self.SF()).simplify()

    def replace(
        self,
        parameters,
        function: str = "PMF",
    ):
        if parameters["p"] < 0 or parameters["p"] > 1:
            raise ValueError("p must be between 0 and 1")
        funcionts_ = {
            "PMF": self.PMF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }
        if function.upper() in funcionts_:
            return funcionts_[function.upper()]().subs({self.p: parameters["p"]})
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        return diff(self.FGM(), self.t, n).subs(self.t, 0).simplify()

    def _negloglik(self, p, data):
        if p <= 0 or p > 1:
            return np.inf
        x = np.array(data)
        loglik = np.sum(np.log(p) + x * np.log(1 - p))
        return -loglik

    def fit(self, data: list, method: str = "MLE"):
        """Estimate the parameter p using Maximum Likelihood Estimation (MLE).

        Args:
            data (list): A list of observed data points (positive integers).

        Returns:
            dict: A dictionary containing the estimated parameter.
        """
        if not all(isinstance(x, int) and x > 0 for x in data):
            raise ValueError("All data points must be positive integers.")

        if method.upper() == "MLE":
            self.method = method.upper()
            return {"p": float(1 / (1 + np.mean(data)))}

        else:
            minimize_kwargs = {
                "fun": self._negloglik,
                "x0": 0.5,
                "args": (np.array(data),),
                "bounds": [(1e-6, 1 - 1e-6)],
            }
            if method.upper() != "DEFAULT":
                minimize_kwargs["method"] = method
            self.method = method.upper()
            res = minimize(**minimize_kwargs)
            return {"p": float(res.x[0])}


class HyperGeometric:
    def __init__(self):
        self.n = symbols("n")
        self.K = symbols("K")
        self.N = symbols("N")
        self.x = symbols("x")
        self.t = symbols("t")
        self._mode = "Discrete"
        self.method = None

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large HyperGeometric distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Range(Max(0, self.n - (self.N - self.K)), Min(self.n, self.K))))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(self.n, Naturals))} \\[6pt]
        \quad {latex(Contains(self.K, Range(0, self.N)))} \\[6pt]
        \quad {latex(Contains(self.n, Range(0, self.N)))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PMF())} \\[6pt]
        \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
        \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
        \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
        \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
        \text{{Expected value:}} \quad {latex(UnevaluatedExpr(self.n * self.K / self.N))} \\[6pt]
        \text{{Variance:}} \quad {latex((self.n * self.K / self.N) * ((self.N - self.K) / self.N) * ((self.N - self.n) / (self.N - 1)))}
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
        return "HyperGeometric"

    @property
    def get_method(self) -> str:
        return self.method

    def PMF(self):
        return (
            binomial(self.K, self.x) * binomial(self.N - self.K, self.n - self.x)
        ) / (binomial(self.N, self.n))

    def FGM(self):
        warnings.warn("It does not have a simple closed-form expression.")
        return summation(
            exp(self.t * self.x) * self.PMF(),
            (self.x, Max(0, self.n - (self.N - self.K)), Min(self.n, self.K)),
        )

    def CDF(self):
        return (summation(self.PMF(), (self.x, 0, floor(self.x)))).simplify()

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PMF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PMF"):
        have_N = False
        if "N" in parameters:
            have_N = True
            if not isinstance(parameters["N"], int) or parameters["N"] < 1:
                raise ValueError("N must be and integer greater than or equal to 1")

        if "K" in parameters:
            if not have_N:
                raise ValueError("K must be defined only after N is defined")
            if not isinstance(parameters["K"], int) or parameters["K"] < 0:
                raise ValueError("K must be an integer greater than or equal to 0")
            if parameters["K"] > parameters["N"]:
                raise ValueError("K must be less than or equal to N")

        if "n" in parameters:
            if not have_N:
                raise ValueError("n must be defined only after N is defined")
            if not isinstance(parameters["n"], int) or parameters["n"] < 0:
                raise ValueError("K must be an integer greater than or equal to 0")
            if parameters["n"] > parameters["N"]:
                raise ValueError("n must be less than or equal to N")

        functions_ = {
            "PMF": self.PMF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }
        if function.upper() in functions_:
            return functions_[function.upper()]().subs(parameters)
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        return diff(self.FGM(), self.t, n).subs(self.t, 0).simplify()

    def _negloglik(self, params, data, n, N):
        # params[0] será K
        K = params
        if K < 0 or K > N:
            return np.inf
        loglik = 0
        for k in data:
            if k > K or k > n:
                return np.inf
            loglik += (
                np.log(comb(K, k)) + np.log(comb(N - K, n - k)) - np.log(comb(N, n))
            )
        return -loglik

    def fit(self, data: list, N: int, n: int, method: str = "Default"):
        if not all(isinstance(x, int) and x >= 0 for x in data):
            raise ValueError("All data points must be non-negative integers.")

        if not isinstance(N, int) or N < 1:
            raise ValueError("N must be an integer greater than or equal to 1.")

        if not isinstance(n, int) or n < 0 or n > N:
            raise ValueError("n must be an integer between 0 and N.")

        minimize_kwargs = {
            "fun": self._negloglik,
            "x0": n,  # Initial guess for K
            "args": (np.array(data), n, N),
            "bounds": [(1e-8, N)],
        }
        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        res = minimize(**minimize_kwargs)
        return {"K": int(round(res.x[0])), "N": N, "n": n}


class Poisson:
    def __init__(self):
        self.l = symbols("lambda")
        self.l_dummy = symbols("l")
        self.x = symbols("x")
        self._mode = "Discrete"
        self.t = symbols("t")
        self.method = None

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Poisson distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.l, Interval(0, oo)))} \\[6pt]
        \text{{Parameters support:}} \quad {latex(Contains(self.l, Interval(0, oo)))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PMF())} \\[6pt]
        \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
        \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
        \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
        \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
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
        return "Poisson"

    @property
    def get_method(self) -> str:
        return self.method

    def PMF(self):
        return pow(self.l, self.x) * exp(-self.l) / factorial(self.x)

    def FGM(self):
        return exp(self.l * (exp(self.t) - 1))

    def CDF(self):
        return (summation(self.PMF(), (self.x, 0, floor(self.x)))).simplify()

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PMF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PMF"):
        if "l" in parameters:
            if parameters["l"] < 0:
                raise ValueError("l must be greater than 0")

        functions_ = {
            "PMF": self.PMF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }
        if function.upper() in functions_:
            return (
                functions_[function.upper()]()
                .subs({self.l: self.l_dummy})
                .subs(parameters)
            )
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        return diff(self.FGM(), self.t, n).subs(self.t, 0).simplify()

    def _negloglik(sel, lam, data):
        if lam <= 0:
            return np.inf
        x = np.array(data)
        loglik = np.sum(x * np.log(lam) - lam - gammaln(x + 1))
        return -loglik

    def fit(self, data: list, method: str = "MLE"):
        """Estimate the parameter l using Maximum Likelihood Estimation (MLE).

        Args:
            data (list): A list of observed data points (non-negative integers).

        Returns:
            dict: A dictionary containing the estimated parameter.
        """
        if not all(isinstance(x, int) and x >= 0 for x in data):
            raise ValueError("All data points must be non-negative integers.")

        if method.upper() == "MLE":
            self.method = method.upper()
            return {"l": float(np.mean(data))}
        else:
            minimize_kwargs = {
                "fun": self._negloglik,
                "x0": 1.0,
                "args": (np.array(data),),
                "bounds": [(1e-6, None)],
            }
            if method.upper() != "DEFAULT":
                minimize_kwargs["method"] = method
            self.method = method.upper()
            res = minimize(**minimize_kwargs)
            return {"l": float(res.x[0])}


class Uniform:
    def __init__(self):
        self.a, self.b = symbols("a b")
        self.x = symbols("x")
        self.t = symbols("t")
        self._mode = "Continuous"
        self.method = None

        raw_cdf = lambdify(
            (self.x, self.a, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x, params: raw_cdf(x, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Uniform distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(self.a, self.b)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(self.a, sympy.Reals))} \\[6pt]
        \quad {latex(Contains(self.b, sympy.Reals))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
        \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
        \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
        \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
        \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
        \text{{Expected value:}} \quad {latex(self.calculate_moments(1).factor())} \\[6pt]
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
        return "Uniform"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return 1 / (self.b - self.a)

    def FGM(self):
        return (exp(self.t * self.b) - exp(self.t * self.a)) / (
            self.t * (self.b - self.a)
        )

    def CDF(self):
        return integrate(self.PDF(), (self.t, self.a, self.x)).simplify()

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        if "a" in parameters:
            if "b" not in parameters:
                raise ValueError("b must be defined only after a is defined")
            if parameters["a"] >= parameters["b"]:
                raise ValueError("a must be less than b")
        functions_ = {
            "PDF": self.PDF,
            "CDF": self.CDF,
            "SF": self.SF,
            "HF": self.HF,
            "FGM": self.FGM,
        }

        if function.upper() in functions_:
            return functions_[function.upper()]().subs(parameters)
        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int, mode: str = "integrate"):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        if mode == "integrate":
            E = integrate(pow(self.x, n) * self.PDF(), (self.x, self.a, self.b))
        elif mode == "diff":
            E = limit(diff(self.FGM(), self.t, n).simplify(), self.t, 0)
        return E.simplify()

    def _negloglik(self, params, data):
        a, b = params
        if a >= b:
            return np.inf
        x = np.array(data)
        if any((x < a) | (x > b)):
            return np.inf
        loglik = np.sum(-np.log(b - a))
        return -loglik

    def fit(self, data: list):
        """Estimate the parameters a and b using Maximum Likelihood Estimation (MLE).

        Args:
            data (list): A list of observed data points.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in data):
            raise ValueError("All data points must be real numbers.")
        self.method = "MLE"
        return {"a": min(data), "b": max(data)}


class Exponential:
    def __init__(self):

        self.l = symbols("lambda", real=True, positive=True)
        self.base_symbols = [self.l]
        self.bounds = [(1e-6, None)]
        self.l_dummy = symbols("l")
        self.x = symbols("x")
        self.t = symbols("t", positive=True)
        self._mode = "Continuous"
        self.method = None

        self._pdf = lambdify((self.x, self.l), self.PDF(), modules=["numpy"])
        self._sf = lambdify((self.x, self.l), self.SF(), modules=["numpy"])

        raw_cdf = lambdify((self.x, self.l), self.CDF(), modules=["numpy", "mpmath"])
        self._cdf = lambda x, params: raw_cdf(x, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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

        raw_pdf = lambdify((self.x, self.m, self.v), self.PDF(), modules=["numpy"])
        self._pdf = lambda x_val, n, v: np.vectorize(
            lambda xv: float(raw_pdf(xv, n, v))
        )(x_val)
        raw_sf = lambdify((self.x, self.m, self.v), self.SF(), modules=["numpy"])
        self._sf = lambda x_val, n, v: np.vectorize(lambda xv: float(raw_sf(xv, n, v)))(
            x_val
        )

        raw_cdf = lambdify(
            (self.x, self.m, self.v), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: np.vectorize(
            lambda xv: float(raw_cdf(xv, *params))
        )(x_val)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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

        self._pdf = lambdify(
            (self.x, self.a, self.b), self.PDF(), modules=["numpy", "mpmath"]
        )
        self._sf = lambdify(
            (self.x, self.a, self.b), self.SF(), modules=["numpy", "mpmath"]
        )

        raw_cdf = lambdify(
            (self.x, self.a, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x, params: raw_cdf(x, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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


class Gamma:
    def __init__(self):
        self.a, self.b = symbols("alpha beta", real=True, positive=True)
        self.base_symbols = (self.a, self.b)
        self.bounds = [(1e-6, None), (1e-6, None)]
        self.a_dummy = symbols("a")
        self.b_dummy = symbols("b")
        self.x = symbols("x")
        self.t = symbols("t")
        self._mode = "Continuous"
        self.method = None

        raw_pdf = lambdify(
            (self.x, self.a, self.b), self.PDF(), modules=["numpy", "mpmath"]
        )
        raw_sf = lambdify(
            (self.x, self.a, self.b), self.SF(), modules=["numpy", "mpmath"]
        )

        self._pdf = lambda x_val, a, b: np.vectorize(
            lambda xv: float(raw_pdf(xv, a, b))
        )(x_val)

        self._sf = lambda x_val, a, b: np.vectorize(lambda xv: float(raw_sf(xv, a, b)))(
            x_val
        )

        raw_cdf = lambdify(
            (self.x, self.a, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: np.vectorize(
            lambda xv: float(raw_cdf(xv, *params))
        )(x_val)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Gamma distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(symbols("alpha"), Interval(0, oo)))} \\[6pt]
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
        return "Gamma"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            (self.b**self.a / gamma(self.a))
            * self.x ** (self.a - 1)
            * exp(-self.b * self.x)
        )

    def FGM(self):
        return (self.b / (self.b - self.t)) ** self.a

    def CDF(self):
        return integrate(self.PDF(), (self.x, 0, self.x)).rewrite(sympy.Piecewise)

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
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
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
            np.sum((a - 1) * np.log(x) - b * x)
            + len(x) * a * np.log(b)
            - len(x) * np.log(gamma_func(a))
        )
        return -loglik

    @singledispatchmethod
    def fit(self, data: List, initial: tuple = None, method: str = "Default"):
        """Estimate the parameters alpha and beta using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (a, b).
            tol (float, optional): Tolerance for the numerical solver. Defaults to None.
            verify (bool, optional): Whether to verify the solution. Defaults to False.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x >= 0 for x in data):
            raise ValueError("All data points must be non-negative.")

        if initial is None:
            mean = np.mean(data)
            var = np.var(data)
            a0 = mean**2 / var  # estimación inicial para alpha
            b0 = mean / var  # estimación inicial para beta
            initial = (a0, b0)

        minimize_kwargs = {
            "fun": self._negloglik,
            "x0": initial,
            "bounds": self.bounds,
            "args": (np.array(data),),
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
            data (tuple): A tuple containing two lists - observed
            times and event indicators.
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
            mean = np.mean(times)
            var = np.var(times)
            a0 = mean**2 / var  # estimación inicial para alpha
            b0 = mean / var  # estimación inicial para beta
            initial = (a0, b0)

        res = minimize(
            fun=negloglik_censored,
            x0=initial,
            args=(times, events),
            bounds=self.bounds,
            method=method if method.upper() != "DEFAULT" else "L-BFGS-B",
        )
        return {"a": float(res.x[0]), "b": float(res.x[1])}


class Beta:
    def __init__(self):
        self.a, self.b = symbols("a b", real=True, positive=True)
        self.a_dummy = symbols("a")
        self.b_dummy = symbols("b")
        self.x = symbols("x")
        self.r = symbols("r")
        self._mode = "Continuous"
        self.method = None

        raw_cdf = lambdify(
            (self.x, self.a, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: raw_cdf(x_val, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

    def __call__(self, *args, **kwds):
        expr = rf"""
        \textbf{{\Large Beta distribution}} \\[6pt]
        \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
        \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, 1)))} \\[6pt]
        \text{{Parameters support:}} \\[6pt]
        \quad {latex(Contains(symbols("alpha"), Interval(0, oo)))} \\[6pt]
        \quad {latex(Contains(symbols("beta"), Interval(0, oo)))} \\[6pt]
        \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
        \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
        \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
        \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
        \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
        \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
        \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).factor())}
        """
        display(Math(expr))

    @property
    def get_mode(self):
        return self._mode

    @property
    def is_fuction(self):
        return True

    @property
    def get_name(self) -> str:
        return "Beta"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            (1 / beta_func(self.a, self.b))
            * (self.x ** (self.a - 1))
            * ((1 - self.x) ** (self.b - 1))
        )

    def FGM(self):
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )

        return (gamma(self.a + self.r) * gamma(self.a + self.b)) / (
            gamma(self.a) * gamma(self.a + self.b + self.r)
        )

    def CDF(self):
        return integrate(self.PDF(), (self.x, 0, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        params = {}
        if "a" in parameters:
            if parameters["a"] < 0:
                raise ValueError("a must be greater than 0")
        if "b" in parameters:
            if parameters["b"] < 0:
                raise ValueError("b must be greater than 0")
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
                .subs({self.a: self.a_dummy, self.b: self.b_dummy})
                .subs(parameters)
            )

        else:
            raise ValueError("Invalid function type")

    def calculate_moments(self, n: int, mode: str = "diff"):
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        if mode == "integrate":
            E = integrate(pow(self.x, n) * self.PDF(), (self.x, 0, 1)).rewrite(
                sympy.Piecewise
            )
        elif mode == "diff":
            E = self.FGM().subs(self.r, n).simplify()
        return E.simplify()

    def _negloglik(self, params, data):
        a, b = params
        if a <= 0 or b <= 0:
            return np.inf
        x = np.array(data)
        loglik = (
            (a - 1) * np.sum(np.log(x))
            + (b - 1) * np.sum(np.log(1 - x))
            - len(x) * np.log(beta_func(a, b))
        )
        return -loglik

    def fit(self, data: List, initial: Tuple = None, method="Default"):
        """Estimate the parameters a and b using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (a, b).
            tol (float, optional): Tolerance for the numerical solver. Defaults to None.
            verify (bool, optional): Whether to verify the solution. Defaults to False.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(0 <= x <= 1 for x in data):
            raise ValueError("All data points must be in the interval [0, 1].")

        if initial is None:
            initial = (1.0, 1.0)
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
        return {"a": float(res.x[0]), "b": float(res.x[1])}


class LogNormal:
    def __init__(self):
        self.m, self.v = symbols("mu sigma^2", real=True)
        self.base_symbols = (self.m, self.v)
        self.bounds = [(None, None), (1e-5, None)]
        self.m_dummy = symbols("m")
        self.v_dummy = symbols("v")
        self.x, self.t = symbols("x t")
        self.t = symbols("t")
        self.r = symbols("r")
        self._mode = "Continuous"
        self.method = None

        raw_pdf = lambdify((self.x, self.m, self.v), self.PDF(), modules=["numpy"])

        raw_sf = lambdify((self.x, self.m, self.v), self.SF(), modules=["numpy"])

        self._pdf = lambda x_val, m, v: np.vectorize(
            lambda xv: float(raw_pdf(xv, m, v))
        )(x_val)

        self._sf = lambda x_val, m, v: np.vectorize(lambda xv: float(raw_sf(xv, m, v)))(
            x_val
        )

        raw_cdf = lambdify(
            (self.x, self.m, self.v), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: np.vectorize(
            lambda xv: float(raw_cdf(xv, *params))
        )(x_val)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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

        raw_pdf = lambdify(
            (self.x, self.m, self.b), self.PDF(), modules=["numpy", "mpmath"]
        )
        raw_sf = lambdify(
            (self.x, self.m, self.b), self.SF(), modules=["numpy", "mpmath"]
        )
        self._pdf = lambda x_val, m, b: np.vectorize(
            lambda xv: float(raw_pdf(xv, m, b))
        )(x_val)
        self._sf = lambda x_val, m, b: np.vectorize(lambda xv: float(raw_sf(xv, m, b)))(
            x_val
        )
        raw_cdf = lambdify(
            (self.x, self.m, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: raw_cdf(x_val, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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

        if self.type == 1:
            self.x_m, self.a = symbols("x_m alpha", real=True, positive=True)
            self.base_symbols = (self.x_m, self.a)
            self.x_m_dummy = symbols("x_m")
            self.a_dummy = symbols("a")

            raw_pdf = lambdify(
                (self.x, self.x_m, self.a), self.PDF(), modules=["numpy", "mpmath"]
            )
            self._pdf = lambda x_val, x_m, a: np.vectorize(
                lambda xv: float(raw_pdf(xv, x_m, a))
            )(x_val)

            raw_sf = lambdify(
                (self.x, self.x_m, self.a), self.SF(), modules=["numpy", "mpmath"]
            )

            self._sf = lambda x_val, x_m, a: np.vectorize(
                lambda xv: float(raw_sf(xv, x_m, a))
            )(x_val)

            raw_cdf = lambdify(
                (self.x, self.x_m, self.a), self.CDF(), modules=["numpy", "mpmath"]
            )
            self._cdf = lambda x_val, params: raw_cdf(x_val, *params)
        elif self.type == 2:
            self.a, self.l = symbols("alpha lambda", real=True, positive=True)
            self.base_symbols = (self.a, self.l)
            self.a_dummy = symbols("a")
            self.l_dummy = symbols("l")
            self.bounds = [(1e-5, None), (1e-5, None)]

            raw_pdf = lambdify(
                (self.x, self.a, self.l), self.PDF(), modules=["numpy", "mpmath"]
            )
            self._pdf = lambda x_val, a, l: np.vectorize(
                lambda xv: float(raw_pdf(xv, a, l))
            )(x_val)

            raw_sf = lambdify(
                (self.x, self.a, self.l), self.SF(), modules=["numpy", "mpmath"]
            )
            self._sf = lambda x_val, a, l: np.vectorize(
                lambda xv: float(raw_sf(xv, a, l))
            )(x_val)

            raw_cdf = lambdify(
                (self.x, self.a, self.l), self.CDF(), modules=["numpy", "mpmath"]
            )
            self._cdf = lambda x_val, params: raw_cdf(x_val, *params)
        elif self.type == 9:
            self.s = symbols("sigma", real=True, positive=True)
            self.s_dummy = symbols("s")
            self.e = symbols("epsilon", real=True)
            self.e_dummy = symbols("e")
            self.base_symbols = (self.s, self.e)
            self.bounds = [(1e-5, None), (None, None)]

            raw_pdf = lambdify(
                (self.x, self.s, self.e), self.PDF(), modules=["numpy", "mpmath"]
            )
            self._pdf = lambda x_val, s, e: np.vectorize(
                lambda xv: float(raw_pdf(xv, s, e))
            )(x_val)

            raw_sf = lambdify(
                (self.x, self.s, self.e), self.SF(), modules=["numpy", "mpmath"]
            )
            self._sf = lambda x_val, s, e: np.vectorize(
                lambda xv: float(raw_sf(xv, s, e))
            )(x_val)

            raw_cdf = lambdify(
                (self.x, self.s, self.e), self.CDF(), modules=["numpy", "mpmath"]
            )
            self._cdf = lambda x_val, params: raw_cdf(x_val, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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

        raw_pdf = lambdify(
            (self.x, self.a, self.b, self.m), self.PDF(), modules=["numpy"]
        )
        self._pdf = lambda x_val, a, b, m: np.vectorize(
            lambda xv: float(raw_pdf(xv, a, b, m))
        )(x_val)

        raw_sf = lambdify(
            (self.x, self.a, self.b, self.m), self.SF(), modules=["numpy", "mpmath"]
        )
        self._sf = lambda x_val, a, b, m: np.vectorize(
            lambda xv: float(raw_sf(xv, a, b, m))
        )(x_val)

        raw_cdf = lambdify(
            (self.x, self.a, self.b, self.m), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: np.vectorize(
            lambda xv: float(raw_cdf(xv, *params))
        )(x_val)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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

        raw_pdf = lambdify(
            (self.x, self.a, self.c, self.l), self.PDF(), modules=["numpy", "mpmath"]
        )
        self._pdf = lambda x_val, a, c, l: np.vectorize(
            lambda xv: float(raw_pdf(xv, a, c, l))
        )(x_val)

        raw_sf = lambdify(
            (self.x, self.a, self.c, self.l), self.SF(), modules=["numpy", "mpmath"]
        )
        self._sf = lambda x_val, a, c, l: np.vectorize(
            lambda xv: float(raw_sf(xv, a, c, l))
        )(x_val)

        raw_cdf = lambdify(
            (self.x, self.a, self.c, self.l), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: raw_cdf(x_val, *params)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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


# --- Funciones globales para evitar lambdas locales ---


def lindley1_pdf_func(x, p, raw_pdf):
    return raw_pdf(x, p)


def lindley1_sf_func(x, p, raw_sf):
    return raw_sf(x, p)


def lindley1_cdf_func(x, params, raw_cdf):
    return raw_cdf(x, *params)


def lindley2_pdf_func(x, p, a, y, raw_pdf):
    return np.vectorize(lambda xv: float(raw_pdf(xv, p, a, y)))(x)


def lindley2_sf_func(x, p, a, y, raw_sf):
    return np.vectorize(lambda xv: float(raw_sf(xv, p, a, y)))(x)


def lindley2_cdf_func(x, params, raw_cdf):
    return np.vectorize(lambda xv: float(raw_cdf(xv, *params)))(x)


# --- Clase principal ---


class Lindley:
    def __init__(self, type: int = 1):
        self.type = type
        if self.type not in [1, 2]:
            raise ValueError("Invalid type. Type only available 1 or 2")

        self._mode = "Continuous"
        self.method = None
        self._build_symbols()
        self._build_functions()

    def _build_symbols(self):
        self.p = symbols("theta", real=True, positive=True)
        self.t = symbols("t")
        self.x = symbols("x")
        self.bounds = [(1e-5, None)]
        self.base_symbols = (self.p,)
        if self.type == 2:
            self.a = symbols("alpha", real=True, positive=True)
            self.y = symbols("gamma", real=True, positive=True)
            self.y_dummy = symbols("y")
            self.bounds = [(1e-5, None), (1e-5, None), (1e-5, None)]
            self.base_symbols = (self.p, self.a, self.y)

    def _build_functions(self):
        if self.type == 1:
            raw_pdf = lambdify(
                (self.x, self.p), self.PDF(), modules=["numpy", "mpmath"]
            )

            raw_sf = lambdify((self.x, self.p), self.SF(), modules=["numpy", "mpmath"])
            raw_cdf = lambdify(
                (self.x, self.p), self.CDF(), modules=["numpy", "mpmath"]
            )
            self._pdf = lambda xv, p: np.vectorize(lambda xvi: float(raw_pdf(xvi, p)))(
                xv
            )
            self._sf = lambda xv, p: np.vectorize(lambda xvi: float(raw_sf(xvi, p)))(xv)
            self._cdf = lambda xv, p: np.vectorize(lambda xvi: float(raw_cdf(xvi, p)))(
                xv
            )

        elif self.type == 2:
            expr = self.PDF().subs({self.y: self.y_dummy})
            raw_pdf = lambdify(
                (self.x, self.p, self.a, self.y),
                expr,
                modules=["numpy", "mpmath"],
            )
            expr = self.SF().subs({self.y: self.y_dummy})
            raw_sf = lambdify(
                (self.x, self.p, self.a, self.y), expr, modules=["numpy", "mpmath"]
            )
            expr = self.CDF().subs({self.y: self.y_dummy})
            raw_cdf = lambdify(
                (self.x, self.p, self.a, self.y),
                expr,
                modules=["numpy", "mpmath"],
            )
            self._pdf = lambda xv, p, a, b: np.vectorize(
                lambda xvi: float(raw_pdf(xvi, p, a, b))
            )(xv)
            self._sf = lambda xv, p, a, b: np.vectorize(
                lambda xvi: float(raw_sf(xvi, p, a, b))
            )(xv)
            self._cdf = lambda xv, p, a, b: np.vectorize(
                lambda xvi: float(raw_cdf(xvi, p, a, b))
            )(xv)

    def lindley2_cdf(self, x, alpha, theta, gamma_param):
        x = np.asarray(x, dtype=float)
        if np.any(x < 0):
            raise ValueError("x debe ser >= 0")
        if alpha <= 0 or theta <= 0 or gamma_param <= 0:
            raise ValueError("alpha, theta y gamma_param deben ser > 0")

        z = theta * x
        A = gammaincc(alpha, z)
        B = gammaincc(alpha + 1, z)
        denom = gamma_param + theta
        F = 1.0 - (theta * A + gamma_param * B) / denom
        return F

    def __getstate__(self):
        state = self.__dict__.copy()
        for k in ["_pdf", "_sf", "_cdf"]:
            if k in state:
                del state[k]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._build_functions()

    def cdf_func(self, x, params):
        return self._cdf(x, params)

    def __call__(self, *args, **kwds):
        if self.type == 1:
            expr = rf"""
            \textbf{{\Large Lindley distribution}} \quad \textbf{{\Large {self.type}}}\\[6pt]
            \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
            \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
            \text{{Parameters support:}} \\[6pt]
            \quad {latex(Contains(symbols("theta"), Interval(0, oo)))} \\[6pt]
            \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
            \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
            \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
            \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
            \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
            \text{{Expected value:}} \quad {latex(self.calculate_moments(1))} \\[6pt]
            \text{{Variance:}} \quad {latex((self.calculate_moments(2) - self.calculate_moments(1)**2).factor())}
            """
        elif self.type == 2:
            expr = rf"""
            \textbf{{\Large Lindley distribution}} \quad \textbf{{\Large {self.type}}}\\[6pt]
            \text{{Distribution mode:}} \quad {self._mode} \\[6pt]
            \text{{Support:}} \quad {latex(Contains(self.x, Interval(0, oo)))} \\[6pt]
            \text{{Parameters support:}} \\[6pt]
            \quad {latex(Contains(symbols('alpha'), Interval(0, oo)))} \\[6pt] 
            \quad {latex(Contains(symbols('gamma'), Interval(0, oo)))} \\[6pt]
            \text{{Function probability:}} \quad {latex(self.PDF())} \\[6pt]
            \text{{Generating function moment:}} \quad {latex(self.FGM())} \\[6pt]
            \text{{Cumulative distribution function:}} \quad {latex(self.CDF())} \\[6pt]
            \text{{Survival function:}} \quad {latex(self.SF())} \\[6pt]
            \text{{Hazard function:}} \quad {latex(self.HF())} \\[6pt]
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
        return f"Lindley {self.type}"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        if self.type == 1:
            return (self.p**2 / (1 + self.p)) * exp(-self.p * self.x) * (1 + self.x)
        elif self.type == 2:
            return (
                self.p**2
                * (self.p * self.x) ** (self.a - 1)
                * (self.a + self.y * self.x)
                * exp(-self.p * self.x)
            ) / ((self.y + self.p) * gamma(self.a + 1))

    def FGM(self):
        if self.type == 1:
            return (self.p**2 / (self.p + 1)) * (
                1 / (self.p - self.t) + 1 / (self.p - self.t) ** 2
            )
        elif self.type == 2:
            return (self.p ** (self.a + 1) / (self.y + self.p)) * (
                1 / (self.p - self.t) ** self.a
                + self.y / (self.p - self.t) ** (self.a + 1)
            )

    def CDF(self):
        return integrate(self.PDF(), (self.x, 0, self.x)).rewrite(sympy.Piecewise)

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def replace(self, parameters, function: str = "PDF"):
        params = {}
        if "p" in parameters:
            if parameters["p"] < 0:
                raise ValueError("p must be greater than 0")
            params[self.p] = self.p_dummy
        if self.type == 2:
            if parameters["a"] < 0:
                raise ValueError("a must be greater than 0")
            if parameters["y"] < 0:
                raise ValueError("y must be greater than 0")
            params[self.a] = self.a_dummy
            params[self.y] = self.y_dummy
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
        if n < 1:
            raise ValueError("n must be greater than or equal to 1")
        if mode == "integrate":
            E = integrate(pow(self.x, n) * self.PDF(), (self.x, 0, oo)).rewrite(
                sympy.Piecewise
            )
        elif mode == "diff":
            E = limit(diff(self.FGM(), self.t, n).simplify(), self.t, 0)
        return E.simplify()

    def _negloglik(self, params, data):
        if self.type == 1:
            p = params
            if p <= 0:
                return np.inf
            n = len(data)
            term1 = n * (2 * np.log(p) - np.log(1 + p))
            term2 = -p * np.sum(data)
            term3 = np.sum(np.log(1 + data))
            return -(term1 + term2 + term3)
        elif self.type == 2:
            p, a, y = params
            if p <= 0 or a <= 0 or y <= 0:
                return np.inf
            data = np.array(data)
            n = len(data)
            term1 = n * (2 * np.log(p) - np.log(y + p) - gammaln(a + 1))
            term2 = (a - 1) * np.sum(np.log(p * data))
            term3 = np.sum(np.log(a + y * data))
            term4 = -p * np.sum(data)
            return -(term1 + term2 + term3 + term4)

    @singledispatchmethod
    def fit(self, data: List, initial: Tuple = None, method: str = "MLE"):
        """Estimate the parameters p and a using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (p, a).
            method (str): Optimization method to use (e.g., 'Nelder-Mead', 'BFGS', 'MLE'). If 'Default', uses default method of scipy's minimize.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        if not all(x >= 0 for x in data):
            raise ValueError("All data points must be non-negative.")

        if method.upper() == "MLE":
            if self.type == 1:
                n = len(data)
                S = sum(data)
                num = -(S - n) + np.sqrt((S - n) ** 2 + 8 * n * S)
                self.method = method.upper()
                return {"p": float(num / (2 * S))}
            elif self.type == 2:
                raise ValueError("No analytical solution for type 2 with MLE method")

        bounds = [(1e-6, None)]
        if self.type == 2:
            if initial is None:
                sample_mean = np.mean(data)
                sample_var = np.var(data)
                initial = [1 / sample_mean, 1.0, 0.5 / sample_mean]  # heurística
            bounds = [(1e-6, None), (1e-6, None), (1e-6, None)]
        else:
            initial = initial if initial else (1,)

        minimize_kwargs = {
            "fun": (self._negloglik),
            "x0": initial,
            "bounds": bounds,
            "args": (np.array(data),),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method

        self.method = method.upper()
        res = minimize(**minimize_kwargs)

        if self.type == 1:
            return {"p": float(res.x[0])}
        elif self.type == 2:
            return {"p": float(res.x[0]), "a": float(res.x[1]), "y": float(res.x[2])}

    @fit.register
    def _(self, data: tuple, initial: Tuple = None, method: str = "Default"):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed times and event indicators.
            initial (Tuple): Initial guess for the parameters.
            method (str): Optimization method to use.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            if self.type == 1:
                p = params
                if p <= 0:
                    return np.inf
                f = self._pdf(times, p)
                S = self._sf(times, p)
            elif self.type == 2:
                p, a, y = params
                if p <= 0 or a <= 0 or y <= 0:
                    return np.inf
                f = self._pdf(times, p, a, y)
                S = self._sf(times, p, a, y)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if self.type == 2:
            if initial is None:
                sample_mean = np.mean(times)
                sample_var = np.var(times)
                initial = [1 / sample_mean, 1.0, 0.5 / sample_mean]  # heurística
        else:
            initial = initial if initial else (1,)

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
        if self.type == 1:
            return {"p": float(res.x[0])}
        elif self.type == 2:
            return {"p": float(res.x[0]), "a": float(res.x[1]), "y": float(res.x[2])}


class Nadarajah_Haghighi:
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

        raw_pdf = lambdify(
            (self.x, self.a, self.b), self.PDF(), modules=["numpy", "mpmath"]
        )
        self._pdf = lambda x_val, a, b: np.vectorize(
            lambda xv: float(raw_pdf(xv, a, b))
        )(x_val)

        raw_sf = lambdify(
            (self.x, self.a, self.b), self.SF(), modules=["numpy", "mpmath"]
        )
        self._sf = lambda x_val, a, b: np.vectorize(lambda xv: float(raw_sf(xv, a, b)))(
            x_val
        )

        raw_cdf = lambdify(
            (self.x, self.a, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )

        self._cdf = lambda x_val, params: np.vectorize(
            lambda xv: float(raw_cdf(xv, *params))
        )(x_val)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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

        raw_pdf = lambdify(
            (self.x, self.a, self.b), self.PDF(), modules=["numpy", "mpmath"]
        )
        self._pdf = lambda x_val, a, b: np.vectorize(
            lambda xv: float(raw_pdf(xv, a, b))
        )(x_val)

        raw_sf = lambdify(
            (self.x, self.a, self.b), self.SF(), modules=["numpy", "mpmath"]
        )

        self._sf = lambda x_val, a, b: np.vectorize(lambda xv: float(raw_sf(xv, a, b)))(
            x_val
        )

        raw_cdf = lambdify(
            (self.x, self.a, self.b), self.CDF(), modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: np.vectorize(
            lambda xv: float(raw_cdf(xv, *params))
        )(x_val)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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


class Weibull_3Params:
    def __init__(self):
        self.a, self.b, self.y = symbols("alpha beta gamma", real=True, positive=True)
        self.a_dummy = symbols("a")
        self.b_dummy = symbols("b")
        self.y_dummy = symbols("y")
        self.base_symbols = (self.a, self.b, self.y_dummy)
        self.k = symbols("k", integer=True, nonnegative=True)
        self.x = symbols("x")
        self.r = symbols("r")
        self._mode = "Continuous"
        self.method = None

        expr = self.PDF().subs(self.y, self.y_dummy)
        raw_pdf = lambdify(
            (self.x, self.a, self.b, self.y_dummy), expr, modules=["numpy", "mpmath"]
        )
        self._pdf = lambda x_val, a, b, y: np.vectorize(
            lambda xv: float(raw_pdf(xv, a, b, y))
        )(x_val)

        expr = self.SF().subs(self.y, self.y_dummy)
        raw_sf = lambdify(
            (self.x, self.a, self.b, self.y_dummy), expr, modules=["numpy", "mpmath"]
        )
        self._sf = lambda x_val, a, b, y: np.vectorize(
            lambda xv: float(raw_sf(xv, a, b, y))
        )(x_val)

        expr = self.CDF().subs(self.y, self.y_dummy)
        raw_cdf = lambdify(
            (self.x, self.a, self.b, self.y_dummy), expr, modules=["numpy", "mpmath"]
        )
        self._cdf = lambda x_val, params: np.vectorize(
            lambda xv: float(raw_cdf(xv, *params))
        )(x_val)

    def cdf_func(self, x, params):
        return self._cdf(x, params)

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
        return f"Weibull 3-Parameters"

    @property
    def get_method(self) -> str:
        return self.method

    def PDF(self):
        return (
            (self.a / self.b)
            * ((self.x - self.y) / self.b) ** (self.a - 1)
            * exp(-(((self.x - self.y) / self.b) ** self.a))
        )

    def CDF(self):
        return 1 - exp(-(((self.x - self.y) / self.b) ** self.a))

    def SF(self):
        return (1 - self.CDF()).simplify()

    def HF(self):
        return (self.PDF() / self.SF()).simplify()

    def FGM(self):
        warnings.warn(
            "It does not have a simple closed-form expression. Then using the explicit form"
        )
        Piecewise(
            (self.b**self.r * gamma(1 + self.r / self.a), Eq(self.y, 0)),
            (
                sum(
                    binomial_coefficient(self.r, self.k)
                    * (self.y) ** (self.r - self.k)
                    * self.b**self.k
                    * gamma(1 + self.k / self.a),
                    (self.k, 0, self.r),
                ),
                True,
            ),
        )

    def replace(self, parameters, function: str = "pdf"):
        params = {}
        if parameters["a"] < 0:
            raise ValueError("a must be greater than 0")
        if parameters["b"] < 0:
            raise ValueError("b must be greater than 0")
        if "y" in parameters:
            params[self.y] = self.y_dummy

        params[self.a] = self.a_dummy
        params[self.b] = self.b_dummy

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
        alpha, beta, gamma = params
        if alpha <= 0 or beta <= 0:
            return np.inf
        if any(x <= gamma for x in data):
            return np.inf
        n = len(data)
        term1 = n * (np.log(alpha) - alpha * np.log(beta))
        term2 = (alpha - 1) * np.sum(np.log(data - gamma))
        term3 = np.sum(((data - gamma) / beta) ** alpha)
        return -(term1 + term2 - term3)

    @singledispatchmethod
    def fit(self, data: List, initial: Tuple = (1, 1, 0), method: str = "Default"):
        """Estimate the parameters alpha, beta and gamma using Maximum Likelihood Estimation (MLE).

        Args:
            data (List): A list of observed data points.
            initial (Tuple): Initial guess for the parameters (alpha, beta, gamma).
            method (str): Optimization method to use (e.g., 'Nelder-Mead', 'BFGS'). If 'Default', uses default method of scipy's minimize.

        """
        minimize_kwargs = {
            "fun": self._negloglik,
            "x0": initial,
            "bounds": [(1e-6, None), (1e-6, None), (None, min(data) - 1e-6)],
            "args": (np.array(data),),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        result = minimize(**minimize_kwargs)

        if result.success:
            return {
                "a": float(result.x[0]),
                "b": float(result.x[1]),
                "y": float(result.x[2]),
            }
        else:
            print(result)
            raise ValueError("Parameter estimation failed")

    @fit.register
    def _(self, data: tuple, initial: Tuple = (1, 1, 0), method: str = "Default"):
        """Estimate the parameters using Maximum Likelihood Estimation (MLE)
        for censored data.

        Args:
            data (tuple): A tuple containing two lists - observed
            times and event indicators.
            initial (Tuple): Initial guess for the parameters (alpha, beta, gamma).
            method (str): Optimization method to use.
        Returns:
            dict: A dictionary containing the estimated parameters.
        """
        times = np.asarray(data[0])
        events = np.asarray(data[1])

        def negloglik_censored(params, times, events):
            alpha, beta, gamma = params
            if alpha <= 0 or beta <= 0:
                return np.inf
            if any(x <= gamma for x in times):
                return np.inf

            f = self._pdf(times, alpha, beta, gamma)
            S = self._sf(times, alpha, beta, gamma)

            f = np.maximum(np.array(f, dtype=float), 1e-300)
            S = np.maximum(np.array(S, dtype=float), 1e-300)
            loglik = np.sum(events * np.log(f) + (1 - events) * np.log(S))
            return -loglik

        if initial is None:
            initial = (1, 1, 0)
        minimize_kwargs = {
            "fun": negloglik_censored,
            "x0": initial,
            "bounds": [
                (1e-6, None),
                (1e-6, None),
                (None, min(times) - 1e-6),
            ],
            "args": (times, events),
        }

        if method.upper() != "DEFAULT":
            minimize_kwargs["method"] = method
        self.method = method.upper()
        res = minimize(**minimize_kwargs)

        return {
            "a": float(res.x[0]),
            "b": float(res.x[1]),
            "y": float(res.x[2]),
        }


if __name__ == "__main__":
    pass
else:
    from .utils import (
        binomial_coefficient,
        is_expr_nan,
        primera_expr_cond,
    )
