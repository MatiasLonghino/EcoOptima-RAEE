from dataclasses import dataclass


@dataclass
class Monitor:

    id: int

    category: str | None = None

    arrival_day: int = 0

    processed: bool = False