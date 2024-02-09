from core.graphics.image import Image

from collections import deque

Action = tuple[str, int]


class UndoRedoStack():
    def __init__(self) -> None:
        self.__redo_stack: deque[Action] = deque()
        self.__undo_stack: deque[Action] = deque()

    def __repr__(self) -> str:
        return f"Undo: {self.__undo_stack}, Redo: {self.__redo_stack}"

    def add_undo_action(self, action: tuple[str, Image]) -> None:
        if len(self.__undo_stack) > 10:
            self.__undo_stack.popleft()

        layer_name, image = action
        self.__undo_stack.append((layer_name, image.copy()))

    def add_redo_action(self, action: tuple[str, Image]):
        if len(self.__undo_stack) > 10:
            self.__redo_stack.popleft()

        layer_name, image = action
        self.__redo_stack.append((layer_name, image.copy()))

    def clear_references(self, layer_name: str) -> None:
        def is_not_layer(x):
            return x[0] != layer_name

        self.__undo_stack = deque(filter(is_not_layer, self.__undo_stack))

    def clear_redo_stack(self) -> None:
        self.__redo_stack.clear()

    def undo(self) -> Action | None:
        if len(self.__undo_stack) == 0:
            return None

        action = self.__undo_stack.pop()
        return action

    def redo(self) -> Action | None:
        if len(self.__redo_stack) == 0:
            return None

        action = self.__redo_stack.pop()
        return action