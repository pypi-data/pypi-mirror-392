from PIL import Image, ImageTk
from tkinter import Tk, Label

def showimage(image_path, width, height):
    img = Image.open(image_path).resize((width, height))
    img.show()

def createimagewidget(
    root,
    width,
    height,
    image_path,
    horizontal=0,
    vertical=0,
    start_pos=False,
    drag=True,
    clickable=True,
    on_click=None
):
    pil_img = Image.open(image_path).resize((width, height))
    tk_img = ImageTk.PhotoImage(pil_img)

    label = Label(root, image=tk_img, bg="white")
    label.image = tk_img
    label.place(x=horizontal, y=vertical)

    drag_data = {"x": 0, "y": 0}

    def handle_click(event):
        if on_click:
            on_click(event)
        else:
            print("Image clicked at:", event.x, event.y)

    def on_drag_start(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def on_drag_motion(event):
        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]
        x = label.winfo_x() + dx
        y = label.winfo_y() + dy
        label.place(x=x, y=y)
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    if clickable:
        label.bind("<Button-1>", handle_click)
    if drag:
        label.bind("<ButtonPress-1>", on_drag_start)
        label.bind("<B1-Motion>", on_drag_motion)

    return label
