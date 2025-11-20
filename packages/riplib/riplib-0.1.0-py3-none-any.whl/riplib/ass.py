import random
from typing import Callable, List, Optional
from .models import Fart
from .types import Smell, Power, Persistence, Soup

class AssClient:
    def __init__(self):
        """
        Initializes the AssClient instance.
        This client manages listeners and generates fart events.
        """
        self.listeners: List[Callable[[Fart], None]] = []

    def rip(
        self,
        smell: Optional[Smell] = None,
        power: Optional[Power] = None,
        persistence: Optional[Persistence] = None,
        soup: Optional[Soup] = None,
    ) -> Fart:
        """
        Generates a fart with the specified attributes or random values if not provided.

        Args:
            smell (Optional[Smell]): The smell of the fart.
            power (Optional[Power]): The power of the fart.
            persistence (Optional[Persistence]): The persistence of the fart.
            soup (Optional[Soup]): The soupiness of the fart.

        Returns:
            Fart: The generated fart instance.
        """
        fart_instance = Fart(
            smell=smell or random.choice(list(Smell)),
            power=power or random.choice(list(Power)),
            persistence=persistence or random.choice(list(Persistence)),
            soup=soup or random.choice(list(Soup)),
        )
        self._notify_listeners(fart_instance)
        return fart_instance

    def _notify_listeners(self, fart: Fart) -> None:
        """
        Notifies all registered listeners about a new fart event.

        Args:
            fart (Fart): The fart instance to notify listeners about.
        """
        for listener in self.listeners:
            listener(fart)

    def register_listener(self, listener: Callable[[Fart], None]) -> None:
        """
        Registers a listener to be notified of fart events.

        Args:
            listener (Callable[[Fart], None]): The listener function to register.
        """
        self.listeners.append(listener)

    def on_rip(self, listener: Callable[[Fart], None]) -> Callable[[Fart], None]:
        """
        Decorator to register a function as a listener for rip events.

        Args:
            listener (Callable[[Fart], None]): The listener function to register.

        Returns:
            Callable[[Fart], None]: The registered listener function.
        """
        self.register_listener(listener)
        return listener