import time
from dataclasses import dataclass, Field, field
from typing import ContextManager

from pynput import mouse

@dataclass
class TripleClickDetector(ContextManager):
    button: mouse.Button = mouse.Button.left
    max_interval: float = 0.5  # Maximaler Zeitabstand zwischen Klicks in Sekunden
    triple_click: bool = False
    _click_times: list[float] = field(default_factory=list)
    _listener: mouse.Listener = field(init=False)

    def __enter__(self):
        self._listener = mouse.Listener(on_click=self._on_click)
        self.triple_click = False
        self._listener.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._listener.stop()
        self._click_times.clear()
        self.triple_click = False

    def _on_click(self, x, y, button, pressed):
        if not pressed or button != self.button:
            return

        now = time.monotonic()
        self._click_times.append(now)

        # Nur letzte drei Klickzeiten behalten
        if len(self._click_times) > 3:
            self._click_times.pop(0)

        print(self._click_times, self._click_times[-1] - self._click_times[0], self.max_interval)

        if len(self._click_times) == 3 and self._click_times[-1] - self._click_times[0] <= self.max_interval:
            print("Dreifachklick erkannt!")
            self.triple_click = True
            self._click_times.clear()
            return


    def stop(self):
        self._listener.stop()
