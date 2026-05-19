from typing import Dict
from app.schemas import TaskOut


class Storage:
    def __init__(self):
        self.tasks: Dict[int, TaskOut] = {}
        self._counter: int = 0

    def next_id(self) -> int:
        self._counter += 1
        return self._counter

    def clear(self):
        self.tasks.clear()
        self._counter = 0


storage = Storage()
