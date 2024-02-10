"""
This module builds the User Interface of the program
"""

import PySimpleGUI as sg

from core.graphics.image import Image
from core.workflow.workspace import Workspace


class UserInterface():
    def __init__(self, title: str) -> None:
        menu_layout = UserInterface.__create_menu()
        tabs_layout = UserInterface.__create_tabs()
        workspace_layout = UserInterface.__create_workspace((500, 500))

        layout = [menu_layout, tabs_layout, workspace_layout]
        self.__window = sg.Window(title, layout=layout, finalize=True)

        self.__event = ""
        self.__values = []

    def get_input(self, timeout: int) -> tuple[str, any]:
        event, values = self.__window.read(timeout)

        self.__event = event
        self.__values = values

        return (event, values)

    def destroy(self) -> None:
        return self.__window.close()

    def disable(self) -> None:
        self.__enable(False)

    def enable(self) -> None:
        self.__enable(True)

    def open_popup(self, message: str) -> str:
        image_formats = ".jpeg, .bmp .gif .jpg .png .ico .ppm"
        file_types = ("Image Files", image_formats)
        return sg.popup_get_file(message, file_types=(file_types,))

    def save_popup(self, message: str) -> str:
        file_types = (("PNG", "*.png"), ("GIF", "*.gif"),
                      ("JPEG", "*.jpg *.jpeg"),)
        return sg.popup_get_file(message, file_types=file_types, save_as=True)

    def show_popup(self, *args, title: str) -> None:
        sg.popup(*args, title=title)

    def input_popup(self, message: str) -> str:
        return sg.popup_get_text(message)

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

    @staticmethod
    def show_about_info() -> None:
        sg.Popup("Made with <3 by PoinP", title="About")

    def __enable(self, status: bool) -> None:
        for key in self.__window.key_dict:
            if not isinstance(key, str):
                continue

            if not key.startswith("-") or "WS" in key:
                continue

            self.__window[key].update(disabled=not status)

    @staticmethod
    def __create_menu() -> list[list[sg.Element]]:
        menu_def = [
            [
                "File",
                [
                    "Open an image",
                    "Save",
                    "Save as..."
                ]
            ],
            [
                "Edit",
                [
                    "Undo",
                    "Redo",
                    "Convert",
                    [
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

        return [[sg.Menu(menu_def)]]

    @staticmethod
    def __create_tabs() -> list[list[sg.Element]]:
        enchancers_tab = UserInterface.__create_enchancers_tab()
        transformations_tab = UserInterface.__create_transfromations_tab()
        modifications_tab = UserInterface.__create_modifications_tab()

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

    @staticmethod
    def __create_workspace(viewer_size: tuple[int, int]) -> list[list[sg.Element]]: # noqa
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
                sg.Listbox(values=[], size=(20, 15), key="-WS_LAYERS-",
                           no_scrollbar=True, enable_events=True),
            ],
            [
                sg.Button("↑", key="-WS_UP-", enable_events=True),
                sg.Button("↓", key="-WS_DOWN-", enable_events=True),
                sg.Button("R", key="-WS_RENAME-", enable_events=True),
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

    @staticmethod
    def __create_enchancers_tab() -> None:
        brightness = [
            [
                sg.Slider((-100, 500), 0, orientation="horizontal",
                          key="-S_BRIGHTNESS-", enable_events=True,
                          size=(30, 20))
            ]
        ]

        contrast = [
            [
                sg.Slider((-100, 500), 0, orientation="horizontal",
                          key="-S_CONTRAST-", enable_events=True,
                          size=(30, 20))
            ]
        ]

        saturation = [
            [
                sg.Slider((-200, 500), 0, orientation="horizontal",
                          k="-S_SATURATION-", enable_events=True,
                          size=(30, 20))
            ]
        ]

        sharpness = [
            [
                sg.Slider((-200, 500), 0, orientation="horizontal",
                          k="-S_SHARPNESS-", enable_events=True,
                          size=(30, 20))
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

    @staticmethod
    def __create_transfromations_tab() -> None:
        orientation_col = [
            [
                sg.Push(),
                sg.Text("Rotation", pad=(0, 0)),
                sg.Push()
            ],
            [
                sg.Slider((-180, 180), 0, orientation="horizontal",
                          key="-TR_ROTATION-", enable_events=True,
                          expand_y=True, tick_interval=90, size=(30, 20))
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
                sg.Push(),
                sg.Column([[orientation_frame]]),
                sg.Column([[positon_frame]]),
                sg.Column([[scale_frame]]),
                sg.Push()
            ]
        ]

        return transformations_tab

    @staticmethod
    def __create_modifications_tab() -> None:
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
                sg.Button("Grayscale", key="-F_GRAYSCALE-"),
                sg.Button("Negative", key="-F_NEGATIVE-"),
                sg.Push()
            ],
            [
                sg.Push(),
                sg.Button("Red Monochrome", key="-F_R_MONOCHROME-"),
                sg.Button("Green Monochrome", key="-F_G_MONOCHROME-"),
                sg.Button("Blue Monochrome", key="-F_B_MONOCHROME-"),
                sg.Push()
            ]
        ]

        adjustments_col = [
            [
                sg.Push(),
                sg.Button("Center", key="-A_CENTER-"),
                sg.Push()
            ],
            [
                sg.Button("Shrink to fit", key="-A_SHRINK_TO_FIT-"),
            ]
        ]

        crop_frame = sg.Frame("Crop", layout=crop_col)
        filter_frame = sg.Frame("Filters", layout=filters_col)
        adjustment_frame = sg.Frame("Adjustments", layout=adjustments_col)

        modifications_tab = [
            [
                sg.Push(),
                sg.Column([[crop_frame]]),
                sg.Column([[filter_frame]]),
                sg.Column([[adjustment_frame]]),
                sg.Push()
            ]
        ]

        return modifications_tab
