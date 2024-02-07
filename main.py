from core.graphics.image import Image
from core.workspace import Workspace
from core.graphics.checkered_background import CheckeredBackground
from core.user_interface import UserInterface

import os
import PySimpleGUI as sg

ui = UserInterface("PySimpleImageEditor")

ws = Workspace()

image = Image(os.path.join("assets", "damn.png"))
image2 = Image(os.path.join("assets", "robot.png"))
image3 = Image(os.path.join("assets", "lake.jpg"))

pos_map: dict[str, tuple[int, int]] = {}

ws = Workspace()
ws.add_layer(image2)
ws.add_layer(image)
ws.add_layer(image3)

ui.update_layers(ws)
canvas = CheckeredBackground((500, 500))
thumbnail = CheckeredBackground((500, 500))


curr_image = None

while True:
    canvas.reset()
    thumbnail.reset()

    for (name, img) in reversed(ws.get_layers()):
        offset = (0, 0)
        if name in pos_map:
            offset = pos_map[name]

        canvas.cropped_paste(img, offset)

    ui.update_image(canvas)

    if curr_image is not None:
        thumbnail.cropped_paste(curr_image)
        ui.update_thumbnail(thumbnail.get_thumbnail((100, 100)))

    event, values = ui.get_input(timeout=100)

    if event in (sg.WINDOW_CLOSED, "Cancel"):
        break

    if event == "-WS_LAYERS-":
        curr_layer_name = ui.get_current_layer()
        curr_image = ws.get_layer(curr_layer_name)
        props = curr_image.get_properties()
        ui.update_value("-TR_ROTATION-", value=props.rotation)
        ui.update_value("-S_BRIGHTNESS-", value=(props.brightness - 1) * 100)
        ui.update_value("-S_CONTRAST-", value=(props.contrast - 1) * 100)
        ui.update_value("-S_SATURATION-", value=(props.saturation - 1) * 100)
        ui.update_value("-S_SHARPNESS-", value=(props.sharpness - 1) * 100)

    if event == "-WS_UP-":
        to_update = ui.get_current_layer()

        if to_update is not None:
            ws.move_layer_up(to_update)
            ui.update_layers(ws)
            ui.select_layer(to_update)

    if event == "-WS_DOWN-":
        to_update = ui.get_current_layer()

        if to_update is not None:
            ws.move_layer_down(to_update)
            ui.update_layers(ws)
            ui.select_layer(to_update)

    if event == "-WS_DELETE-":
        to_delete = ui.get_current_layer()

        if to_delete is not None:
            ws.delete_layer(to_delete)
            ui.update_layers(ws)
            curr_image.clear()

    if event == "-POS_UP-":
        curr_layer_name = ui.get_current_layer()
        if curr_layer_name not in pos_map:
            pos_map[curr_layer_name] = (0, 0)
        x, y = pos_map[curr_layer_name]
        pos_map[curr_layer_name] = (x, y - 5)

    if event == "-POS_DOWN-":
        curr_layer_name = ui.get_current_layer()
        if curr_layer_name not in pos_map:
            pos_map[curr_layer_name] = (0, 0)
        x, y = pos_map[curr_layer_name]
        pos_map[curr_layer_name] = (x, y + 5)

    if event == "-POS_LEFT-":
        curr_layer_name = ui.get_current_layer()
        if curr_layer_name not in pos_map:
            pos_map[curr_layer_name] = (0, 0)
        x, y = pos_map[curr_layer_name]
        pos_map[curr_layer_name] = (x - 5, y)

    if event == "-POS_RIGHT-":
        curr_layer_name = ui.get_current_layer()
        if curr_layer_name not in pos_map:
            pos_map[curr_layer_name] = (0, 0)
        x, y = pos_map[curr_layer_name]
        pos_map[curr_layer_name] = (x + 5, y)

    if event == "-SCALE_UP-":
        curr_image.scale((1.1, 1.1))

    if event == "-SCALE_DOWN-":
        curr_image.scale((0.9, 0.9))

    if event == "-SCALE_X_UP-":
        curr_image.scale((1.1, 1.0))

    if event == "-SCALE_X_DOWN-":
        curr_image.scale((0.9, 1.0))

    if event == "-SCALE_Y_UP-":
        curr_image.scale((1.0, 1.1))

    if event == "-SCALE_Y_DOWN-":
        curr_image.scale((1.0, 0.9))

    if event == "-TR_ROTATION-":
        curr_image.rotate(-values[event])

    if event == "-TR_FLIP_VERTICAL-":
        curr_image.flip_vertical()

    if event == "-TR_FLIP_HORIZONTAL-":
        curr_image.flip_horizontal()

    if event == "-S_BRIGHTNESS-":
        curr_image.apply_brightness(values[event] / 100 + 1)

    if event == "-S_SATURATION-":
        curr_image.apply_saturation(values[event] / 100 + 1)

    if event == "-S_CONTRAST-":
        curr_image.apply_contrast(values[event] / 100 + 1)

    if event == "-S_SHARPNESS-":
        curr_image.apply_sharpness(values[event] / 100 + 1)

ui.destroy()
exit()
