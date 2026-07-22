from dataclasses import dataclass
import time


@dataclass
class AnalysisTimer:

    weather: float = 0.0

    gpm: float = 0.0

    sentinel: float = 0.0

    terrain: float = 0.0

    hazard: float = 0.0

    infrastructure: float = 0.0

    spatial: float = 0.0

    gemini: float = 0.0

    total: float = 0.0


class Timer:

    def __init__(self):

        self.start = time.perf_counter()

    def elapsed(self):

        return round(

            time.perf_counter() - self.start,

            2,

        )