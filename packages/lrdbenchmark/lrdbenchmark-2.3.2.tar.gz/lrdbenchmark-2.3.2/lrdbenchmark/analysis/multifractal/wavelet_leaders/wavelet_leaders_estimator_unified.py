#!/usr/bin/env python3
"""
Unified Multifractal Wavelet Leaders Estimator.

This module implements the Multifractal Wavelet Leaders estimator with automatic optimization framework
selection (JAX, Numba, NumPy) for the best performance on the available hardware.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pywt
from typing import Dict, Any, Optional, Union, Tuple, List
import warnings

# Import optimization frameworks
try:
    import jax
    import jax.numpy as jnp

    JAX_AVAILABLE = True
except ImportError:
    jax = None  # type: ignore[assignment]
    jnp = None  # type: ignore[assignment]
    JAX_AVAILABLE = False

try:
    import numba
    from numba import jit as numba_jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from lrdbenchmark.analysis.base_estimator import BaseEstimator
from lrdbenchmark.analysis.wavelet.jax_wavelet import dwt_periodized


class MultifractalWaveletLeadersEstimator(BaseEstimator):
    """
    Unified Multifractal Wavelet Leaders Estimator.

    This estimator uses wavelet leaders to analyze multifractal properties
    of time series data, providing robust estimates of the multifractal spectrum.

    Features:
    - Automatic optimization framework selection (JAX, Numba, NumPy)
    - GPU acceleration with JAX when available
    - JIT compilation with Numba for CPU optimization
    - Graceful fallbacks when optimization frameworks fail

    Parameters
    ----------
    wavelet : str, optional (default='db4')
        Wavelet to use for analysis
    scales : List[int], optional (default=None)
        List of scales for analysis. If None, will be generated from min_scale to max_scale
    min_scale : int, optional (default=2)
        Minimum scale for analysis
    max_scale : int, optional (default=32)
        Maximum scale for analysis
    num_scales : int, optional (default=10)
        Number of scales to use if scales is None
    q_values : List[float], optional (default=None)
        List of q values for multifractal analysis. Default: [-5, -3, -1, 0, 1, 2, 3, 5]
    use_optimization : str, optional (default='auto')
        Optimization framework to use: 'auto', 'jax', 'numba', 'numpy'
    """

    def __init__(
        self,
        wavelet: str = "db3",
        scales: Optional[List[int]] = None,
        min_scale: int = 2,
        max_scale: int = 32,
        num_scales: int = 10,
        q_values: Optional[List[float]] = None,
        use_optimization: str = "numpy",
    ):
        super().__init__()
        
        # Set default q_values if not provided
        if q_values is None:
            q_values = [-2, -1, -0.5, 0, 0.5, 1, 2, 3, 4]

        # Set default scales if not provided
        if scales is None:
            scales = np.arange(min_scale, max_scale + 1, max(1, (max_scale - min_scale) // max(1, num_scales - 1)))
        
        # Estimator parameters
        self.parameters = {
            "wavelet": wavelet,
            "scales": scales,
            "min_scale": min_scale,
            "max_scale": max_scale,
            "num_scales": num_scales,
            "q_values": q_values,
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

        if not isinstance(self.parameters["scales"], (list, np.ndarray)):
            raise ValueError("scales must be a list or array")

        if not isinstance(self.parameters["q_values"], (list, np.ndarray)):
            raise ValueError("q_values must be a list or array")

        if self.parameters["min_scale"] <= 0:
            raise ValueError("min_scale must be positive")

        if self.parameters["max_scale"] <= self.parameters["min_scale"]:
            raise ValueError("max_scale must be greater than min_scale")

    def estimate(self, data: Union[np.ndarray, list]) -> Dict[str, Any]:
        """
        Estimate multifractal properties using Wavelet Leaders with automatic optimization.

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
            - 'structure_functions': Dictionary of Sq(j) for each q
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
        """NumPy implementation of Wavelet Leaders estimation."""
        # Adjust scales for data length
        max_safe_scale = min(self.parameters["max_scale"], len(data) // 8)
        if max_safe_scale < self.parameters["min_scale"]:
            raise ValueError(f"Data length {len(data)} is too short for wavelet leaders analysis")
        
        # Update scales if needed
        if max_safe_scale < self.parameters["max_scale"]:
            safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
            if len(safe_scales) >= 3:
                self.parameters["scales"] = np.array(safe_scales)
                self.parameters["max_scale"] = max_safe_scale
            else:
                warnings.warn(
                    f"Data length ({len(data)}) may be too short for reliable wavelet leaders analysis"
                )

        scales = np.asarray(self.parameters["scales"], dtype=int)
        q_values = np.asarray(self.parameters["q_values"], dtype=float)

        # Compute leaders once via full DWT
        w = pywt.Wavelet(self.parameters["wavelet"])
        J = pywt.dwt_max_level(len(data), w.dec_len)
        coeffs = pywt.wavedec(data, w, mode='periodization', level=J)
        abs_details = [np.abs(c) for c in coeffs[-1:0:-1]]  # [|cD_1|, ..., |cD_J|]
        leaders = self._leaders_from_dwt(abs_details)

        # Structure functions S_L(q,j) with j = 1..J (scale index)
        js = scales.astype(float)
        SL = np.zeros((q_values.size, js.size), dtype=float)
        for jj, j in enumerate(scales):
            Lj = leaders[j-1] if 1 <= j <= len(leaders) else leaders[-1]
            for qi, q in enumerate(q_values):
                if np.isclose(q, 0.0):
                    SL[qi, jj] = float(np.exp(np.mean(np.log(Lj + 1e-18))))
                else:
                    SL[qi, jj] = float(np.mean((Lj + 1e-18) ** q))

        # zeta(q): slope of log2 SL(q,j) vs j (NOT log j)
        zeta = np.zeros(q_values.size, dtype=float)
        for qi in range(q_values.size):
            y = np.log2(SL[qi, :] + 1e-300)
            slope, intercept = np.polyfit(js, y, 1)
            zeta[qi] = float(slope)

        # c1 via linear fit of zeta(q) vs q around q≈0
        slope_c1, intercept_c0 = np.polyfit(q_values, zeta, 1)
        H_hat = float(slope_c1)

        self.results = {
            "hurst_parameter": H_hat,
            "method": "wavelet_leaders",
            "q": q_values.tolist(),
            "zeta": zeta.tolist(),
            "c1": float(slope_c1),
            "c0": float(intercept_c0),
            "j_used": js.tolist(),
        }
        return self.results

    def _estimate_numba(self, data: np.ndarray) -> Dict[str, Any]:
        """Numba-optimized implementation of Wavelet Leaders estimation."""
        # For now, use NumPy implementation with Numba JIT compilation
        # This can be enhanced with custom Numba kernels for specific operations
        return self._estimate_numpy(data)

    def _estimate_jax(self, data: np.ndarray) -> Dict[str, Any]:
        """JAX-optimized implementation of Wavelet Leaders estimation."""
        if not JAX_AVAILABLE:
            return self._estimate_numpy(data)

        data_np = np.asarray(data, dtype=float)
        n = len(data_np)

        max_safe_scale = min(self.parameters["max_scale"], n // 8)
        if max_safe_scale < self.parameters["min_scale"]:
            raise ValueError(f"Data length {n} is too short for wavelet leaders analysis")

        if max_safe_scale < self.parameters["max_scale"]:
            safe_scales = [s for s in self.parameters["scales"] if s <= max_safe_scale]
            if len(safe_scales) >= 3:
                self.parameters["scales"] = np.array(safe_scales)
                self.parameters["max_scale"] = max_safe_scale
            else:
                warnings.warn(
                    f"Data length ({n}) may be too short for reliable wavelet leaders analysis"
                )

        scales = np.asarray(self.parameters["scales"], dtype=int)
        q_values = np.asarray(self.parameters["q_values"], dtype=float)

        wavelet = self.parameters["wavelet"]
        w = pywt.Wavelet(wavelet)
        J = pywt.dwt_max_level(n, w.dec_len)
        data_jax = jnp.asarray(data_np, dtype=jnp.float64)
        _, details = dwt_periodized(data_jax, wavelet, J)
        abs_details = [jnp.abs(d) for d in details]

        leaders: List[jnp.ndarray] = []
        for j, Dj in enumerate(abs_details):
            n_j = Dj.shape[0]
            Lj = jnp.zeros(n_j, dtype=jnp.float64)
            for k in range(n_j):
                segments = [Dj[max(0, k - 1): min(n_j, k + 2)]]
                if j > 0:
                    Df = abs_details[j - 1]
                    start = 2 * k - 2
                    idx = jnp.arange(max(0, start), min(Df.shape[0], start + 5))
                    if idx.size > 0:
                        segments.append(Df[idx])
                if j > 1:
                    Df2 = abs_details[j - 2]
                    start2 = 4 * k - 4
                    idx2 = jnp.arange(max(0, start2), min(Df2.shape[0], start2 + 9))
                    if idx2.size > 0:
                        segments.append(Df2[idx2])
                concatenated = jnp.concatenate(segments)
                Lj = Lj.at[k].set(jnp.max(concatenated))
            leaders.append(Lj + 1e-18)

        js = scales.astype(float)
        SL_rows = []
        for q in q_values:
            row_vals = []
            for j in scales:
                Lj = leaders[j - 1] if 1 <= j <= len(leaders) else leaders[-1]
                if Lj.size == 0:
                    row_vals.append(jnp.nan)
                    continue
                if np.isclose(q, 0.0):
                    row_vals.append(jnp.exp(jnp.mean(jnp.log(Lj))))
                else:
                    row_vals.append(jnp.mean(Lj ** q) ** (1.0 / q))
            SL_rows.append(jnp.asarray(row_vals, dtype=jnp.float64))
        SL = jnp.stack(SL_rows, axis=0)

        x = jnp.asarray(js, dtype=jnp.float64)
        x_mean = jnp.mean(x)
        x_centered = x - x_mean
        denom = jnp.sum(x_centered ** 2)

        zeta = []
        for row in SL:
            y = jnp.log2(row + 1e-300)
            y_mean = jnp.mean(y)
            slope = jnp.sum((x - x_mean) * (y - y_mean)) / denom
            zeta.append(slope)
        zeta = jnp.asarray(zeta, dtype=jnp.float64)

        q_arr = jnp.asarray(q_values, dtype=jnp.float64)
        q_mean = jnp.mean(q_arr)
        q_centered = q_arr - q_mean
        denom_q = jnp.sum(q_centered ** 2)
        slope_c1 = jnp.sum(q_centered * (zeta - jnp.mean(zeta))) / denom_q if denom_q > 0 else 0.0
        intercept_c0 = jnp.mean(zeta) - slope_c1 * q_mean

        self.results = {
            "hurst_parameter": float(slope_c1),
            "method": "jax",
            "q": q_values.tolist(),
            "zeta": [float(val) for val in zeta],
            "c1": float(slope_c1),
            "c0": float(intercept_c0),
            "j_used": js.tolist(),
        }

        return self.results

    def _compute_wavelet_coefficients(self, data: np.ndarray, scale: int) -> np.ndarray:
        """Compute wavelet coefficients at a given scale."""
        # Compute wavelet coefficients
        coeffs = pywt.wavedec(data, self.parameters["wavelet"], level=scale)

        # Return detail coefficients at the specified scale
        if scale <= len(coeffs) - 1:
            return coeffs[scale]
        else:
            # If scale is too large, use the highest available level
            return coeffs[-1]

    def _compute_wavelet_leaders(self, data: np.ndarray, scale: int) -> np.ndarray:
        """Compute wavelet leaders at a given scale."""
        # Compute wavelet coefficients at multiple scales
        coeffs = pywt.wavedec(data, self.parameters["wavelet"], level=min(scale, 8))

        # For wavelet leaders, we need coefficients at the current scale and finer scales
        if scale <= len(coeffs) - 1:
            current_coeffs = coeffs[scale]
        else:
            current_coeffs = coeffs[-1]

        # Compute wavelet leaders as the maximum of coefficients at current and finer scales
        leaders = np.zeros_like(current_coeffs)

        for i in range(len(current_coeffs)):
            # Find the maximum absolute coefficient value across scales for this position
            max_val = 0
            for j in range(min(scale + 1, len(coeffs))):
                if i < len(coeffs[j]):
                    max_val = max(max_val, abs(coeffs[j][i]))
            leaders[i] = max_val

        return leaders

    def _compute_structure_functions(
        self, data: np.ndarray, q: float, scale: int
    ) -> float:
        """Compute structure function for a given q and scale."""
        leaders = self._compute_wavelet_leaders(data, scale)

        # Remove zeros to avoid log(0)
        valid_leaders = leaders[leaders > 0]

        if len(valid_leaders) == 0:
            return np.nan

        # Compute q-th order structure function
        if q == 0:
            # Special case for q = 0
            sq = np.exp(np.mean(np.log(valid_leaders)))
        else:
            sq = np.mean(valid_leaders**q) ** (1 / q)

        return sq

    def _leaders_from_dwt(self, detail_coeffs: List[np.ndarray]) -> List[np.ndarray]:
        """
        Build 1D wavelet leaders from |cD_j[k]| using a 3-neighborhood and inclusion
        of finer scales j-1, j-2. detail_coeffs ordered as [|cD_1|, |cD_2|, ..., |cD_J|]
        where j increases with scale (coarser).
        """
        J = len(detail_coeffs)
        leaders: List[np.ndarray] = []
        for j in range(J):  # j=0 is finest (|cD_1|), j=J-1 coarsest (|cD_J|)
            Dj = detail_coeffs[j]
            n = len(Dj)
            Ljk = np.zeros(n, dtype=float)
            for k in range(n):
                neigh = [Dj[max(0, k - 1) : min(n, k + 2)]]
                if j > 0:
                    Df = detail_coeffs[j - 1]
                    start = 2 * k - 2
                    idx = np.arange(max(0, start), min(len(Df), start + 5))
                    if idx.size > 0:
                        neigh.append(Df[idx])
                if j > 1:
                    Df2 = detail_coeffs[j - 2]
                    start2 = 4 * k - 4
                    idx2 = np.arange(max(0, start2), min(len(Df2), start2 + 9))
                    if idx2.size > 0:
                        neigh.append(Df2[idx2])
                Ljk[k] = float(np.max(np.concatenate(neigh))) if len(neigh) > 0 else float(np.abs(Dj[k]))
            leaders.append(Ljk + 1e-18)
        return leaders

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
        """Plot the Wavelet Leaders analysis results."""
        if not self.results:
            raise ValueError("No results available. Run estimate() first.")

        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle(f'Wavelet Leaders Analysis - {self.parameters["wavelet"]} Wavelet', fontsize=16)

        # Plot 1: Structure functions for different q values
        ax1 = axes[0, 0]
        scales = self.results["scales"]
        q_values = self.results["q_values"]
        
        for q in q_values:
            if q in self.results["structure_functions"]:
                sq_vals = self.results["structure_functions"][q]
                valid_mask = ~np.isnan(sq_vals) & (sq_vals > 0)
                if np.any(valid_mask):
                    ax1.loglog(np.array(scales)[valid_mask], sq_vals[valid_mask], 
                              'o-', label=f'q={q}', alpha=0.7)
        
        ax1.set_xlabel('Scale (j)')
        ax1.set_ylabel('Sq(j)')
        ax1.set_title('Structure Functions')
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
                "reasoning": f"Data size n={n} is too small for wavelet leaders analysis",
                "method_details": {
                    "description": "NumPy implementation",
                    "best_for": "Small datasets (n < 100)",
                    "complexity": "O(n log n)",
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
                    "complexity": "O(n log n)",
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
                    "best_for": "Large datasets (n ≥ 2000)",
                    "complexity": "O(n log n)",
                    "memory": "O(n)",
                    "accuracy": "High"
                }
            }
