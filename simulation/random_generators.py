from __future__ import annotations

from abc import ABC, abstractmethod


class UniformRandomGenerator(ABC):

    @abstractmethod
    def next(self) -> float:

        raise NotImplementedError

    def generate_many(self, count: int) -> list[float]:

        return [
            self.next()
            for _ in range(count)
        ]

    def generate(self, count: int) -> list[float]:

        return self.generate_many(count)


class CongruentialGenerator(UniformRandomGenerator):

    def __init__(
        self,
        seed: int,
        multiplier: int,
        modulus: int,
        increment: int = 0,
    ):

        if modulus <= 0:

            raise ValueError("El módulo debe ser mayor que cero.")

        self.multiplier = int(multiplier)

        self.increment = int(increment)

        self.modulus = int(modulus)

        self.state = int(seed) % self.modulus

        if self.state == 0 and self.increment == 0:

            self.state = 1

    def next(self) -> float:

        self.state = (
            self.multiplier * self.state
            + self.increment
        ) % self.modulus

        if self.state == 0 and self.increment == 0:

            self.state = 1

        return self.state / self.modulus


class LehmerGenerator(CongruentialGenerator):

    def __init__(
        self,
        seed: int,
        multiplier: int = 48271,
        digits: int | None = None,
    ):

        if multiplier <= 0:

            raise ValueError("El multiplicador debe ser mayor que cero.")

        self.state = abs(int(seed))

        if self.state == 0:

            self.state = 1

        self.multiplier = int(multiplier)

        self.multiplier_digits = len(str(self.multiplier))

        self.digits = digits or max(
            len(str(self.state)),
            self.multiplier_digits + 1,
        )

    def next(self) -> float:

        product = self.state * self.multiplier

        product_text = str(product)

        if len(product_text) <= self.multiplier_digits:

            product_text = product_text.zfill(self.multiplier_digits + 1)

        left_text = product_text[:self.multiplier_digits]

        right_text = product_text[self.multiplier_digits:]

        next_state = int(right_text or 0) - int(left_text or 0)

        if next_state < 0:

            next_state = abs(next_state)

        self.state = next_state if next_state > 0 else 1

        denominator = 10 ** len(str(self.state))

        return self.state / denominator


class MixedCongruentialGenerator(CongruentialGenerator):

    def __init__(
        self,
        seed: int,
        multiplier: int,
        increment: int,
        modulus: int,
    ):

        super().__init__(
            seed=seed,
            multiplier=multiplier,
            modulus=modulus,
            increment=increment,
        )


class MultiplicativeCongruentialGenerator(CongruentialGenerator):

    def __init__(
        self,
        seed: int,
        multiplier: int,
        modulus: int,
    ):

        super().__init__(
            seed=seed,
            multiplier=multiplier,
            modulus=modulus,
            increment=0,
        )


class AdditiveCongruentialGenerator(UniformRandomGenerator):

    def __init__(
        self,
        seeds: list[int] | tuple[int, ...],
        modulus: int,
        lag_a: int = 1,
        lag_b: int = 4,
    ):

        if modulus <= 0:

            raise ValueError("El módulo debe ser mayor que cero.")

        if lag_a <= 0 or lag_b <= 0:

            raise ValueError("Los retardos deben ser mayores que cero.")

        self.modulus = int(modulus)

        self.lag_a = int(lag_a)

        self.lag_b = int(lag_b)

        self.buffer = [
            int(seed) % self.modulus
            for seed in seeds
        ]

        required_size = max(self.lag_a, self.lag_b)

        if len(self.buffer) < required_size:

            raise ValueError(
                "Se necesitan suficientes semillas iniciales para los retardos indicados."
            )

    def next(self) -> float:

        next_value = (
            self.buffer[-self.lag_a]
            + self.buffer[-self.lag_b]
        ) % self.modulus

        self.buffer.append(next_value)

        return next_value / self.modulus


class MiddleSquareGenerator(UniformRandomGenerator):

    def __init__(
        self,
        seed: int,
        digits: int = 4,
    ):

        if digits <= 0:

            raise ValueError("La cantidad de dígitos debe ser mayor que cero.")

        self.digits = int(digits)

        self.state = abs(int(seed))

        self._modulus = 10 ** self.digits

        self.state %= self._modulus

    def next(self) -> float:

        square_text = str(self.state ** 2).zfill(self.digits * 2)

        extra_digits = len(square_text) - self.digits

        start = max(0, extra_digits // 2)

        middle_text = square_text[start:start + self.digits]

        self.state = int(middle_text) if middle_text else 0

        return self.state / self._modulus