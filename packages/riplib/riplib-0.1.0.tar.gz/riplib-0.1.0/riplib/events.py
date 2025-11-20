from typing import Callable, List, Dict

class EventManager:
    """
    Manages event listeners and triggers events.
    """
    def __init__(self):
        """
        Initializes the EventManager with an empty dictionary of listeners.
        """
        self.listeners: Dict[str, List[Callable]] = {}

    def on(self, event_name: str) -> Callable:
        """
        Registers a function as a listener for a specific event.

        Args:
            event_name (str): The name of the event to listen for.

        Returns:
            Callable: A decorator to register the listener function.
        """
        def decorator(func: Callable) -> Callable:
            if event_name not in self.listeners:
                self.listeners[event_name] = []
            self.listeners[event_name].append(func)
            return func
        return decorator

    def trigger(self, event_name: str, *args, **kwargs) -> None:
        """
        Triggers an event, calling all registered listeners for that event.

        Args:
            event_name (str): The name of the event to trigger.
            *args: Positional arguments to pass to the listeners.
            **kwargs: Keyword arguments to pass to the listeners.
        """
        if event_name in self.listeners:
            for listener in self.listeners[event_name]:
                listener(*args, **kwargs)

event_manager = EventManager()

def on_rip(func: Callable) -> Callable:
    """
    Decorator to register a function as a listener for the "rip" event.

    Args:
        func (Callable): The function to register as a listener.

    Returns:
        Callable: The registered listener function.
    """
    return event_manager.on("rip")(func)