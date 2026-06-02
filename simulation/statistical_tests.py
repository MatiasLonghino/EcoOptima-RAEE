from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist

import numpy as np


@dataclass(frozen=True)
class MeanTestResult:

    sample_size: int

    sample_mean: float

    z_statistic: float

    critical_value: float

    alpha: float

    reject_null: bool

    @property
    def decision(self):

        if self.reject_null:

            return "Se rechaza H0"

        return "No se rechaza H0"


def run_mean_test(sample, alpha=0.05):

    sample_array = np.asarray(sample, dtype=float)

    sample_size = int(sample_array.size)

    if sample_size == 0:

        raise ValueError("La muestra no puede estar vacía.")

    sample_mean = float(sample_array.mean())

    z_statistic = (
        sample_mean - 0.5
    ) / sqrt(1 / (12 * sample_size))

    critical_value = NormalDist().inv_cdf(1 - (alpha / 2))

    reject_null = abs(z_statistic) > critical_value

    return MeanTestResult(
        sample_size=sample_size,
        sample_mean=sample_mean,
        z_statistic=z_statistic,
        critical_value=critical_value,
        alpha=alpha,
        reject_null=reject_null,
    )