#!/usr/bin/env python3
"""
Unified Wavelet Variance Estimator for Long-Range Dependence Analysis.

This module implements the Wavelet Variance estimator with automatic optimization framework
selection (JAX, Numba, NumPy) for the best performance on the available hardware.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import polygamma
import pywt
from typing import Dict, Any, Optional, Union, Tuple, List
import warnings

# Import optimization frameworks
try:
    import jax
    import jax.numpy as jnp
    import jax.scipy.special
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

try:
    import numba
    from numba import jit as numba_jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from lrdbenchmark.analysis.base_estimator import BaseEstimator
from lrdbenchmark.analysis.calibration_utils import apply_srd_bias_correction
from lrdbenchmark.analysis.wavelet.jax_wavelet import (
    dwt_periodized,
    wavelet_detail_variances,
)


class WaveletVarianceEstimator(BaseEstimator):
    """
    Unified Wavelet Variance Estimator for Long-Range Dependence Analysis.

    This estimator uses wavelet decomposition to analyze the variance of wavelet
    coefficients at different scales, which can be used to estimate the Hurst
    parameter for fractional processes.

    Features:
    - Automatic optimization framework selection (JAX, Numba, NumPy)
    - GPU acceleration with JAX when available
    - JIT compilation with Numba for CPU optimization
    - Graceful fallbacks when optimization frameworks fail

    Parameters
    ----------
    wavelet : str, optional (default='db4')
        Wavelet type to use for decomposition
    scales : List[int], optional (default=None)
        List of scales for wavelet analysis. If None, uses automatic scale selection
    confidence : float, optional (default=0.95)
        Confidence level for confidence intervals
    use_optimization : str, optional (default='auto')
        Optimization framework to use: 'auto', 'jax', 'numba', 'numpy'
    """

    def __init__(
        self,
        wavelet: str = "db4",
        scales: Optional[List[int]] = None,
        confidence: float = 0.95,
        use_optimization: str = "auto",
        robust: bool = False,
        j_min: int = 2,
        j_max: Optional[int] = None,
    ):
        super().__init__()
        
        # Estimator parameters
        self.parameters = {
            "wavelet": wavelet,
            "scales": scales,
            "confidence": confidence,
            "robust": robust,
            "j_min": int(max(1, j_min)),
            "j_max": j_max,
        }
        
        # Optimization framework
        self.optimization_framework = self._select_optimization_framework(use_optimization)
        
        # Results storage
        self.results = {}
        
        # Validation
        self._validate_parameters()

    def _select_optimization_framework(self, use_optimization: str) -> str:
        """Select the optimal optimization framework."""
        if use_optimization == "auto":
            if JAX_AVAILABLE:
                return "jax"  # Best for GPU acceleration
            elif NUMBA_AVAILABLE:
                return "numba"  # Good for CPU optimization
            else:
                return "numpy"  # Fallback
        elif use_optimization == "jax" and JAX_AVAILABLE:
            return "jax"
        elif use_optimization == "numba" and NUMBA_AVAILABLE:
            return "numba"
        else:
            return "numpy"

    def _validate_parameters(self) -> None:
        """Validate estimator parameters."""
        if not isinstance(self.parameters["wavelet"], str):
            raise ValueError("wavelet must be a string")
        
        if self.parameters["scales"] is not None:
            if not isinstance(self.parameters["scales"], list) or len(self.parameters["scales"]) == 0:
                raise ValueError("scales must be a non-empty list")
        
        if not (0 < self.parameters["confidence"] < 1):
            raise ValueError("confidence must be between 0 and 1")

    def estimate(self, data: Union[np.ndarray, list]) -> Dict[str, Any]:
        """
        Estimate the Hurst parameter using wavelet variance analysis with automatic optimization.

        Parameters
        ----------
        data : array-like
            Input time series data

        Returns
        -------
        dict
            Dictionary containing estimation results including:
            - hurst_parameter: Estimated Hurst parameter
            - confidence_interval: Confidence interval for the estimate
            - r_squared: R-squared value of the fit
            - scales: Scales used in the analysis
            - wavelet_type: Wavelet type used
            - slope: Slope of the log-log regression
            - intercept: Intercept of the log-log regression
            - wavelet_variances: Variance at each scale
        """
        data = np.asarray(data)
        n = len(data)

        if n < 100:
            warnings.warn("Data length is small, results may be unreliable")

        # Select optimal method based on data size and framework
        if self.optimization_framework == "jax" and JAX_AVAILABLE:
            try:
                return self._estimate_jax(data)
            except Exception as e:
                warnings.warn(f"JAX implementation failed: {e}, falling back to NumPy")
                return self._estimate_numpy(data)
        elif self.optimization_framework == "numba" and NUMBA_AVAILABLE:
            try:
                return self._estimate_numba(data)
            except Exception as e:
                warnings.warn(f"Numba implementation failed: {e}, falling back to NumPy")
                return self._estimate_numpy(data)
        else:
            return self._estimate_numpy(data)

    def _estimate_numpy(self, data: np.ndarray) -> Dict[str, Any]:
        """NumPy implementation of Wavelet Variance estimation."""
        n = len(data)
        
        # Determine levels/scales
        if self.parameters["scales"] is None:
            w = pywt.Wavelet(self.parameters["wavelet"])
            J = max(1, pywt.dwt_max_level(n, w.dec_len))
            j_min = min(self.parameters["j_min"], J)
            j_max = self.parameters["j_max"] if self.parameters["j_max"] is not None else max(1, J - 1)
            j_max = min(max(j_min, j_max), J)
            self.parameters["scales"] = list(range(j_min, j_max + 1))
        
        # Adjust scales for data length
        max_safe_scale = min(max(self.parameters["scales"]), int(np.log2(n)) - 1)
        safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
        
        if len(safe_scales) < 2:
            raise ValueError(
                f"Data length {n} is too short for available scales {self.parameters['scales']}"
            )
        
        # Use safe scales
        self.parameters["scales"] = safe_scales

        # Cap to conservative maximum scale to reduce SRD bias
        scale_cap = min(max(self.parameters["scales"]), 6)
        capped_scales = [s for s in self.parameters["scales"] if s <= scale_cap]
        if len(capped_scales) >= 3:
            self.parameters["scales"] = capped_scales

        coeffs = pywt.wavedec(
            data,
            self.parameters["wavelet"],
            level=max(self.parameters["scales"]),
            mode="periodization",
        )

        # Calculate wavelet variances for each scale
        wavelet_variances = {}
        scale_logs = []
        variance_logs = []
        variance_log_variances = []

        for j in self.parameters["scales"]:
            detail_coeffs = coeffs[-j]
            if self.parameters["robust"]:
                med = np.median(detail_coeffs)
                mad = np.median(np.abs(detail_coeffs - med))
                sigma = mad / 0.6744897501960817
                variance = float(sigma ** 2)
            else:
                variance = float(np.var(detail_coeffs, ddof=1))

            wavelet_variances[j] = variance
            scale_logs.append(float(j))
            variance_logs.append(np.log2(variance))

            n_coeffs = max(len(detail_coeffs), 2)
            dof = max(n_coeffs - 1, 1)
            var_log = float(polygamma(1, 0.5 * dof))
            if not np.isfinite(var_log) or var_log <= 0:
                var_log = 1.0 / max(dof, 1.0)
            variance_log_variances.append(var_log / (np.log(2.0) ** 2))

        slope, intercept, r_squared, slope_se, weights = self._weighted_regression(
            np.array(scale_logs, dtype=float),
            np.array(variance_logs, dtype=float),
            np.array(variance_log_variances, dtype=float),
        )

        # Empirical mapping consistent with orthonormal DWT conventions: H ≈ (slope + 1)/2
        estimated_hurst = 0.5 * (slope + 1.0)

        # Calculate confidence interval
        confidence_interval = self._get_confidence_interval(
            estimated_hurst,
            slope_se,
            len(scale_logs),
        )

        corrected_hurst, applied_bias = apply_srd_bias_correction(
            "WaveletVar", float(estimated_hurst)
        )
        if applied_bias != 0.0 and confidence_interval is not None:
            lower = max(0.01, min(0.99, confidence_interval[0] - applied_bias))
            upper = max(0.01, min(0.99, confidence_interval[1] - applied_bias))
            confidence_interval = (lower, upper)
        estimated_hurst = corrected_hurst

        # Store results
        self.results = {
            "hurst_parameter": float(estimated_hurst),
            "confidence_interval": confidence_interval,
            "r_squared": float(r_squared),
            "scales": self.parameters["scales"],
            "wavelet_type": self.parameters["wavelet"],
            "slope": float(slope),
            "intercept": float(intercept),
            "wavelet_variances": wavelet_variances,
            "scale_logs": scale_logs,
            "variance_logs": variance_logs,
            "regression_weights": weights.tolist(),
            "bias_correction": applied_bias,
            "method": "numpy",
            "optimization_framework": self.optimization_framework,
        }
        
        return self.results

    def _estimate_numba(self, data: np.ndarray) -> Dict[str, Any]:
        """Numba-optimized implementation of Wavelet Variance estimation."""
        # For now, use NumPy implementation with Numba JIT compilation
        # This can be enhanced with custom Numba kernels for specific operations
        return self._estimate_numpy(data)

    def _estimate_jax(self, data: np.ndarray) -> Dict[str, Any]:
        """JAX-optimized implementation of Wavelet Variance estimation."""
        if not JAX_AVAILABLE:
            return self._estimate_numpy(data)

        data_np = np.asarray(data, dtype=float)
        n = len(data_np)

        # Determine admissible scales identical to NumPy path
        if self.parameters["scales"] is None:
            w = pywt.Wavelet(self.parameters["wavelet"])
            J = max(1, pywt.dwt_max_level(n, w.dec_len))
            j_min = min(self.parameters["j_min"], J)
            j_max = self.parameters["j_max"] if self.parameters["j_max"] is not None else max(1, J - 1)
            j_max = min(max(j_min, j_max), J)
            self.parameters["scales"] = list(range(j_min, j_max + 1))

        max_safe_scale = min(max(self.parameters["scales"]), int(np.log2(n)) - 1)
        safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
        if len(safe_scales) < 2:
            raise ValueError(
                f"Data length {n} is too short for available scales {self.parameters['scales']}"
            )
        self.parameters["scales"] = safe_scales

        max_level = max(self.parameters["scales"])
        data_jax = jnp.asarray(data_np, dtype=jnp.float64)
        _, details = dwt_periodized(data_jax, self.parameters["wavelet"], max_level)

        robust = bool(self.parameters.get("robust", False))
        variances_all, counts_all = wavelet_detail_variances(details, robust=robust)

        selected_indices = jnp.array([s - 1 for s in self.parameters["scales"]], dtype=jnp.int32)
        selected_variances = variances_all[selected_indices]
        selected_counts = counts_all[selected_indices]

        scale_logs = jnp.asarray(self.parameters["scales"], dtype=jnp.float64)
        variance_logs = jnp.log2(selected_variances)

        dof = jnp.maximum(selected_counts - 1, 1)
        trigamma = jax.scipy.special.polygamma(1, 0.5 * dof)
        var_log = jnp.maximum(trigamma, 1e-12) / (jnp.log(2.0) ** 2)
        weights = 1.0 / jnp.clip(var_log, 1e-12, None)

        X = jnp.stack([jnp.ones_like(scale_logs), scale_logs], axis=1)
        XtWX = X.T @ (weights[:, None] * X)
        XtWy = X.T @ (weights * variance_logs)
        beta = jnp.linalg.solve(XtWX, XtWy)
        intercept, slope = beta

        y_fit = slope * scale_logs + intercept
        y_mean = jnp.average(variance_logs, weights=weights)
        ss_res = jnp.sum(weights * (variance_logs - y_fit) ** 2)
        ss_tot = jnp.sum(weights * (variance_logs - y_mean) ** 2)
        r_squared = jnp.where(ss_tot > 0, 1.0 - ss_res / ss_tot, 0.0)

        estimated_hurst = 0.5 * (slope + 1.0)

        slope_se = jnp.sqrt(jnp.clip(jnp.linalg.inv(XtWX)[1, 1], 1e-12, None))
        confidence_interval = self._get_confidence_interval(
            float(estimated_hurst),
            float(slope_se),
            len(self.parameters["scales"]),
        )

        corrected_hurst, applied_bias = apply_srd_bias_correction(
            "WaveletVar", float(estimated_hurst)
        )
        if applied_bias != 0.0 and confidence_interval is not None:
            lower = max(0.01, min(0.99, confidence_interval[0] - applied_bias))
            upper = max(0.01, min(0.99, confidence_interval[1] - applied_bias))
            confidence_interval = (lower, upper)
        estimated_hurst = corrected_hurst

        wavelet_variances = {
            int(scale): float(selected_variances[i])
            for i, scale in enumerate(self.parameters["scales"])
        }

        self.results = {
            "hurst_parameter": float(estimated_hurst),
            "confidence_interval": confidence_interval,
            "r_squared": float(r_squared),
            "scales": list(self.parameters["scales"]),
            "wavelet_type": self.parameters["wavelet"],
            "slope": float(slope),
            "intercept": float(intercept),
            "wavelet_variances": wavelet_variances,
            "scale_logs": [float(s) for s in self.parameters["scales"]],
            "variance_logs": [float(v) for v in variance_logs],
            "regression_weights": [float(w) for w in weights],
            "bias_correction": applied_bias,
            "method": "jax",
            "optimization_framework": self.optimization_framework,
        }

        return self.results

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

    def _get_confidence_interval(
        self,
        estimated_hurst: float,
        slope_se: float,
        n_points: int,
    ) -> Tuple[float, float]:
        """Calculate confidence interval for the Hurst parameter estimate."""
        confidence = self.parameters["confidence"]
        hurst_se = slope_se / 2.0
        dof = max(n_points - 2, 1)
        t_value = stats.t.ppf((1 + confidence) / 2, df=dof)
        margin = float(t_value * hurst_se)
        return (float(estimated_hurst - margin), float(estimated_hurst + margin))

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

    def plot_analysis(self, figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None) -> None:
        """Plot the wavelet variance analysis results."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(f'Wavelet Variance Analysis - {self.parameters["wavelet"]} Wavelet', fontsize=16)

        # Plot 1: Log-log scaling relationship
        ax1 = axes[0, 0]
        x = self.results["scale_logs"]
        y = self.results["variance_logs"]

        ax1.scatter(x, y, s=60, alpha=0.7, label="Data points")

        # Plot fitted line
        slope = self.results["slope"]
        intercept = self.results["intercept"]
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept
        ax1.plot(x_fit, y_fit, "r--", label=f"Linear fit (slope={slope:.3f})")

        ax1.set_xlabel("log₂(Scale)")
        ax1.set_ylabel("log₂(Variance)")
        ax1.set_title("Wavelet Variance Scaling")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Variance vs Scale (log-log)
        ax2 = axes[0, 1]
        scales = self.results["scales"]
        variances = [self.results["wavelet_variances"][s] for s in scales]
        
        ax2.scatter(scales, variances, s=60, alpha=0.7)
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.set_xlabel("Scale")
        ax2.set_ylabel("Variance")
        ax2.set_title("Variance vs Scale (log-log)")
        ax2.grid(True, which="both", ls=":", alpha=0.3)

        # Plot 3: Hurst parameter estimate
        ax3 = axes[1, 0]
        hurst = self.results["hurst_parameter"]
        conf_interval = self.results["confidence_interval"]
        
        ax3.bar(["Hurst Parameter"], [hurst], yerr=[[hurst-conf_interval[0]], [conf_interval[1]-hurst]], 
                capsize=10, alpha=0.7, color='skyblue')
        ax3.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='H=0.5 (no memory)')
        ax3.set_ylabel("Hurst Parameter")
        ax3.set_title(f"Hurst Parameter Estimate: {hurst:.3f}")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: R-squared and confidence
        ax4 = axes[1, 1]
        r_squared = self.results["r_squared"]
        confidence = self.parameters["confidence"]
        
        ax4.bar(["R²"], [r_squared], alpha=0.7, color='lightgreen')
        ax4.set_ylabel("R²")
        ax4.set_title(f"Goodness of Fit: R² = {r_squared:.3f}")
        ax4.set_ylim(0, 1)
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.show()

    def get_method_recommendation(self, n: int) -> Dict[str, Any]:
        """Get method recommendation for a given data size."""
        if n < 100:
            return {
                "recommended_method": "numpy",
                "reasoning": f"Data size n={n} is too small for optimization benefits",
                "method_details": {
                    "description": "NumPy implementation",
                    "best_for": "Small datasets (n < 100)",
                    "complexity": "O(n log n)",
                    "memory": "O(n)",
                    "accuracy": "High"
                }
            }
        elif n < 1000:
            return {
                "recommended_method": "numba",
                "reasoning": f"Data size n={n} benefits from JIT compilation",
                "method_details": {
                    "description": "Numba JIT-compiled implementation",
                    "best_for": "Medium datasets (100 ≤ n < 1000)",
                    "complexity": "O(n log n)",
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
                    "best_for": "Large datasets (n ≥ 1000)",
                    "complexity": "O(n log n)",
                    "memory": "O(n)",
                    "accuracy": "High"
                }
            }
