"""
The undo-redo stack handles the undo and redo operations of the program.
A more tight method can be used by storing only the properties of an image,
however this has some limitations on what effects a user can do undo on.
"""

from collections import deque

from core.graphics.image import Image

Action = tuple[str, Image]


class UndoRedoStack():
    def __init__(self) -> None:
        self.__redo_stack: deque[Action] = deque()
        self.__undo_stack: deque[Action] = deque()

    def __repr__(self) -> str:
        return f"Undo: {self.__undo_stack}, Redo: {self.__redo_stack}"

    def peek_undo_stack(self) -> Action | None:
        if len(self.__undo_stack) == 0:
            return None

        return self.__undo_stack[-1]

    def add_undo_action(self, action: tuple[str, Image]) -> None:
        last_undo = self.peek_undo_stack()

        if last_undo is not None and last_undo[1] == action[1]:
            return

        if len(self.__undo_stack) > 20:
            self.__undo_stack.popleft()

        layer_name, image = action
        self.__undo_stack.append((layer_name, image.copy()))

    def add_redo_action(self, action: tuple[str, Image]):
        if len(self.__undo_stack) > 20:
            self.__redo_stack.popleft()

        layer_name, image = action
        self.__redo_stack.append((layer_name, image.copy()))

    def refresh_layer_name(self, old_name: str, new_name: str) -> None:
        for idx, layer in enumerate(self.__undo_stack):
            if layer[0] == old_name:
                _, image = self.__undo_stack[idx]
                self.__undo_stack[idx] = (new_name, image)

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
