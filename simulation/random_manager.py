from __future__ import annotations

from dataclasses import dataclass

from simulation.config import SimulationConfig
from simulation.distributions import (
    NormalDistribution,
    PoissonDistribution,
    UniformDistribution,
)
from simulation.random_generators import (
    AdditiveCongruentialGenerator,
    LehmerGenerator,
    MiddleSquareGenerator,
    MixedCongruentialGenerator,
    MultiplicativeCongruentialGenerator,
    UniformRandomGenerator,
)


@dataclass
class RandomManager:

    config: SimulationConfig

    uniform_generator: UniformRandomGenerator

    arrival_distribution: PoissonDistribution

    triage_time_distribution: UniformDistribution

    crt_time_distribution: NormalDistribution

    lcd_time_distribution: NormalDistribution

    @classmethod
    def from_config(cls, config: SimulationConfig):

        generator = cls._build_generator(config)

        return cls(
            config=config,
            uniform_generator=generator,
            arrival_distribution=PoissonDistribution(
                generator=generator,
                lam=config.arrival_lambda,
            ),
            triage_time_distribution=UniformDistribution(
                generator=generator,
                low=10,
                high=15,
            ),
            crt_time_distribution=NormalDistribution(
                generator=generator,
                mean=20,
                standard_deviation=3,
            ),
            lcd_time_distribution=NormalDistribution(
                generator=generator,
                mean=37,
                standard_deviation=4,
            ),
        )

    @staticmethod
    def _build_generator(config: SimulationConfig) -> UniformRandomGenerator:

        method = config.generator_method.strip().lower()

        if method == "lehmer":

            return LehmerGenerator(
                seed=config.random_seed,
                multiplier=config.generator_multiplier,
            )

        if method == "mixto":

            return MixedCongruentialGenerator(
                seed=config.random_seed,
                multiplier=config.generator_multiplier,
                increment=config.generator_increment,
                modulus=config.generator_modulus,
            )

        if method == "multiplicativo":

            return MultiplicativeCongruentialGenerator(
                seed=config.random_seed,
                multiplier=config.generator_multiplier,
                modulus=config.generator_modulus,
            )

        if method == "aditivo":

            return AdditiveCongruentialGenerator(
                seeds=[
                    config.additive_seed_1,
                    config.additive_seed_2,
                    config.additive_seed_3,
                    config.additive_seed_4,
                ],
                modulus=config.generator_modulus,
                lag_a=config.additive_lag_a,
                lag_b=config.additive_lag_b,
            )

        if method in {"cuadrado medio", "middle square", "middle_square"}:

            return MiddleSquareGenerator(
                seed=config.middle_square_seed,
                digits=config.middle_square_digits,
            )

        raise ValueError(
            f"Método de generador no soportado: {config.generator_method}"
        )