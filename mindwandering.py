#-*- coding: utf-8 -*-
#
#  mindwandering.py
#
#  Created by Craig Baker on 10/31/2022.
#

import time
import textwrap

from tkinter import *
from tkinter import ttk

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageTk


class MindWandering:
    def __init__(self):
        self.image_width = 800
        self.image_height = 2000
        self.screen_height = 500
        self.scale_multiplier = 2

        self.root = Tk()
        self.root.geometry(str(self.image_width + 1) + "x" + str(self.screen_height + 1))

        self.canvas = Canvas(self.root, width=self.image_width, height=self.image_height)
        self.canvas.pack()

        self.image = PIL.Image.new("RGBA", (self.image_width * self.scale_multiplier, self.image_height * self.scale_multiplier), (255,255,255))
        draw = PIL.ImageDraw.Draw(self.image)
        fontsize = 48
        font = PIL.ImageFont.truetype("fonts/Merriweather/Merriweather-Black.ttf", fontsize)
        lines = textwrap.wrap(text, width=60)
        lines_text = "\n".join(lines)
        lines_text = "\n\n".join([lines_text] * 5)
        draw.text((10, self.screen_height * self.scale_multiplier / 2.), lines_text, (0, 0, 0), font=font)

        self.do_scroll()
        #self.root.after(1, lambda: self.do_scroll())
        #self.root.mainloop()


    def do_scroll(self):

        n = 0
        while True:
            cropped_image = self.image.crop((0, n, self.image_width * self.scale_multiplier, self.screen_height * self.scale_multiplier + n))
            img_resized = cropped_image.resize((self.image_width, self.screen_height), PIL.Image.Resampling.LANCZOS)

            image = PIL.ImageTk.PhotoImage(img_resized)
            imagesprite = self.canvas.create_image(self.image_width / 2, self.screen_height / 2, image=image)
            self.root.update_idletasks()
            self.root.update()

            n += 2
            n = n % (self.image_height - self.screen_height)


text = "In the study today, you read two chapters of a Bill Bryson book and completed questions regarding the task and attention questionnaires. We conducted this study to assess comprehension and mind wandering when reading text. In particular we are interested in the differences between scrolling text and static text. We appreciate you giving your time and if you have any questions please contact us."


def main():
    mw = MindWandering()


if __name__ == "__main__":
    main()