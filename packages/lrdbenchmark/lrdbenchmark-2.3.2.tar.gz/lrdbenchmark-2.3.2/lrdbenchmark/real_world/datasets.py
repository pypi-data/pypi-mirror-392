#!/usr/bin/env python3
"""
Deterministic, portable dataset definitions for real-world validation.

The goal of these specifications is not to mirror full-scale datasets but to
provide representative signals that capture the qualitative characteristics of
the domains we care about (financial, physiological, climate, network, etc.)
while remaining fully reproducible and lightweight.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable

import numpy as np


@dataclass(frozen=True)
class DatasetSpec:
    """Metadata and generator for a deterministic validation dataset."""

    name: str
    domain: str
    description: str
    default_length: int
    base_seed: int
    generator: Callable[[int, np.random.Generator], np.ndarray]


def _financial_series(length: int, rng: np.random.Generator) -> np.ndarray:
    t = np.linspace(0, 6 * np.pi, length)
    trend = 0.002 * np.arange(length)
    seasonal = 0.04 * np.sin(0.5 * t) + 0.02 * np.sin(1.3 * t + 0.6)
    volatility = 0.03 * np.sin(0.1 * t + 1.5)
    noise = rng.normal(0, 0.01, length)
    return trend + seasonal + volatility * noise.cumsum() / max(length, 1)


def _physiological_hrv(length: int, rng: np.random.Generator) -> np.ndarray:
    t = np.linspace(0, 8 * np.pi, length)
    baseline = 0.8 + 0.1 * np.sin(0.2 * t)
    respiration = 0.05 * np.sin(0.35 * t + 0.3)
    noise = rng.normal(0, 0.02, length)
    return baseline + respiration + noise


def _physiological_eeg(length: int, rng: np.random.Generator) -> np.ndarray:
    t = np.linspace(0, 4 * np.pi, length)
    alpha = 0.5 * np.sin(10 * t)
    beta = 0.2 * np.sin(20 * t + 1.3)
    artifacts = 0.1 * np.sin(1.5 * t) + 0.05 * np.sign(np.sin(0.3 * t + 0.8))
    noise = rng.normal(0, 0.05, length)
    return alpha + beta + artifacts + noise


def _climate_temperature(length: int, rng: np.random.Generator) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, length)
    seasonal = 0.6 * np.sin(t) + 0.2 * np.sin(2 * t + 0.4)
    multi_year = 0.05 * np.sin(0.2 * t + 1.1)
    trend = 0.0015 * np.arange(length)
    noise = rng.normal(0, 0.03, length)
    return 15 + seasonal + multi_year + trend + noise


def _network_traffic(length: int, rng: np.random.Generator) -> np.ndarray:
    time = np.linspace(0, 1, length)
    baseline = 150 + 40 * np.sin(4 * np.pi * time)
    burst_prob = np.clip(0.1 + 0.2 * np.sin(2 * np.pi * time), 0, 0.9)
    bursts = rng.binomial(1, burst_prob, size=length) * rng.normal(50, 10, size=length)
    noise = rng.normal(0, 5, length)
    return baseline + bursts + noise


def _biophysics_protein(length: int, rng: np.random.Generator) -> np.ndarray:
    t = np.linspace(0, 3 * np.pi, length)
    folding = 2 * np.exp(-0.3 * t) * np.sin(3 * t)
    micro_fluctuations = rng.normal(0, 0.1, length)
    return folding + micro_fluctuations


DATASETS: Iterable[DatasetSpec] = (
    DatasetSpec(
        name="financial_sp500",
        domain="financial",
        description="Synthetic log-return series with seasonal volatility.",
        default_length=1024,
        base_seed=101,
        generator=_financial_series,
    ),
    DatasetSpec(
        name="physiological_hrv",
        domain="physiological",
        description="Heart-rate variability surrogate with respiratory modulation.",
        default_length=1024,
        base_seed=202,
        generator=_physiological_hrv,
    ),
    DatasetSpec(
        name="physiological_eeg",
        domain="physiological",
        description="EEG-like signal combining alpha/beta activity and artifacts.",
        default_length=2048,
        base_seed=303,
        generator=_physiological_eeg,
    ),
    DatasetSpec(
        name="climate_temperature",
        domain="climate",
        description="Temperature anomaly surrogate with annual and multi-annual cycles.",
        default_length=1200,
        base_seed=404,
        generator=_climate_temperature,
    ),
    DatasetSpec(
        name="network_traffic",
        domain="network",
        description="Backbone traffic surrogate with bursty behaviour.",
        default_length=1500,
        base_seed=505,
        generator=_network_traffic,
    ),
    DatasetSpec(
        name="biophysics_protein",
        domain="biophysics",
        description="Protein folding energy landscape surrogate.",
        default_length=900,
        base_seed=606,
        generator=_biophysics_protein,
    ),
)


def dataset_map() -> Dict[str, DatasetSpec]:
    """Return dataset specifications keyed by their canonical name."""
    return {spec.name: spec for spec in DATASETS}

