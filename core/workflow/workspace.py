from core.graphics.image import Image


class Workspace:
    def __init__(self) -> None:
        self.__layers: list[tuple(str, Image)] = []

    def __len__(self) -> int:
        return len(self.__layers)

    def get_layers_count(self) -> int:
        len(self.__layers)

    def get_layers(self) -> list[(str, Image)]:
        return self.__layers

    def get_layers_names(self) -> list[str]:
        return [name for (name, image) in self.__layers]

    def delete_layer(self, name: str) -> None:
        self.__layers = list(filter(lambda x: x[0] != name, self.__layers))

    def add_layer(self, image: Image, layer_name: str | None = None) -> None:
        if layer_name is None:
            layer_name = "Layer"

        name_count = self.__count_layer_namings(layer_name)

        if (name_count != 0):
            layer_name = layer_name + f" ({name_count})"

        self.__layers.append((layer_name, image))

    def rename_layer(self, old_name: str, new_name: str) -> str:
        layer_index = None
        layers_names = self.get_layers_names()

        try:
            layer_index = layers_names.index(old_name)
        except ValueError:
            return

        name_count = self.__count_layer_namings(new_name)

        if (name_count != 0):
            new_name = new_name + f" ({name_count})"

        name, image = self.__layers[layer_index]
        self.__layers[layer_index] = (new_name, image)
        return new_name

    def update_layer(self, layer_name: str, image: Image) -> None:
        for i in range(len(self)):
            name, img = self.__layers[i]
            if name == layer_name:
                self.__layers[i] = (name, image)
                return

    def move_layer_up(self, name: str) -> None:
        layers_names = self.get_layers_names()
        layer_index = 0

        try:
            layer_index = layers_names.index(name)
        except ValueError:
            return

        if layer_index == 0:
            return

        self.swap_layers(layer_index, layer_index - 1)

    def move_layer_down(self, name: str) -> None:
        layers_names = self.get_layers_names()
        layer_index = 0

        try:
            layer_index = layers_names.index(name)
        except ValueError:
            return

        if layer_index == len(self) - 1:
            return

        self.swap_layers(layer_index, layer_index + 1)

    def get_layer(self, name: str) -> Image | None:
        layer = list(filter(lambda x: x[0] == name, self.__layers))

        if len(layer) == 0:
            return None

        return layer[0][1]

    def swap_layers(self, first_index: int, second_index: int) -> None:
        if first_index < 0 or second_index < 0:
            return

        temp_layer = self.__layers[first_index]
        self.__layers[first_index] = self.__layers[second_index]
        self.__layers[second_index] = temp_layer

    def __count_layer_namings(self, layer_name: str):
        name_count = 0

        layers_names = self.get_layers_names()
        if layer_name in layers_names:
            for name in layers_names:
                name_count += name.count(layer_name)

        return name_count
