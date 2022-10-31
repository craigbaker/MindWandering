#-*- coding: utf-8 -*-
#
#  mindwandering.py
#
#  Created by Craig Baker on 10/31/2022.
#

from tkinter import *
from tkinter import ttk

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageTk


def main():
    root = Tk()
    root.geometry('501x501')
    canvas = Canvas(root, width=500, height=500)
    canvas.pack()

    image = PIL.Image.new("RGBA", (5000, 5000), (255,255,255))
    draw = PIL.ImageDraw.Draw(image)
    fontsize = 512
    font = PIL.ImageFont.truetype("fonts/Merriweather/Merriweather-Black.ttf", fontsize)

    draw.text((10, 0), "Hello World", (0,0,0), font=font)
    img_resized = image.resize((500, 500), PIL.Image.Resampling.LANCZOS)

    image = PIL.ImageTk.PhotoImage(img_resized)
    imagesprite = canvas.create_image(250, 250, image=image)
    root.mainloop()


if __name__ == "__main__":
    main()