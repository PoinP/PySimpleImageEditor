import unittest

from PIL import Image as PILImage  # type: ignore
from core.graphics.image import Image
from core.workflow.undo_redo_stack import UndoRedoStack


class Test_UndoRedoStack(unittest.TestCase):
    def setUp(self) -> None:
        self.stack = UndoRedoStack()

        self.red = Image(image=PILImage.new("RGB", (10, 10), "Red"))
        self.green = Image(image=PILImage.new("RGB", (10, 10), "Green"))
        self.blue = Image(image=PILImage.new("RGB", (10, 10), "Blue"))

        self.stack.add_undo_action(("red", self.red))
        self.stack.add_undo_action(("green", self.green))
        self.stack.add_undo_action(("blue", self.blue))

        return super().setUp()

    def test_add_undo_action(self):
        self.stack.add_undo_action(("green", self.green))
        undo_action = self.stack.undo()

        self.assertEqual(undo_action[0], "green")
        self.assertEqual(undo_action[1], self.green)

    def test_add_redo_action(self):
        self.stack.add_redo_action(("green", self.green))
        redo_action = self.stack.redo()

        self.assertEqual(redo_action[0], "green")
        self.assertEqual(redo_action[1], self.green)

    def test_refresh_layer_name(self):
        self.stack.add_undo_action(("green", self.green))
        self.stack.add_undo_action(("green", self.green))
        self.stack.add_undo_action(("green", self.green))

        self.stack.refresh_layer_name("green", "green_new")

        names = ["green_new", "green_new", "green_new",
                 "blue", "green_new", "red"]

        images = [self.green, self.green, self.green,
                  self.blue, self.green, self.red]

        for i in range(6):
            name, image = self.stack.undo()
            self.assertEqual(name, names[i])
            self.assertEqual(image, images[i])

    def test_clear_references(self):
        self.stack.clear_references("green")

        names = ["blue", "red"]

        images = [self.blue, self.red]

        for i in range(2):
            name, image = self.stack.undo()
            self.assertEqual(name, names[i])
            self.assertEqual(image, images[i])

    def test_clear_redo_stack(self):
        self.stack.add_redo_action(("green", self.green))
        self.stack.add_redo_action(("green", self.green))
        self.stack.add_redo_action(("green", self.green))

        self.assertIsNotNone(self.stack.redo())
        self.stack.clear_redo_stack()
        self.assertIsNone(self.stack.redo())

    def test_peek_undo_stack(self):
        action = self.stack.peek_undo_stack()
        self.assertEqual(action[0], "blue")
        self.assertEqual(action[1], self.blue)


if __name__ == "__main__":
    unittest.main()
