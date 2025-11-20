from enum import Enum
from dataclasses import dataclass
from .types import Smell, Power, Persistence, Soup

class Smell(Enum):
    PUTRID = "putrid"
    FOUL = "foul"
    NEUTRAL = "neutral"
    PLEASANT = "pleasant"
    HEAVENLY = "heavenly"

@dataclass
class Fart:
    """
    Represents a fart with various attributes such as smell, power, persistence, and soupiness.
    """
    smell: Smell
    power: Power
    persistence: Persistence
    soup: Soup

    def __init__(
        self,
        smell: Smell = Smell.NEUTRAL,
        power: Power = Power.MODERATE,
        persistence: Persistence = Persistence.MEDIUM,
        soup: Soup = Soup.NONE,
    ):
        """
        Initializes a new Fart instance.

        Args:
            smell (Smell): The smell of the fart.
            power (Power): The power of the fart.
            persistence (Persistence): The persistence of the fart.
            soup (Soup): The soupiness of the fart.
        """
        self.smell = smell
        self.power = power
        self.persistence = persistence
        self.soup = soup

    def is_burst(self) -> bool:
        """
        Determines if the fart qualifies as a burst.
        A burst is defined as a fart with explosive power and eternal persistence.

        Returns:
            bool: True if the fart is a burst, False otherwise.
        """
        return self.power == Power.EXPLOSIVE and self.persistence == Persistence.ETERNAL