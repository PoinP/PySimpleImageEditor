from core.graphics.image import Image
from core.workspace import Workspace
from core.graphics.checkered_background import CheckeredBackground
from core.user_interface import UserInterface
from core.undo_redo_stack import UndoRedoStack

import os
import PySimpleGUI as sg

PosMap = dict[str, tuple[int, int]]
Event = (str, list[str])


class Program():
    def __init__(self, window_name: str) -> None:
        self.ui = UserInterface(window_name)
        self.ws = Workspace()
        self.action_stack = UndoRedoStack()
        self.pos_map = PosMap()
        self.curr_event = Event

        self.is_active = True
        self.set_undo = False

        self.canvas = CheckeredBackground((500, 500))
        self.thumbnail = CheckeredBackground((500, 500))

        self.curr_image: Image | None = None
        self.prev_image: Image | None = None

        image = Image(os.path.join("assets", "damn.png"))
        image2 = Image(os.path.join("assets", "robot.png"))
        image3 = Image(os.path.join("assets", "lake.jpg"))

        self.ws.add_layer(image2)
        self.ws.add_layer(image)
        self.ws.add_layer(image3)
        self.ui.update_layers(self.ws)

    def run(self) -> None:
        while self.is_active:
            self.canvas.reset()
            self.thumbnail.reset()

            self.__render_view()
            self.__render_thumbnail()

            self.curr_event = self.ui.get_input(timeout=250)

            self.__handle_events()

        self.ui.destroy()

    def __render_view(self):
        for (name, img) in reversed(self.ws.get_layers()):
            offset = (0, 0)
            if name in self.pos_map:
                offset = self.pos_map[name]

            self.canvas.cropped_paste(img, offset)

        self.ui.update_image(self.canvas)

    def __render_thumbnail(self):
        if self.curr_image is None:
            self.ui.update_thumbnail(None)
            return

        self.thumbnail.cropped_paste(self.curr_image)
        self.ui.update_thumbnail(self.thumbnail.get_thumbnail((100, 100)))

    def __handle_events(self):
        event, values = self.curr_event

        if event in (sg.WINDOW_CLOSED, "Cancel"):
            self.is_active = False
            return

        if event == "__TIMEOUT__":
            if self.set_undo:
                curr_layer_name = self.ui.get_current_layer()
                action = (curr_layer_name, self.prev_image)

                self.action_stack.clear_redo_stack()
                self.action_stack.add_undo_action(action)
                self.prev_image = self.curr_image.copy()
                self.set_undo = False
            return

        if event.startswith("-WS_"):
            self.__handle_workspace()
        elif event.startswith("-POS_"):
            self.__handle_postion()
        elif event.startswith("-SCALE_"):
            self.__handle_scale()
        elif event.startswith("-TR_"):
            self.__handle_transformation()
        elif event.startswith("-S_"):
            self.__handle_slider()
        else:
            self.__hande_menu()

    def __handle_workspace(self):
        event, values = self.curr_event

        if event == "-WS_LAYERS-":
            curr_layer_name = self.ui.get_current_layer()
            self.curr_image = self.ws.get_layer(curr_layer_name)
            self.prev_image = self.curr_image.copy()
            self.__update_slider_values()

        if event == "-WS_UP-":
            to_update = self.ui.get_current_layer()

            if to_update is not None:
                self.ws.move_layer_up(to_update)
                self.ui.update_layers(self.ws)
                self.ui.select_layer(to_update)

        if event == "-WS_DOWN-":
            to_update = self.ui.get_current_layer()

            if to_update is not None:
                self.ws.move_layer_down(to_update)
                self.ui.update_layers(self.ws)
                self.ui.select_layer(to_update)

        if event == "-WS_DELETE-":
            to_delete = self.ui.get_current_layer()

            if to_delete is not None:
                self.action_stack.clear_references(to_delete)
                self.action_stack.clear_redo_stack()
                self.ws.delete_layer(to_delete)
                self.ui.update_layers(self.ws)
                self.curr_image = None

    def __handle_postion(self) -> None:
        event, values = self.curr_event

        def change_pos_map(offset: tuple[int, int]) -> None:
            curr_layer_name = self.ui.get_current_layer()

            if curr_layer_name not in self.pos_map:
                self.pos_map[curr_layer_name] = (0, 0)

            x_offset, y_offset = offset

            x, y = self.pos_map[curr_layer_name]
            self.pos_map[curr_layer_name] = (x + x_offset, y + y_offset)

        if event == "-POS_UP-":
            change_pos_map((0, -5))

        elif event == "-POS_DOWN-":
            change_pos_map((0, 5))

        elif event == "-POS_LEFT-":
            change_pos_map((-5, 0))

        elif event == "-POS_RIGHT-":
            change_pos_map((5, 0))

    def __handle_scale(self) -> None:
        event, values = self.curr_event

        if event == "-SCALE_UP-":
            self.curr_image.scale((1.1, 1.1))
        elif event == "-SCALE_DOWN-":
            self.curr_image.scale((0.9, 0.9))
        elif event == "-SCALE_X_UP-":
            self.curr_image.scale((1.1, 1.0))
        elif event == "-SCALE_X_DOWN-":
            self.curr_image.scale((0.9, 1.0))
        elif event == "-SCALE_Y_UP-":
            self.curr_image.scale((1.0, 1.1))
        elif event == "-SCALE_Y_DOWN-":
            self.curr_image.scale((1.0, 0.9))
        else:
            return

        self.set_undo = True

    def __handle_transformation(self) -> None:
        event, values = self.curr_event

        if event == "-TR_ROTATION-":
            self.curr_image.rotate(-values[event])
        elif event == "-TR_FLIP_VERTICAL-":
            self.curr_image.flip_vertical()
        elif event == "-TR_FLIP_HORIZONTAL-":
            self.curr_image.flip_horizontal()
        else:
            return

        self.set_undo = True

    def __handle_slider(self) -> None:
        event, values = self.curr_event

        if event == "-S_BRIGHTNESS-":
            self.curr_image.apply_brightness(values[event] / 100 + 1)
        elif event == "-S_SATURATION-":
            self.curr_image.apply_saturation(values[event] / 100 + 1)
        elif event == "-S_CONTRAST-":
            self.curr_image.apply_contrast(values[event] / 100 + 1)
        elif event == "-S_SHARPNESS-":
            self.curr_image.apply_sharpness(values[event] / 100 + 1)
        else:
            return

        self.set_undo = True

    def __hande_menu(self) -> None:
        event, values = self.curr_event

        if event == "Undo":
            undo_action = self.action_stack.undo()
            if undo_action is not None:
                curr_layer_name = self.ui.get_current_layer()

                redo_action = (curr_layer_name, self.curr_image)
                self.action_stack.add_redo_action(redo_action)

                layer_name, image = undo_action
                self.ui.select_layer(layer_name)
                self.ws.update_layer(layer_name, image.copy())
                self.curr_image = self.ws.get_layer(layer_name)
                self.prev_image = self.curr_image.copy()

                self.__update_slider_values()

        if event == "Redo":
            redo_action = self.action_stack.redo()
            if redo_action is not None:
                curr_layer_name = self.ui.get_current_layer()

                undo_action = (curr_layer_name, self.curr_image)
                self.action_stack.add_undo_action(undo_action)

                layer_name, image = redo_action
                self.ui.select_layer(layer_name)
                self.ws.update_layer(layer_name, image.copy())
                self.curr_image = self.ws.get_layer(layer_name)
                self.prev_image = self.curr_image.copy()

                self.__update_slider_values()

        if event == "Convert to Grayscale":
            self.curr_image.convert_to_grayscale()
        elif event == "Convert to RGB":
            self.curr_image.convert_to_rgb()
        elif event == "Convert to RGBA":
            self.curr_image.convert_to_rgb()
        elif event == "Clear Effects":
            self.curr_image.clear_effects()
            self.__update_slider_values()
        else:
            return

        self.set_undo = True

    def __update_slider_values(self) -> None:
        props = self.curr_image.get_properties()

        def map_value(value) -> float:
            return (value - 1) * 100

        ui = self.ui

        ui.update_value("-TR_ROTATION-", value=props.rotation)
        ui.update_value("-S_BRIGHTNESS-", value=map_value(props.brightness))
        ui.update_value("-S_CONTRAST-", value=map_value(props.contrast))
        ui.update_value("-S_SATURATION-", value=map_value(props.saturation))
        ui.update_value("-S_SHARPNESS-", value=map_value(props.sharpness))


pr = Program("Woah")
pr.run()

# ui = UserInterface("PySimpleImageEditor")

# ur_stack = UndoRedoStack()
# ws = Workspace()

# image = Image(os.path.join("assets", "damn.png"))
# image2 = Image(os.path.join("assets", "robot.png"))
# image3 = Image(os.path.join("assets", "lake.jpg"))

# pos_map: dict[str, tuple[int, int]] = {}

# ws = Workspace()
# ws.add_layer(image2)
# ws.add_layer(image)
# ws.add_layer(image3)

# ui.update_layers(ws)
# canvas = CheckeredBackground((500, 500))
# thumbnail = CheckeredBackground((500, 500))


# curr_image = None
# mod_image = None
# add_stack = False


# while True:
#     canvas.reset()
#     thumbnail.reset()

#     for (name, img) in reversed(ws.get_layers()):
#         offset = (0, 0)
#         if name in pos_map:
#             offset = pos_map[name]

#         canvas.cropped_paste(img, offset)

#     ui.update_image(canvas)

#     if curr_image is not None:
#         thumbnail.cropped_paste(curr_image)
#         ui.update_thumbnail(thumbnail.get_thumbnail((100, 100)))

#     event, values = ui.get_input(timeout=500)
#     print(event)

#     if event in (sg.WINDOW_CLOSED, "Cancel"):
#         break

#     if event == "__TIMEOUT__":
#         print(add_stack)
#         if add_stack:
#             ur_stack.add_action((ui.get_current_layer(), mod_image))
#             mod_image = curr_image.copy()
#             add_stack = False
#         continue

#     if event == "-CROP_LEFT-":
#         x, y = curr_image.get_size()
#         curr_image.crop((10, 0, x, y))

#     if event == "-CROP_RIGHT-":
#         x, y = curr_image.get_size()
#         curr_image.crop((0, 0, x - 10, y))

#     add_stack = True

# ui.destroy()
# exit()
