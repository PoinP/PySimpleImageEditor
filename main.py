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
        canvas.cropped_paste(img)

    ui.update_image(canvas)

    if curr_image is not None:
        thumbnail.cropped_paste(curr_image)
        ui.update_thumbnail(thumbnail.get_thumbnail((100, 100)))

    event, values = ui.get_input(timeout=100)

    if event in (sg.WINDOW_CLOSED, "Cancel"):
        break

    if event == "-WS_LAYERS-":
        curr_image = ws.get_layer(values["-WS_LAYERS-"][0])
        props = curr_image.get_properties()
        ui.update_value("-POS_ROTATION-", value=props.rotation)
        ui.update_value("-S_BRIGHTNESS-", value=(props.brightness - 1) * 100)
        ui.update_value("-S_CONTRAST-", value=(props.contrast - 1) * 100)
        ui.update_value("-S_SATURATION-", value=(props.color_level - 1) * 100)
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

    if event == "-POS_ROTATION-":
        curr_image.rotate(values[event])

    if event == "-S_BRIGHTNESS-":
        curr_image.apply_brightness(values[event] / 100 + 1)

    if event == "-S_CONTRAST-":
        curr_image.apply_color_level(values[event] / 100 + 1)

    if event == "-S_SATURATION-":
        curr_image.apply_contrast(values[event] / 100 + 1)

    if event == "-S_SHARPNESS-":
        curr_image.apply_sharpness(values[event] / 100 + 1)

ui.destroy()
exit()
