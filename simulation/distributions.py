from __future__ import annotations

from dataclasses import dataclass
from math import cos, exp, log, pi, sqrt, sin

from simulation.random_generators import UniformRandomGenerator


class BaseDistribution:

    def sample(self):

        raise NotImplementedError

    def sample_many(self, count: int):

        return [
            self.sample()
            for _ in range(count)
        ]


@dataclass
class UniformDistribution(BaseDistribution):

    generator: UniformRandomGenerator

    low: float = 0.0

    high: float = 1.0

    def sample(self):

        return self.low + (
            (self.high - self.low)
            * self.generator.next()
        )


@dataclass
class ExponentialDistribution(BaseDistribution):

    generator: UniformRandomGenerator

    rate: float

    def sample(self):

        if self.rate <= 0:

            raise ValueError("La tasa debe ser mayor que cero.")

        u = self.generator.next()

        while u <= 0:

            u = self.generator.next()

        return -log(1 - u) / self.rate


@dataclass
class NormalDistribution(BaseDistribution):

    generator: UniformRandomGenerator

    mean: float

    standard_deviation: float

    _cached_value: float | None = None

    def sample(self):

        if self._cached_value is not None:

            cached_value = self._cached_value

            self._cached_value = None

            return self.mean + self.standard_deviation * cached_value

        u1 = self.generator.next()

        while u1 <= 0:

            u1 = self.generator.next()

        u2 = self.generator.next()

        radius = sqrt(-2.0 * log(u1))

        z0 = radius * cos(2.0 * pi * u2)

        z1 = radius * sin(2.0 * pi * u2)


        self._cached_value = z1

        return self.mean + self.standard_deviation * z0


@dataclass
class PoissonDistribution(BaseDistribution):

    generator: UniformRandomGenerator

    lam: float

    def sample(self):

        if self.lam < 0:

            raise ValueError("Lambda no puede ser negativo.")

        if self.lam == 0:

            return 0

        threshold = exp(-self.lam)

        product = 1.0

        k = 0

        while product > threshold:

            k += 1

            product *= self.generator.next()

        return k - 1