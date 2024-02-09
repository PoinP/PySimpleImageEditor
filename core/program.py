from core.graphics.image import Image
from core.graphics.image import ImageNotRecognizedError
from core.workspace import Workspace
from core.graphics.checkered_background import CheckeredBackground
from core.user_interface import UserInterface
from core.undo_redo_stack import UndoRedoStack

import os
import PySimpleGUI as sg

Event = (str, list[str])


class Program():
    def __init__(self, window_name: str) -> None:
        self.ui = UserInterface(window_name)
        self.ws = Workspace()
        self.action_stack = UndoRedoStack()
        self.curr_event = Event

        self.is_active = True
        self.set_undo = False

        self.canvas = CheckeredBackground((500, 500))
        self.thumbnail = CheckeredBackground((500, 500))

        self.save_location = None

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
        for (name, image) in reversed(self.ws.get_layers()):
            offset = image.get_properties().offset
            self.canvas.cropped_paste(image, offset)

        self.ui.update_image(self.canvas)

    def __render_thumbnail(self):
        if self.curr_image is None:
            self.ui.update_thumbnail(None)
            return

        offset = self.curr_image.get_properties().offset
        self.thumbnail.cropped_paste(self.curr_image, offset)
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
        elif event.startswith("-CROP_"):
            self.__handle_crop()
        elif event.startswith("-F_"):
            self.__handle_filters()
        elif event.startswith("-A_"):
            self.__handle_adjustments()
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

        if event == "-WS_ADD-":
            self.__open_image()

    def __handle_postion(self) -> None:
        event, values = self.curr_event

        if event == "-POS_UP-":
            self.curr_image.set_offset((0, -5))
        elif event == "-POS_DOWN-":
            self.curr_image.set_offset((0, 5))
        elif event == "-POS_LEFT-":
            self.curr_image.set_offset((-5, 0))
        elif event == "-POS_RIGHT-":
            self.curr_image.set_offset((5, 0))
        else:
            return

        self.set_undo = True

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

    def __handle_crop(self) -> None:
        event, values = self.curr_event

        if event == "-CROP_LEFT-":
            self.curr_image.crop((10, 0, 0, 0))
        elif event == "-CROP_RIGHT-":
            self.curr_image.crop((0, 0, 10, 0))
        elif event == "-CROP_TOP-":
            self.curr_image.crop((0, 10, 0, 0))
        elif event == "-CROP_BOT-":
            self.curr_image.crop((0, 0, 0, 10))
        else:
            return

        self.set_undo = True

    def __handle_filters(self) -> None:
        event, values = self.curr_event

        if event == "-F_GRAYSCALE-":
            self.curr_image.convert_to_grayscale()
        elif event == "-F_NEGATIVE-":
            self.curr_image.apply_negative()
        else:
            return

        self.set_undo = True

    def __handle_adjustments(self) -> None:
        event, values = self.curr_event

        if event == "-A_CENTER-":
            self.curr_image.center(self.canvas.get_size())
        elif event == "-A_SHRINK_TO_FIT-":
            self.curr_image.shrink_to_fit(self.canvas.get_size())
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

        if event == "Open an image":
            self.__open_image()
        elif event == "Save":
            self.__save_image()
        elif event == "Save as...":
            self.__save_image_as()

        if event == "Convert to RGB":
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

    def __open_image(self) -> None:
        image_path = self.ui.open_popup("Open an image")

        if image_path is None:
            return

        image: Image | None = None

        try:
            image = Image(image_path)
        except FileNotFoundError:
            error_message = "The following image does not exist:"
            self.ui.show_popup(error_message, image_path, title="Error")
            return
        except ImageNotRecognizedError:
            error_message = "This image's format is not supported:"
            self.ui.show_popup(error_message, image_path, title="Error")
            return

        self.ws.add_layer(image)
        self.ui.update_layers(self.ws)

    def __save_image(self) -> None:
        if self.save_location is None:
            self.__save_image_as()
        else:
            self.__save_image_as(self.save_location)

    def __save_image_as(self, image_path: str | None = None) -> None:
        if image_path is None:
            image_path = self.ui.save_popup("Choose location")

        if image_path is None:
            return

        head, tail = os.path.split(image_path)
        if not os.path.exists(head):
            error_message = "The following path does not exist!:"
            self.ui.show_popup(error_message, image_path, title="Error")
            return None

        to_save = Image(image=self.canvas.get_base_image())
        to_save.clear()

        for (name, image) in reversed(self.ws.get_layers()):
            offset = image.get_properties().offset
            to_save.cropped_paste(image, offset)

        try:
            to_save.save(image_path)
        except ValueError:
            error_message = "Output format couldn't be determined for the following image:" # noqa
            self.ui.show_popup(error_message, image_path, title="Error")
            return None
        except OSError:
            error_message = "An error occured while writing the image:"
            self.ui.show_popup(error_message, image_path, title="Error")
            return None

        self.save_location = image_path
        self.ui.show_popup("Image saved successfully!", title="Success")
