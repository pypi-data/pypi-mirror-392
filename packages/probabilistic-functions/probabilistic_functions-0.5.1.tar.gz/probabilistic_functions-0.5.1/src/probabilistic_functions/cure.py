import numpy as np
import sympy
from sympy import symbols, exp
from scipy.optimize import minimize
from sympy import lambdify
from .utils import make_transforms_from_bounds
import numdifftools as nd
import numpy as np
from scipy.special import expit, logit


class CureModel:
    def __init__(self, base_model):
        """
        Modelo genérico de supervivencia con población curada.
        base_model: instancia de un modelo base (e.g., Exponential(), Weibull(), etc.)
        """
        self.base = base_model
        self.p = symbols("p", real=True)
        self.x = self.base.x
        self._mode = self.base.get_mode
        self.method = None
        self.params_ = None

        if hasattr(self.base, "bounds"):
            self.bounds = self.base.bounds
        else:
            self.bounds = []
        # asignamos referencias (pero no las serializaremos)
        self._pdf = getattr(self.base, "_pdf", None)
        self._sf = getattr(self.base, "_sf", None)

        """
        self._pdf = lambdify(
            (self.x, *self.base.base_symbols),
            self.base.PDF(),
            modules=["numpy"],
        )
        self._sf = lambdify(
            (self.x, *self.base.base_symbols),
            self.base.SF(),
            modules=["numpy"],
        )
        """

    # =================================================================
    # Serialización controlada: no serializar funciones no-picklables
    # =================================================================
    def __getstate__(self):
        state = self.__dict__.copy()
        # quitamos referencias a funciones que pueden no ser picklables
        # (las reconstruiremos en __setstate__)
        for key in ("_pdf", "_sf"):
            if key in state:
                del state[key]
        return state

    def __setstate__(self, state):
        # restauramos atributos
        self.__dict__.update(state)

        # tratamos de reconstruir funciones desde base si es posible
        # si base implementó su propio __setstate__/__getstate__, esto funcionará
        try:
            self._pdf = getattr(self.base, "_pdf")
            self._sf = getattr(self.base, "_sf")
        except Exception:
            # Si base no tiene _pdf/_sf (o no es picklable),
            # intentamos crear lambdify a partir de las expresiones simbólicas
            # (esto requiere que base tenga PDF() y SF() definidas simbólicamente)
            try:
                from sympy import lambdify

                # reconstrucción segura: envolver en try/except porque puede fallar
                raw_pdf = lambdify(
                    (self.x, *getattr(self.base, "base_symbols", ())),
                    self.base.PDF(),
                    modules=["numpy"],
                )
                raw_sf = lambdify(
                    (self.x, *getattr(self.base, "base_symbols", ())),
                    self.base.SF(),
                    modules=["numpy"],
                )
                # Asignamos funciones "simples" (globales)
                self._pdf = lambda x_val, *params: raw_pdf(x_val, *params)
                self._sf = lambda x_val, *params: raw_sf(x_val, *params)
            except Exception:
                # si tampoco podemos lambdify, dejamos None para detectar error más abajo
                self._pdf = None
                self._sf = None

    # =================================================================
    # Helper para validar que _pdf/_sf están disponibles en tiempo de ejecución
    # =================================================================
    def _ensure_pdf_sf(self):
        if self._pdf is None or self._sf is None:
            # intento de reparación: reasignar desde self.base si existe
            self._pdf = getattr(self.base, "_pdf", None)
            self._sf = getattr(self.base, "_sf", None)
            if self._pdf is None or self._sf is None:
                raise RuntimeError(
                    "CureModel: _pdf/_sf no están disponibles; "
                    "asegúrese de que el modelo base sea reconstruible o picklable."
                )

    def PDF(self):
        """
        f(t) = (1 - p) * f0(t)
        """
        return (1 - self.p) * self.base.PDF()

    def SF(self):
        """
        S(t) = p + (1 - p) * S0(t)
        """
        return self.p + (1 - self.p) * self.base.SF()

    def CDF(self):
        """
        F(t) = 1 - S(t)
        """
        return 1 - self.SF()

    def HF(self):
        """
        h(t) = f(t) / S(t)
        """
        return self.PDF() / self.SF()

    def replace(self, parameters, function="PDF"):
        """
        Sustituye parámetros en las funciones simbólicas del modelo con cura,
        aprovechando la función 'replace' del modelo base.
        """
        function = function.upper()
        valid = {"PDF", "SF", "CDF", "HF"}

        if function not in valid:
            raise ValueError(f"Función inválida. Debe ser una de {valid}")

        # Generar la expresión del modelo de cura en términos simbólicos
        if function == "PDF":
            expr = (1 - self.p) * self.base.replace(parameters, function="PDF")
        elif function == "SF":
            expr = self.p + (1 - self.p) * self.base.replace(parameters, function="SF")
        elif function == "CDF":
            expr = 1 - (
                self.p + (1 - self.p) * self.base.replace(parameters, function="SF")
            )
        elif function == "HF":
            expr = ((1 - self.p) * self.base.replace(parameters, function="PDF")) / (
                self.p + (1 - self.p) * self.base.replace(parameters, function="SF")
            )

        expr = expr.subs(self.p, parameters.get("p_c", self.p))
        parameters = {k: v for k, v in parameters.items() if k != "p_c"}
        return expr.subs(parameters)

    @property
    def get_name(self):
        return self.base.get_name

    @property
    def get_mode(self):
        return self.base.get_mode

    def hessian_se_nat(neg_loglik_fn, theta_int_hat, from_internal, eps=1e-5, reg=1e-8):
        try:
            H = nd.Hessian(neg_loglik_fn, step=eps, method="central")(theta_int_hat)
            H_reg = H + reg * np.eye(H.shape[0])
            cond = np.linalg.cond(H_reg)
            if cond > 1e12:
                print("Hessian is ill-conditioned")
                return None, None, cond
            print(H_reg)
            vcov_int = np.linalg.inv(H_reg)
            # Delta method
            base_nat = from_internal(theta_int_hat)
            p = len(theta_int_hat)
            J = np.zeros((p, p))
            for i in range(p):
                thp = theta_int_hat.copy()
                thp[i] += eps
                natp = from_internal(thp)
                J[:, i] = (natp - base_nat) / eps
            cov_nat = J @ vcov_int @ J.T
            se_nat = np.sqrt(np.abs(np.diag(cov_nat)))
            return se_nat, cov_nat, cond
        except Exception:
            return None, None, None

    def parametric_bootstrap_se(
        self, theta_nat_hat, times, events, base_param_names, n_obs, B=30, rng=None
    ):
        if rng is None:
            rng = np.random.default_rng()
        ests = []
        for _ in range(B):
            if hasattr(self.base, "rvs"):
                sim = self.base.rvs(size=n_obs, params=theta_nat_hat, random_state=rng)
                times_b, events_b = sim["times"], sim["events"]
            else:
                idx = rng.integers(0, n_obs, size=n_obs)
                times_b, events_b = times[idx], events[idx]
            out = self.__class__(base=self.base).fit(
                times_b, events_b, n_total=None, max_iter=150, tol=1e-6
            )
            ests.append([out[k] for k in base_param_names if k in out])
        ests = np.array(ests)
        return np.nanstd(ests, axis=0, ddof=1)

    def neg_loglik(self, times, events, theta_int, p, from_internal, eps=1e-300):
        theta_nat = from_internal(theta_int)
        f = np.maximum(self._pdf(times, *theta_nat), 1e-300)
        S = np.maximum(self._sf(times, *theta_nat), 1e-300)
        ll = np.sum(events * (np.log(1 - p + eps) + np.log(f))) + np.sum(
            (1 - events) * np.log(p + (1 - p) * S)
        )
        return -ll

    def fit(
        self,
        times,
        events,
        n_total=None,
        p_init=None,
        max_iter=200,
        tol=1e-7,
        verbose=False,
    ):
        times = np.asarray(times, dtype=float)
        events = np.asarray(events, dtype=int)
        n = len(times)
        if n == 0:
            raise ValueError("No data provided")

        m = np.sum(events)
        if n_total is None:
            n_total = n
        n_cured = n_total - m

        # Estimación inicial de parámetros base
        results = self.base.fit((times, events))
        base_params = list(results.values())
        base_param_names = list(results.keys())

        if p_init is None:
            p = float(n_cured / n_total) if n_total > 0 else max(1e-3, 1.0 - m / n)
        else:
            p = float(p_init)
        theta = np.array(base_params, dtype=float)

        eps = 1e-300
        prev_ll = -np.inf
        converged = False

        def get_f_S(theta_vec):
            f = np.maximum(np.array(self._pdf(times, *theta_vec), dtype=float), 1e-300)
            S = np.maximum(np.array(self._sf(times, *theta_vec), dtype=float), 1e-300)
            return f, S

        def negQ(theta_vec, w):
            f, S = get_f_S(theta_vec)
            if np.any(f <= 0) or np.any(S <= 0):
                return np.inf
            ll_events = np.sum(events * np.log(f + eps))
            ll_cens = np.sum((1 - events) * w * np.log(S + eps))
            return -(ll_events + ll_cens)

        if len(self.bounds) == 0:
            if self.base.get_name == "Pareto 1":
                self.bounds = [(min(times), min(times) + 1e-6), (1e-6, None)]
            elif self.base.get_name in ["Birnbaum-Saunders", "Weibull 3-Parameters"]:
                self.bounds = [(1e-6, None), (1e-6, None), (None, min(times) - 1e-6)]

        # --- EM ---
        for it in range(1, max_iter + 1):
            f, S = get_f_S(theta)
            denom = p + (1 - p) * S
            denom = np.maximum(denom, eps)
            w = np.where(events == 1, 1.0, (1 - p) * S / denom)

            p_new = np.clip(np.mean(1 - w), 1e-9, 1 - 1e-9)

            res = minimize(
                fun=negQ,
                x0=theta,
                args=(w,),
                method="L-BFGS-B",
                bounds=self.bounds,
                options={"maxiter": 200, "ftol": 1e-9},
            )
            # if not res.success:
            # print(f"Advertencia: optimización fallida en iter {it}, {res.message}")
            theta_new = res.x

            f, S = get_f_S(theta_new)
            ll = np.sum(events * (np.log(1 - p_new + eps) + np.log(f + eps))) + np.sum(
                (1 - events) * np.log(p_new + (1 - p_new) * S + eps)
            )

            if verbose and (it == 1 or it % 10 == 0):
                th_str = ", ".join(
                    f"{n}={v:.4g}" for n, v in zip(base_param_names, theta_new)
                )
                print(f"iter {it:3d} ll={ll:.6f} p={p_new:.4f} theta=[{th_str}]")

            if abs(ll - prev_ll) < tol:
                converged = True
                theta, p = theta_new, p_new
                break

            theta, p = theta_new, p_new
            prev_ll = ll

        # --- Cálculo de SE ---

        to_internal, from_internal = make_transforms_from_bounds(self.bounds)

        def neg_loglik(theta_int):
            theta_nat = from_internal(theta_int)
            f = np.maximum(self._pdf(times, *theta_nat), 1e-300)
            S = np.maximum(self._sf(times, *theta_nat), 1e-300)
            ll = np.sum(events * (np.log(1 - p + eps) + np.log(f))) + np.sum(
                (1 - events) * np.log(p + (1 - p) * S)
            )
            return -ll

        theta_int_hat = to_internal(theta)
        se_nat, cov_nat, cond = self.hessian_se_nat(
            neg_loglik, theta_int_hat, from_internal
        )

        params = dict(zip(base_param_names, theta))
        params["p_c"] = p
        self.params_ = params
        self.method = "EM"

        return {
            "p_c": p,
            **{k: v for k, v in zip(base_param_names, theta)},
            "loglik": ll,
            "iter": it,
            "converged": converged,
            "se": se_nat,
        }
