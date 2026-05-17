from typing import Callable


class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable):
        if event in self._listeners:
            self._listeners[event].remove(callback)

    def emit(self, event: str, **kwargs):
        if event in self._listeners:
            for callback in self._listeners[event]:
                callback(**kwargs)


bus = EventBus()
