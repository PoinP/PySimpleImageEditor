import unittest

from core.graphics.image import Image
from core.workflow.workspace import Workspace


class Test_Workspace(unittest.TestCase):
    def setUp(self) -> None:
        self.ws = Workspace()

        image = Image()
        self.dummyImage = image
        self.ws.add_layer(image, "Im")
        self.ws.add_layer(image, "Im2")

        return super().setUp()

    def test_len(self):
        self.assertEqual(len(self.ws), 2)

    def test_count(self):
        count = self.ws.get_layers_count()
        self.assertEqual(count, 2)

    def test_get_layers(self):
        layers = self.ws.get_layers()
        names = ["Im", "Im2"]

        for idx, layer in enumerate(layers):
            self.assertEqual(layer[0], names[idx])
            self.assertEqual(layer[1], self.dummyImage)

    def test_get_layer_names(self):
        layers_names = self.ws.get_layers_names()
        names = ["Im", "Im2"]

        for idx, layer_name in enumerate(layers_names):
            self.assertEqual(layer_name, names[idx])

    def test_delete_layer(self):
        self.ws.delete_layer("Im")

        self.assertEqual(len(self.ws), 1)

        layer = self.ws.get_layers()[0]
        self.assertEqual(layer[0], "Im2")

    def test_add_layer(self):
        self.ws.add_layer(self.dummyImage, "Im")
        self.ws.add_layer(self.dummyImage, "Im")

        self.assertEqual(len(self.ws), 4)

        names = ["Im", "Im2", "Im (2)", "Im (3)"]
        layers = self.ws.get_layers()

        for idx, layer in enumerate(layers):
            self.assertEqual(layer[0], names[idx])
            self.assertEqual(layer[1], self.dummyImage)

    def test_rename_layer(self):
        self.ws.rename_layer("Im", "Im2")

        names = ["Im2 (1)", "Im2"]
        layers = self.ws.get_layers()

        for idx, layer in enumerate(layers):
            self.assertEqual(layer[0], names[idx])
            self.assertEqual(layer[1], self.dummyImage)

    def test_move_layer_up(self):
        self.ws.move_layer_up("Im2")

        layers_names = self.ws.get_layers_names()
        names = ["Im2", "Im"]

        for idx, layer_name in enumerate(layers_names):
            self.assertEqual(layer_name, names[idx])

        self.ws.move_layer_up("Im2")
        for idx, layer_name in enumerate(layers_names):
            self.assertEqual(layer_name, names[idx])

    def test_move_layer_down(self):
        self.ws.move_layer_down("Im")

        layers_names = self.ws.get_layers_names()
        names = ["Im2", "Im"]

        for idx, layer_name in enumerate(layers_names):
            self.assertEqual(layer_name, names[idx])

        self.ws.move_layer_down("Im")
        for idx, layer_name in enumerate(layers_names):
            self.assertEqual(layer_name, names[idx])

    def test_get_layer(self):
        self.assertEqual(self.ws.get_layer("Im"), self.dummyImage)
        self.assertIsNone(self.ws.get_layer("Aaaa"))

    def test_swap_layers(self):
        self.ws.add_layer(self.dummyImage, "1")
        self.ws.add_layer(self.dummyImage, "2")
        self.ws.add_layer(self.dummyImage, "3")
        self.ws.add_layer(self.dummyImage, "4")
        self.ws.add_layer(self.dummyImage, "5")
        self.ws.add_layer(self.dummyImage, "6")
        self.ws.add_layer(self.dummyImage, "7")
        self.ws.add_layer(self.dummyImage, "8")

        self.ws.swap_layers(0, 8)
        self.ws.swap_layers(8, 3)
        self.ws.swap_layers(5, 7)

        names = ["7", "Im2", "1", "Im", "3",
                 "6", "5", "4", "2", "8"]

        layer_names = self.ws.get_layers_names()
        for idx, layer in enumerate(layer_names):
            self.assertEqual(layer, names[idx])


if __name__ == "__main__":
    unittest.main()
