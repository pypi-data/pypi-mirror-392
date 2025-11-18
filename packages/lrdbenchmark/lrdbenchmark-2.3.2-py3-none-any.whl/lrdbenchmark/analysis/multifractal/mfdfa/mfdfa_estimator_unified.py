#!/usr/bin/env python3
"""
Unified Multifractal Detrended Fluctuation Analysis (MFDFA) Estimator.

This module implements the MFDFA estimator with automatic optimization framework
selection (JAX, Numba, NumPy) for the best performance on the available hardware.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import detrend
from typing import Dict, Any, Optional, Union, Tuple, List, Callable
import warnings

from lrdbenchmark.analysis.backend_utils import select_backend, JAX_AVAILABLE, NUMBA_AVAILABLE
from lrdbenchmark.analysis.calibration_utils import apply_srd_bias_correction

# Import optimization frameworks
if JAX_AVAILABLE:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap
if NUMBA_AVAILABLE:
    import numba
    from numba import jit as numba_jit, prange
else:
    # Create a dummy decorator when numba is not available
    def numba_jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range  # Dummy prange

# Import base estimator
try:
    from lrdbenchmark.analysis.base_estimator import BaseEstimator
except ImportError:
    from lrdbenchmark.analysis.base_estimator import BaseEstimator


# Numba-compatible polynomial fitting functions (only when Numba is available)
if NUMBA_AVAILABLE:
    @numba_jit(nopython=True)
    def _polyfit_numba(x: np.ndarray, y: np.ndarray, deg: int) -> np.ndarray:
        """Numba-compatible polyfit using Vandermonde matrix and least squares."""
        n = len(x)
        m = deg + 1
        
        # Build Vandermonde matrix
        V = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                V[i, j] = x[i] ** (m - 1 - j)
        
        # Solve using normal equations: (V^T V) coeffs = V^T y
        VtV = np.zeros((m, m))
        Vty = np.zeros(m)
        
        for i in range(m):
            for j in range(m):
                VtV[i, j] = 0.0
                for k in range(n):
                    VtV[i, j] += V[k, i] * V[k, j]
            Vty[i] = 0.0
            for k in range(n):
                Vty[i] += V[k, i] * y[k]
        
        # Solve linear system using Gaussian elimination (simple version)
        coeffs = np.zeros(m)
        A = VtV.copy()
        b = Vty.copy()
        
        # Forward elimination
        for i in range(m):
            # Find pivot
            max_row = i
            for k in range(i + 1, m):
                if abs(A[k, i]) > abs(A[max_row, i]):
                    max_row = k
            # Swap rows (element by element for Numba compatibility)
            for j in range(m):
                temp = A[i, j]
                A[i, j] = A[max_row, j]
                A[max_row, j] = temp
            temp_b = b[i]
            b[i] = b[max_row]
            b[max_row] = temp_b
            
            # Eliminate
            for k in range(i + 1, m):
                if A[i, i] != 0:
                    factor = A[k, i] / A[i, i]
                    for j in range(i, m):
                        A[k, j] -= factor * A[i, j]
                    b[k] -= factor * b[i]
        
        # Back substitution
        for i in range(m - 1, -1, -1):
            coeffs[i] = b[i]
            for j in range(i + 1, m):
                coeffs[i] -= A[i, j] * coeffs[j]
            if A[i, i] != 0:
                coeffs[i] /= A[i, i]
            else:
                coeffs[i] = 0.0
        
        return coeffs

    @numba_jit(nopython=True)
    def _polyval_numba(p: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Numba-compatible polyval."""
        n = len(x)
        m = len(p)
        y = np.zeros(n)
        
        for i in range(n):
            for j in range(m):
                y[i] += p[j] * (x[i] ** (m - 1 - j))
        
        return y

    @numba_jit(nopython=True, parallel=True)
    def _compute_fluctuation_function_numba(data, q, scale, order):
        """Numba-jitted fluctuation calculation for MFDFA."""
        n_segments = len(data) // scale
        if n_segments == 0:
            return np.nan

        variances = np.zeros(n_segments)
        for i in prange(n_segments):
            start_idx = i * scale
            end_idx = start_idx + scale
            segment = data[start_idx:end_idx]
            
            x = np.arange(scale, dtype=np.float64)
            if order == 0:
                detrended = segment - np.mean(segment)
            else:
                coeffs = _polyfit_numba(x, segment, order)
                trend = _polyval_numba(coeffs, x)
                detrended = segment - trend
            
            variances[i] = np.mean(detrended**2)

        if q == 0:
            return np.exp(0.5 * np.mean(np.log(variances)))
        else:
            return np.mean(variances ** (q / 2)) ** (1 / q)


class MFDFAEstimator(BaseEstimator):
    """
    Unified Multifractal Detrended Fluctuation Analysis (MFDFA) Estimator.

    MFDFA extends DFA to analyze multifractal properties by computing
    fluctuation functions for different moments q.

    Features:
    - Automatic optimization framework selection (JAX, Numba, NumPy)
    - GPU acceleration with JAX when available
    - JIT compilation with Numba for CPU optimization
    - Graceful fallbacks when optimization frameworks fail

    Parameters
    ----------
    q_values : List[float], optional (default=None)
        List of q values for multifractal analysis. Default: [-5, -3, -1, 0, 1, 2, 3, 5]
    scales : List[int], optional (default=None)
        List of scales for analysis. If None, will be generated from min_scale to max_scale
    min_scale : int, optional (default=8)
        Minimum scale for analysis
    max_scale : int, optional (default=50)
        Maximum scale for analysis
    num_scales : int, optional (default=15)
        Number of scales to use if scales is None
    order : int, optional (default=1)
        Order of polynomial for detrending
    use_optimization : str, optional (default='auto')
        Optimization framework to use: 'auto', 'jax', 'numba', 'numpy'
    """

    def __init__(
        self,
        q_values: Optional[List[float]] = None,
        scales: Optional[List[int]] = None,
        min_scale: int = 8,
        max_scale: int = 50,
        num_scales: int = 15,
        order: int = 1,
        use_optimization: str = "auto",
        confidence: float = 0.95,
        bootstrap_samples: int = 64,
        bootstrap_block_size: Optional[int] = None,
    ):
        super().__init__()
        
        # Set default q_values if not provided
        if q_values is None:
            q_values = [-5, -3, -1, 0, 1, 2, 3, 5]

        if not (0 < confidence < 1):
            raise ValueError("confidence must be between 0 and 1")

        # Set default scales if not provided
        if scales is None:
            scales = np.logspace(
                np.log10(min_scale), np.log10(max_scale), num_scales, dtype=int
            )
        
        # Estimator parameters
        self.parameters = {
            "q_values": q_values,
            "scales": scales,
            "min_scale": min_scale,
            "max_scale": max_scale,
            "num_scales": num_scales,
            "order": order,
            "confidence": float(confidence),
            "bootstrap_samples": int(max(0, bootstrap_samples)),
            "bootstrap_block_size": bootstrap_block_size,
        }
        
        # Optimization framework
        self.optimization_framework = select_backend(use_optimization)
        
        # Results storage
        self.results = {}
        
        # Validation
        self._validate_parameters()

    def estimate(self, data: Union[np.ndarray, list]) -> Dict[str, Any]:
        """
        Estimate multifractal properties using MFDFA with automatic optimization.

        Parameters
        ----------
        data : array-like
            Time series data to analyze

        Returns
        -------
        dict
            Dictionary containing:
            - 'hurst_parameter': Estimated Hurst exponent (q=2)
            - 'generalized_hurst': Dictionary of generalized Hurst exponents for each q
            - 'multifractal_spectrum': Dictionary with f(alpha) and alpha values
            - 'scales': List of scales used
            - 'q_values': List of q values used
            - 'fluctuation_functions': Dictionary of Fq(s) for each q
        """
        data = np.asarray(data)
        n = len(data)

        if n < 100:
            warnings.warn("Data length is small, results may be unreliable")

        # Select optimal method based on data size and framework
        backend = self.optimization_framework
        if backend == "jax":
            try:
                return self._estimate_jax(data)
            except Exception as e:
                warnings.warn(f"JAX implementation failed: {e}, falling back to NumPy")
                return self._estimate_numpy(data)
        elif backend == "numba":
            try:
                return self._estimate_numba(data)
            except Exception as e:
                warnings.warn(f"Numba implementation failed: {e}, falling back to NumPy")
                return self._estimate_numpy(data)
        else: # numpy
            return self._estimate_numpy(data)

    def _estimate_numba(self, data: np.ndarray) -> Dict[str, Any]:
        """Numba-optimized implementation of MFDFA estimation."""
        max_safe_scale = min(self.parameters["max_scale"], len(data) // 4)
        if max_safe_scale < self.parameters["min_scale"]:
            raise ValueError(f"Data length {len(data)} is too short for MFDFA analysis")
        
        if max_safe_scale < self.parameters["max_scale"]:
            safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
            if len(safe_scales) >= 3:
                self.parameters["scales"] = np.array(safe_scales)
                self.parameters["max_scale"] = max_safe_scale

        scales = np.array(self.parameters["scales"])
        q_values = np.array(self.parameters["q_values"])
        order = self.parameters["order"]

        fluctuation_functions: Dict[float, np.ndarray] = {}
        for q in q_values:
            fq_values = np.zeros(len(scales))
            for i in range(len(scales)):
                fq_values[i] = _compute_fluctuation_function_numba(data, q, scales[i], order)
            fluctuation_functions[q] = fq_values

        generalized_hurst = {}
        log_scales = np.log(scales)

        for q in q_values:
            fq_vals = fluctuation_functions[q]
            valid_mask = ~np.isnan(fq_vals) & (fq_vals > 0)
            if np.sum(valid_mask) < 3:
                generalized_hurst[q] = np.nan
                continue

            log_fq = np.log(fq_vals[valid_mask])
            log_s = log_scales[valid_mask]

            try:
                slope, intercept, r_value, _, _ = stats.linregress(log_s, log_fq)
                generalized_hurst[q] = slope
            except (ValueError, np.linalg.LinAlgError):
                generalized_hurst[q] = np.nan
        
        hurst_parameter = generalized_hurst.get(2, np.nan)
        multifractal_spectrum = self._compute_multifractal_spectrum(generalized_hurst, q_values.tolist())

        self.results = {
            "hurst_parameter": float(hurst_parameter) if not np.isnan(hurst_parameter) else np.nan,
            "generalized_hurst": {q: float(h) if not np.isnan(h) else np.nan for q, h in generalized_hurst.items()},
            "multifractal_spectrum": multifractal_spectrum,
            "scales": scales.tolist(),
            "q_values": q_values.tolist(),
            "fluctuation_functions": {q: fq.tolist() for q, fq in fluctuation_functions.items()},
            "method": "numba",
            "optimization_framework": self.optimization_framework,
        }
        return self.results

    def _finalize_results_from_fq(
        self,
        data: np.ndarray,
        scales: Union[np.ndarray, List[int]],
        q_values: Union[np.ndarray, List[float]],
        fluctuation_functions: Dict[float, np.ndarray],
        segment_stats_q2: Optional[Dict[int, Dict[str, float]]] = None,
        compute_ci: bool = True,
        method_label: str = "numpy",
    ) -> Dict[str, Any]:
        """Shared post-processing for converting fluctuation functions into estimator results."""
        scales_array = np.asarray(scales)
        q_array = np.asarray(q_values, dtype=float)

        generalized_hurst: Dict[float, float] = {}
        log_scales = np.log(scales_array)
        hurst_confidence_interval: Optional[Tuple[float, float]] = None
        hurst_weights: Optional[List[float]] = None
        hurst_intercept: Optional[float] = None
        hurst_r_squared: Optional[float] = None

        stats_q2 = segment_stats_q2 or {}

        for q in q_array:
            q_key = float(q)
            fq_vals = np.asarray(fluctuation_functions.get(q_key, np.nan), dtype=float)
            valid_mask = ~np.isnan(fq_vals) & (fq_vals > 0)

            if np.sum(valid_mask) < 3:
                generalized_hurst[q_key] = np.nan
                continue

            log_fq = np.log(fq_vals[valid_mask])
            log_s = log_scales[valid_mask]

            try:
                if np.isclose(q_key, 2.0):
                    variance_logs = []
                    for scale_val in np.asarray(scales_array)[valid_mask]:
                        stats_entry = stats_q2.get(int(scale_val))
                        if (
                            stats_entry is None
                            or stats_entry["mean"] <= 0
                            or stats_entry["n"] < 1
                        ):
                            variance_logs.append(0.01)
                            continue

                        mean_var = stats_entry["mean"]
                        seg_var = stats_entry["var"]
                        if seg_var <= 0:
                            seg_var = 0.25 * mean_var**2
                        var_mean = seg_var / max(stats_entry["n"], 1)
                        var_log = (0.5 / mean_var) ** 2 * var_mean
                        variance_logs.append(max(var_log, 1e-12))

                    (
                        slope,
                        intercept,
                        r_sq,
                        slope_se,
                        weights,
                    ) = self._weighted_regression(
                        log_s, log_fq, np.array(variance_logs, dtype=float)
                    )
                    generalized_hurst[q_key] = slope
                    hurst_confidence_interval = self._get_hurst_confidence_interval(
                        slope, slope_se, len(log_s)
                    )
                    hurst_weights = weights.tolist()
                    hurst_intercept = float(intercept)
                    hurst_r_squared = float(r_sq)
                else:
                    slope, intercept, r_value, _, _ = stats.linregress(
                        log_s, log_fq
                    )
                    generalized_hurst[q_key] = slope
            except (ValueError, np.linalg.LinAlgError):
                generalized_hurst[q_key] = np.nan

        hurst_parameter = generalized_hurst.get(2.0, np.nan)
        multifractal_spectrum = self._compute_multifractal_spectrum(
            generalized_hurst, q_array
        )

        if (
            compute_ci
            and self.parameters["bootstrap_samples"] > 0
            and not np.isnan(hurst_parameter)
        ):
            bootstrap_ci = self._bootstrap_confidence_interval(data)
            if bootstrap_ci is not None:
                hurst_confidence_interval = bootstrap_ci

        corrected_hurst, applied_bias = apply_srd_bias_correction(
            "MFDFA", float(hurst_parameter) if not np.isnan(hurst_parameter) else float("nan")
        )
        if applied_bias != 0.0 and hurst_confidence_interval is not None:
            lower = max(0.01, min(0.99, hurst_confidence_interval[0] - applied_bias))
            upper = max(0.01, min(0.99, hurst_confidence_interval[1] - applied_bias))
            hurst_confidence_interval = (lower, upper)
        hurst_parameter = corrected_hurst

        result = {
            "hurst_parameter": float(hurst_parameter) if not np.isnan(hurst_parameter) else np.nan,
            "generalized_hurst": {
                float(q): float(h) if not np.isnan(h) else np.nan
                for q, h in generalized_hurst.items()
            },
            "multifractal_spectrum": multifractal_spectrum,
            "scales": scales_array.tolist(),
            "q_values": q_array.tolist(),
            "fluctuation_functions": {
                float(q): np.asarray(fq, dtype=float).tolist()
                for q, fq in fluctuation_functions.items()
            },
            "confidence_interval": hurst_confidence_interval,
            "hurst_regression_details": {
                "weights": hurst_weights,
                "intercept": hurst_intercept,
                "r_squared": hurst_r_squared,
            },
            "bias_correction": applied_bias,
            "method": method_label,
            "optimization_framework": self.optimization_framework,
        }

        self.results = result
        return result

    def _estimate_numpy(self, data: np.ndarray, compute_ci: bool = True) -> Dict[str, Any]:
        """NumPy implementation of MFDFA estimation."""
        # Adjust scales for data length
        max_safe_scale = min(self.parameters["max_scale"], len(data) // 4)
        if max_safe_scale < self.parameters["min_scale"]:
            raise ValueError(f"Data length {len(data)} is too short for MFDFA analysis")
        
        # Update scales if needed
        if max_safe_scale < self.parameters["max_scale"]:
            safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
            if len(safe_scales) >= 3:
                self.parameters["scales"] = np.array(safe_scales)
                self.parameters["max_scale"] = max_safe_scale
            else:
                warnings.warn(
                    f"Data length ({len(data)}) may be too short for reliable MFDFA analysis"
                )

        scales = self.parameters["scales"]
        q_values = self.parameters["q_values"]

        # Pre-compute segment statistics for q=2 intervals
        segment_stats_q2 = (
            self._compute_segment_stats(data, scales)
            if 2 in np.asarray(q_values)
            else {}
        )

        # Compute fluctuation functions for all q and scales
        fluctuation_functions: Dict[float, np.ndarray] = {}
        for q in q_values:
            fq_values = []
            for scale in scales:
                fq = self._compute_fluctuation_function(data, q, scale)
                fq_values.append(fq)
            fluctuation_functions[float(q)] = np.array(fq_values, dtype=float)

        return self._finalize_results_from_fq(
            data,
            scales,
            q_values,
            fluctuation_functions,
            segment_stats_q2=segment_stats_q2,
            compute_ci=compute_ci,
            method_label="numpy",
        )

    def _compute_segment_stats(
        self, data: np.ndarray, scales: Union[np.ndarray, List[int]]
    ) -> Dict[int, Dict[str, float]]:
        """Collect per-scale segment variance statistics for q=2 uncertainty estimates."""
        stats: Dict[int, Dict[str, float]] = {}
        scales_array = np.asarray(scales, dtype=int)
        for scale in scales_array:
            n_segments = len(data) // scale
            if n_segments < 2:
                continue
            segments = data[: n_segments * scale].reshape(n_segments, scale)
            seg_vars = []
            for segment in segments:
                detrended = self._detrend_series(segment, scale, self.parameters["order"])
                seg_vars.append(float(np.mean(detrended**2)))
            if not seg_vars:
                continue
            seg_vars_arr = np.asarray(seg_vars, dtype=float)
            stats[int(scale)] = {
                "mean": float(np.mean(seg_vars_arr)),
                "var": float(np.var(seg_vars_arr, ddof=1)) if len(seg_vars_arr) > 1 else 0.0,
                "n": int(len(seg_vars_arr)),
            }
        return stats

    def _bootstrap_confidence_interval(
        self,
        data: np.ndarray,
    ) -> Optional[Tuple[float, float]]:
        """Approximate Hurst confidence interval using circular block bootstrap."""
        n_boot = self.parameters.get("bootstrap_samples", 0)
        if n_boot <= 0:
            return None

        estimates: List[float] = []
        n = len(data)
        block_size = self.parameters.get("bootstrap_block_size")
        if block_size is None:
            block_size = max(32, n // 4)
        block_size = min(max(8, block_size), n)

        scales_snapshot = (
            list(self.parameters["scales"])
            if isinstance(self.parameters.get("scales"), (list, np.ndarray))
            else None
        )

        for _ in range(n_boot):
            resampled = self._circular_block_resample(data, block_size)
            try:
                replicate = self._estimate_numpy(
                    resampled,
                    compute_ci=False,
                )
                est = replicate.get("hurst_parameter")
                if est is not None and np.isfinite(est):
                    estimates.append(float(est))
            except Exception:
                continue
            finally:
                if scales_snapshot is not None:
                    self.parameters["scales"] = list(scales_snapshot)

        if len(estimates) < max(8, n_boot // 4):
            return None

        alpha = 1.0 - self.parameters.get("confidence", 0.95)
        lower = float(np.percentile(estimates, 100 * (alpha / 2)))
        upper = float(np.percentile(estimates, 100 * (1 - alpha / 2)))
        return (lower, upper)

    def _circular_block_resample(self, data: np.ndarray, block_size: int) -> np.ndarray:
        """Generate circular block bootstrap resample."""
        n = len(data)
        n_blocks = max(1, int(np.ceil(n / block_size)))
        resampled = np.empty(n, dtype=float)
        pos = 0
        for _ in range(n_blocks):
            start = np.random.randint(0, n)
            block = np.take(
                data,
                np.arange(start, start + block_size) % n,
                mode="wrap",
            )
            length = min(block_size, n - pos)
            resampled[pos : pos + length] = block[:length]
            pos += length
            if pos >= n:
                break
        return resampled

    def _weighted_regression(
        self,
        x: np.ndarray,
        y: np.ndarray,
        y_variances: np.ndarray,
    ) -> Tuple[float, float, float, float, np.ndarray]:
        """Perform weighted linear regression with variance-informed weights."""
        weights = 1.0 / np.clip(y_variances, 1e-12, None)
        X = np.column_stack((np.ones_like(x), x))
        XtWX = X.T @ (weights[:, None] * X)
        XtWy = X.T @ (weights * y)
        beta = np.linalg.solve(XtWX, XtWy)
        intercept, slope = beta
        y_hat = X @ beta
        residuals = y - y_hat
        dof = max(len(x) - 2, 1)
        ss_res = float(np.sum(weights * residuals**2))
        y_mean = np.average(y, weights=weights)
        ss_tot = float(np.sum(weights * (y - y_mean) ** 2))
        r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        sigma2 = ss_res / dof if dof > 0 else 0.0
        if sigma2 < 1e-10:
            sigma2 = np.mean(1.0 / weights)
        cov_beta = sigma2 * np.linalg.inv(XtWX)
        slope_se = float(np.sqrt(max(cov_beta[1, 1], 1e-12)))
        return float(slope), float(intercept), float(r_squared), slope_se, weights

    def _get_hurst_confidence_interval(
        self, hurst_estimate: float, slope_se: float, n_points: int
    ) -> Tuple[float, float]:
        """Construct confidence interval for the Hurst exponent."""
        confidence = self.parameters.get("confidence", 0.95)
        dof = max(n_points - 2, 1)
        t_value = stats.t.ppf((1 + confidence) / 2, df=dof)
        margin = float(t_value * slope_se)
        lower = float(hurst_estimate - margin)
        upper = float(hurst_estimate + margin)
        return (lower, upper)

    def _estimate_jax(self, data: np.ndarray) -> Dict[str, Any]:
        """JAX-optimized implementation of MFDFA estimation."""
        if not JAX_AVAILABLE:
            warnings.warn("JAX backend requested but not available; falling back to NumPy.")
            return self._estimate_numpy(data)

        data_np = np.asarray(data, dtype=float)

        max_safe_scale = min(self.parameters["max_scale"], len(data_np) // 4)
        if max_safe_scale < self.parameters["min_scale"]:
            raise ValueError(f"Data length {len(data_np)} is too short for MFDFA analysis")

        if max_safe_scale < self.parameters["max_scale"]:
            safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
            if len(safe_scales) >= 3:
                self.parameters["scales"] = np.array(safe_scales)
                self.parameters["max_scale"] = max_safe_scale
            else:
                warnings.warn(
                    f"Data length ({len(data_np)}) may be too short for reliable MFDFA analysis"
                )

        scales = np.asarray(self.parameters["scales"], dtype=int)
        q_values = np.asarray(self.parameters["q_values"], dtype=float)
        order = int(self.parameters["order"])

        if scales.ndim == 0:
            scales = np.array([int(scales)], dtype=int)
        if q_values.ndim == 0:
            q_values = np.array([float(q_values)], dtype=float)

        data_jax = jnp.asarray(data_np, dtype=jnp.float64)

        variance_functions: Dict[int, Callable[[Any], Any]] = {}
        variance_cache: Dict[int, Optional[Any]] = {}

        def build_variance_fn(scale: int):
            x = jnp.arange(scale, dtype=data_jax.dtype)

            if order == 0:
                def compute(segments: Any) -> Any:
                    mean = jnp.mean(segments, axis=1, keepdims=True)
                    detrended = segments - mean
                    return jnp.mean(detrended**2, axis=1)
            else:
                V = jnp.vander(x, order + 1, increasing=False)
                gram = V.T @ V
                gram += 1e-10 * jnp.eye(gram.shape[0], dtype=V.dtype)
                pinv = jnp.linalg.solve(gram, V.T)

                def compute(segments: Any) -> Any:
                    coeffs = segments @ pinv.T
                    trend = coeffs @ V.T
                    detrended = segments - trend
                    return jnp.mean(detrended**2, axis=1)

            return jit(compute)

        for scale_val in scales:
            scale_int = int(scale_val)
            n_segments = len(data_np) // scale_int
            if n_segments == 0:
                variance_cache[scale_int] = None
                continue

            trimmed = data_jax[: n_segments * scale_int]
            segments = trimmed.reshape((n_segments, scale_int))

            variance_fn = variance_functions.get(scale_int)
            if variance_fn is None:
                variance_fn = build_variance_fn(scale_int)
                variance_functions[scale_int] = variance_fn

            variances = variance_fn(segments)
            variance_cache[scale_int] = variances

        fluctuation_functions: Dict[float, np.ndarray] = {}
        for q in q_values:
            q_float = float(q)
            fq_values: List[float] = []
            for scale_val in scales:
                scale_int = int(scale_val)
                variances = variance_cache.get(scale_int)
                if variances is None or variances.size == 0:
                    fq_values.append(np.nan)
                    continue

                safe_var = jnp.clip(variances, 1e-18, None)
                if np.isclose(q_float, 0.0):
                    fq = jnp.exp(0.5 * jnp.mean(jnp.log(safe_var)))
                else:
                    fq = jnp.mean(jnp.power(safe_var, q_float / 2.0)) ** (1.0 / q_float)
                fq_values.append(float(fq))
            fluctuation_functions[q_float] = np.array(fq_values, dtype=float)

        segment_stats_q2 = (
            self._compute_segment_stats(data_np, scales)
            if np.any(np.isclose(q_values, 2.0))
            else {}
        )

        return self._finalize_results_from_fq(
            data_np,
            scales,
            q_values,
            fluctuation_functions,
            segment_stats_q2=segment_stats_q2,
            compute_ci=True,
            method_label="jax",
        )

    def _detrend_series(self, series: np.ndarray, scale: int, order: int) -> np.ndarray:
        """Detrend a series segment using polynomial fitting."""
        if order == 0:
            return series - np.mean(series)
        else:
            x = np.arange(scale)
            coeffs = np.polyfit(x, series, order)
            trend = np.polyval(coeffs, x)
            return series - trend

    def _compute_fluctuation_function(
        self, data: np.ndarray, q: float, scale: int
    ) -> float:
        """Compute fluctuation function for a given q and scale."""
        n_segments = len(data) // scale
        if n_segments == 0:
            return np.nan

        # Reshape data into segments
        segments = data[: n_segments * scale].reshape(n_segments, scale)

        # Compute variance for each segment
        variances = []
        for segment in segments:
            detrended = self._detrend_series(segment, scale, self.parameters["order"])
            variance = np.mean(detrended**2)
            variances.append(variance)

        # Compute q-th order fluctuation function
        if q == 0:
            # Special case for q = 0
            fq = np.exp(0.5 * np.mean(np.log(variances)))
        else:
            fq = np.mean(np.array(variances) ** (q / 2)) ** (1 / q)

        return fq

    def _compute_multifractal_spectrum(
        self, generalized_hurst: Dict[float, float], q_values: List[float]
    ) -> Dict[str, List[float]]:
        """Compute the multifractal spectrum f(alpha) vs alpha."""
        # Filter out NaN values
        valid_q = [
            q for q in q_values if not np.isnan(generalized_hurst.get(q, np.nan))
        ]
        valid_h = [generalized_hurst[q] for q in valid_q]

        if len(valid_q) < 3:
            return {"alpha": [], "f_alpha": []}

        # Compute alpha and f(alpha) using Legendre transform
        alpha = []
        f_alpha = []

        for i in range(1, len(valid_q) - 1):
            # Compute alpha as derivative of h(q)
            dq = valid_q[i + 1] - valid_q[i - 1]
            dh = valid_h[i + 1] - valid_h[i - 1]
            
            if dq != 0:
                alpha_val = valid_h[i] + valid_q[i] * (dh / dq)
                f_alpha_val = valid_q[i] * alpha_val - valid_h[i]
                
                alpha.append(alpha_val)
                f_alpha.append(f_alpha_val)

        return {"alpha": alpha, "f_alpha": f_alpha}

    def get_optimization_info(self) -> Dict[str, Any]:
        """Get information about available optimizations and current selection."""
        return {
            "current_framework": self.optimization_framework,
            "jax_available": JAX_AVAILABLE,
            "numba_available": NUMBA_AVAILABLE,
            "recommended_framework": self._get_recommended_framework()
        }

    def _get_recommended_framework(self) -> str:
        """Get the recommended optimization framework."""
        if JAX_AVAILABLE:
            return "jax"  # Best for GPU acceleration
        elif NUMBA_AVAILABLE:
            return "numba"  # Good for CPU optimization
        else:
            return "numpy"  # Fallback

    def plot_analysis(self, figsize: Tuple[int, int] = (15, 10), save_path: Optional[str] = None) -> None:
        """Plot the MFDFA analysis results."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('MFDFA Analysis Results', fontsize=16)

        # Plot 1: Fluctuation functions for different q values
        ax1 = axes[0, 0]
        scales = self.results["scales"]
        q_values = self.results["q_values"]
        
        for q in q_values:
            if q in self.results["fluctuation_functions"]:
                fq_vals = self.results["fluctuation_functions"][q]
                valid_mask = ~np.isnan(fq_vals) & (fq_vals > 0)
                if np.any(valid_mask):
                    ax1.loglog(np.array(scales)[valid_mask], fq_vals[valid_mask], 
                              'o-', label=f'q={q}', alpha=0.7)
        
        ax1.set_xlabel('Scale (s)')
        ax1.set_ylabel('Fq(s)')
        ax1.set_title('Fluctuation Functions')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Generalized Hurst exponents
        ax2 = axes[0, 1]
        q_vals = list(self.results["generalized_hurst"].keys())
        h_vals = list(self.results["generalized_hurst"].values())
        
        valid_mask = ~np.isnan(h_vals)
        if np.any(valid_mask):
            ax2.plot(np.array(q_vals)[valid_mask], np.array(h_vals)[valid_mask], 
                    'o-', linewidth=2, markersize=8)
            ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='H=0.5 (no memory)')
        
        ax2.set_xlabel('q')
        ax2.set_ylabel('h(q)')
        ax2.set_title('Generalized Hurst Exponents')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Multifractal spectrum
        ax3 = axes[0, 2]
        spectrum = self.results["multifractal_spectrum"]
        if spectrum["alpha"] and spectrum["f_alpha"]:
            ax3.plot(spectrum["alpha"], spectrum["f_alpha"], 'o-', linewidth=2, markersize=8)
            ax3.set_xlabel('α')
            ax3.set_ylabel('f(α)')
            ax3.set_title('Multifractal Spectrum')
            ax3.grid(True, alpha=0.3)

        # Plot 4: Standard Hurst parameter
        ax4 = axes[1, 0]
        hurst = self.results["hurst_parameter"]
        if not np.isnan(hurst):
            ax4.bar(["Hurst Parameter"], [hurst], alpha=0.7, color='skyblue')
            ax4.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='H=0.5 (no memory)')
            ax4.set_ylabel("Hurst Parameter")
            ax4.set_title(f"Standard Hurst Parameter: {hurst:.3f}")
            ax4.legend()
            ax4.grid(True, alpha=0.3)

        # Plot 5: Scale distribution
        ax5 = axes[1, 1]
        ax5.hist(scales, bins=min(10, len(scales)), alpha=0.7, color='lightgreen')
        ax5.set_xlabel('Scale')
        ax5.set_ylabel('Frequency')
        ax5.set_title('Scale Distribution')
        ax5.grid(True, alpha=0.3)

        # Plot 6: Q-values distribution
        ax6 = axes[1, 2]
        ax6.bar(range(len(q_values)), q_values, alpha=0.7, color='orange')
        ax6.set_xlabel('Q Index')
        ax6.set_ylabel('Q Value')
        ax6.set_title('Q Values Used')
        ax6.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()

    def get_method_recommendation(self, n: int) -> Dict[str, Any]:
        """Get method recommendation for a given data size."""
        if n < 100:
            return {
                "recommended_method": "numpy",
                "reasoning": f"Data size n={n} is too small for MFDFA analysis",
                "method_details": {
                    "description": "NumPy implementation",
                    "best_for": "Small datasets (n < 100)",
                    "complexity": "O(n²)",
                    "memory": "O(n)",
                    "accuracy": "Low (insufficient data)"
                }
            }
        elif n < 500:
            return {
                "recommended_method": "numpy",
                "reasoning": f"Data size n={n} is too small for optimization benefits",
                "method_details": {
                    "description": "NumPy implementation",
                    "best_for": "Small datasets (100 ≤ n < 500)",
                    "complexity": "O(n²)",
                    "memory": "O(n)",
                    "accuracy": "Medium"
                }
            }
        elif n < 2000:
            return {
                "recommended_method": "numba",
                "reasoning": f"Data size n={n} benefits from JIT compilation",
                "method_details": {
                    "description": "Numba JIT-compiled implementation",
                    "best_for": "Medium datasets (500 ≤ n < 2000)",
                    "complexity": "O(n²)",
                    "memory": "O(n)",
                    "accuracy": "High"
                }
            }
        else:
            return {
                "recommended_method": "jax",
                "reasoning": f"Data size n={n} benefits from GPU acceleration",
                "method_details": {
                    "description": "JAX GPU-accelerated implementation",
                    "best_for": "Large datasets (n ≥ 2000)",
                    "complexity": "O(n²)",
                    "memory": "O(n)",
                    "accuracy": "High"
                }
            }
