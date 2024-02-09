import PySimpleGUI as sg
from core.workspace import Workspace
from core.graphics.image import Image


class UserInterface():
    def __init__(self, title: str) -> None:
        menu_layout = self.__create_menu()
        tabs_layout = self.__create_tabs()
        workspace_layout = self.__create_workspace((500, 500))

        layout = [menu_layout, tabs_layout, workspace_layout]
        self.__window = sg.Window(title, layout=layout, finalize=True)

        self.__event = ""
        self.__values = []

    def get_input(self, timeout: int) -> tuple[str, list[str]]:
        event, values = self.__window.read(timeout)

        self.__event = event
        self.__values = values

        return (event, values)

    def destroy(self) -> None:
        return self.__window.close()

    def update_value(self, key: str, *args, **kwargs) -> None:
        self.__window[key].update(*args, **kwargs)

    def update_thumbnail(self, image: Image | None) -> None:
        thumbnail_data = None

        if image is not None:
            thumbnail = image.get_thumbnail((100, 100))
            thumbnail_data = thumbnail.get_tkinter_data()

        self.__window["-WS_THUMBNAIL-"].update(data=thumbnail_data)

    def update_image(self, image: Image | None) -> None:
        image_data = image.get_tkinter_data() if image is not None else None
        self.__window["-WS_IMAGE-"].update(data=image_data)

    def update_layers(self, layers: Workspace) -> None:
        layers_names = layers.get_layers_names()
        self.__window["-WS_LAYERS-"].update(values=layers_names)

    def select_layer(self, layer_name: str) -> None:
        current_layers = self.__window["-WS_LAYERS-"].Values
        if layer_name in current_layers:
            self.__window["-WS_LAYERS-"].set_value(layer_name)

    def get_current_layer(self) -> str | None:
        if len(self.__values["-WS_LAYERS-"]) == 0:
            return None

        return self.__values["-WS_LAYERS-"][0]

    def get_event(self) -> str:
        return self.__event

    def get_values(self, event_key: str) -> list[any]:
        return self.__values

    def get_window(self) -> sg.Window:
        return self.__window

    def __create_menu(self) -> list[list[sg.Element]]:
        menu_def = [
            [
                "File",
                [
                    "Open an image",
                    "Save",
                    "Save as"
                ]
            ],
            [
                "Edit",
                [
                    "Undo",
                    "Redo",
                    "Convert",
                    [
                        "Convert to Grayscale",
                        "Convert to RGB",
                        "Convert to RGBA"
                    ],
                    "Clear Effects"
                ]
            ],
            [
                "Help",
                [
                    "About"
                ]
            ]
        ]

        return [[sg.Menu(menu_def, key="-MENU-")]]

    def __create_tabs(self) -> list[list[sg.Element]]:
        enchancers_tab = self.__create_enchancers_tab()
        transformations_tab = self.__create_transfromations_tab()
        modifications_tab = self.__create_modifications_tab()

        return [[
            sg.Push(),
            sg.TabGroup(
                [[
                    sg.Tab("Enchancers", enchancers_tab),
                    sg.Tab("Transformations", transformations_tab),
                    sg.Tab("Modifications", modifications_tab)
                ]]
            ),
            sg.Push()
        ]]

    def __create_workspace(self, viewer_size: tuple[int, int]) -> list[list[sg.Element]]: # noqa
        image_viewer_column = [
            [
                sg.Push(),
                sg.Image(size=viewer_size, key="-WS_IMAGE-"),
                sg.Push()
            ]
        ]

        layers_column = [
            [
                sg.Push(),
                sg.Image(size=(100, 100), key="-WS_THUMBNAIL-"),
                sg.Push()
            ],
            [
                sg.Listbox(values=[], size=(15, 15), key="-WS_LAYERS-",
                           no_scrollbar=True, enable_events=True),
            ],
            [
                sg.Button("↑", key="-WS_UP-", enable_events=True),
                sg.Button("↓", key="-WS_DOWN-", enable_events=True),
                sg.Push(),
                sg.Button("x", key="-WS_DELETE-", enable_events=True),
                sg.Button("+", key="-WS_ADD-", enable_events=True)
            ]
        ]

        return [
            [
                sg.Column(image_viewer_column),
                sg.Column(layers_column)
            ]
        ]

    def __create_enchancers_tab(self) -> None:
        brightness = [
            [
                sg.Slider((-100, 500), 0, orientation="horizontal",
                          key="-S_BRIGHTNESS-", enable_events=True)
            ]
        ]

        contrast = [
            [
                sg.Slider((-100, 500), 0, orientation="horizontal",
                          key="-S_CONTRAST-", enable_events=True)
            ]
        ]

        saturation = [
            [
                sg.Slider((-200, 500), 0, orientation="horizontal",
                          k="-S_SATURATION-", enable_events=True)
            ]
        ]

        sharpness = [
            [
                sg.Slider((-200, 500), 0, orientation="horizontal",
                          k="-S_SHARPNESS-", enable_events=True)
            ]
        ]

        brightness_frame = sg.Frame("Brightness", layout=brightness)
        contrast_frame = sg.Frame("Contrast", layout=contrast)
        saturation_frame = sg.Frame("Saturation", layout=saturation)
        sharpness_frame = sg.Frame("Sharpness", layout=sharpness)

        enchancers_tab = [
            [
                sg.Push(),
                sg.Column([[brightness_frame], [contrast_frame]]),
                sg.Push(),
                sg.Column([[saturation_frame], [sharpness_frame]]),
                sg.Push()
            ]
        ]

        return enchancers_tab

    def __create_transfromations_tab(self) -> None:
        orientation_col = [
            [
                sg.Push(),
                sg.Text("Rotation", pad=(0, 0)),
                sg.Push()
            ],
            [
                sg.Slider((-180, 180), 0, orientation="horizontal",
                          key="-TR_ROTATION-", enable_events=True),
            ],
            [
                sg.Button("Flip Vertical", key="-TR_FLIP_VERTICAL-"),
                sg.Push(),
                sg.Button("Flip Horizontal", key="-TR_FLIP_HORIZONTAL-")
            ]
        ]

        position_col = [
            [
                sg.Push(),
                sg.Button("↑", size=(2, 1), key="-POS_UP-"),
                sg.Push()
            ],
            [
                sg.Button("←", size=(2, 1), key="-POS_LEFT-"),
                sg.Push(),
                sg.Button("→", size=(2, 1), key="-POS_RIGHT-"),
            ],
            [
                sg.Push(),
                sg.Button("↓", size=(2, 1), key="-POS_DOWN-"),
                sg.Push()
            ],
        ]

        full_scale_col = [
            [
                sg.Push(),
                sg.Button("↑", key="-SCALE_UP-"),
                sg.Push()
            ],
            [
                sg.Push(),
                sg.Button("↓", key="-SCALE_DOWN-"),
                sg.Push()
            ]
        ]

        x_scale_col = [
            [
                sg.Push(),
                sg.Button("↑", key="-SCALE_X_UP-"),
                sg.Push()
            ],
            [
                sg.Push(),
                sg.Button("↓", key="-SCALE_X_DOWN-"),
                sg.Push()
            ]
        ]

        y_scale_col = [
            [
                sg.Push(),
                sg.Button("↑", key="-SCALE_Y_UP-"),
                sg.Push()
            ],
            [
                sg.Push(),
                sg.Button("↓", key="-SCALE_Y_DOWN-"),
                sg.Push()
            ]
        ]

        scale_col = [
            [
                sg.Column([[sg.Frame("Scale X", layout=x_scale_col)]]),
                sg.Column([[sg.Frame("Scale Y", layout=y_scale_col)]]),
                sg.Column([[sg.Frame("Scale XY", layout=full_scale_col)]])
            ]
        ]

        orientation_frame = sg.Frame("Orientation", layout=orientation_col)
        positon_frame = sg.Frame("Position", layout=position_col)
        scale_frame = sg.Frame("Scale", layout=scale_col)

        transformations_tab = [
            [
                sg.Column([[orientation_frame]]),
                sg.Column([[positon_frame]]),
                sg.Column([[scale_frame]])
            ]
        ]

        return transformations_tab

    def __create_modifications_tab(self) -> None:
        crop_col = [
            [
                sg.Push(),
                sg.Button("↓", size=(2, 1), key="-CROP_TOP-"),
                sg.Push()
            ],
            [
                sg.Button("→", size=(2, 1), key="-CROP_LEFT-"),
                sg.Push(),
                sg.Button("←", size=(2, 1), key="-CROP_RIGHT-"),
            ],
            [
                sg.Push(),
                sg.Button("↑", size=(2, 1), key="-CROP_BOT-"),
                sg.Push()
            ],
        ]

        filters_col = [
            [
                sg.Push(),
                sg.Button("Grayscale"),
                sg.Button("Negative"),
                sg.Button("Monochrome"),
                sg.Push()
            ],
            [
                sg.Push(),
                sg.Button("Screen"),
                sg.Button("Multiply"),
                sg.Button("Color Dodge"),
                sg.Push()
            ]
        ]

        crop_frame = sg.Frame("Crop", layout=crop_col)
        filter_frame = sg.Frame("Filters", layout=filters_col)

        modifications_tab = [
            [
                sg.Push(),
                sg.Column([[crop_frame]]),
                sg.Column([[filter_frame]]),
                sg.Push()
            ]
        ]

        return modifications_tab
