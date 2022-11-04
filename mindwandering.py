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
        self.image_height = 1500
        self.screen_height = 500
        self.scale_multiplier = 1

        self.speed = 1
        self.paused = False

        self.frame_t = 1. / 30
        self.frame_start = time.perf_counter()

        self.root = Tk()
        self.root.geometry(str(self.image_width + 1) + "x" + str(self.screen_height + 100))

        #self.canvas = Canvas(self.root, width=self.image_width, height=self.image_height)
        #self.canvas.pack()

        image = PIL.Image.new("L", (self.image_width * self.scale_multiplier, self.image_height * self.scale_multiplier), 255)# (255,255,255))
        draw = PIL.ImageDraw.Draw(image)
        fontsize = 24
        font = PIL.ImageFont.truetype("fonts/Merriweather/Merriweather-Black.ttf", fontsize)
        lines = textwrap.wrap(text, width=60)
        lines_text = "\n".join(lines)
        lines_text = "\n\n".join([lines_text] * 5)
        draw.text((10, self.screen_height * self.scale_multiplier / 2.), lines_text, 0, font=font)

        self.image = image.resize((self.image_width, self.image_height), PIL.Image.Resampling.LANCZOS)

        #self.do_scroll()
        #self.root.after(1, lambda: self.do_scroll())
        #self.root.mainloop()

        self.label = Label(self.root)#, width=self.image_width, height=self.screen_height)
        self.label.pack()

        buttonframe = Frame(self.root)
        buttonframe.pack()

        style = ttk.Style()
        style.layout(
            'Left.TButton',[
                ('Button.focus', {'children': [
                    ('Button.leftarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'}
                         )]}
                     )]}
                 )]
            )
        style.configure('Left.TButton',font=('','40','bold'), width=1, arrowcolor='black')
        self.lbutton = ttk.Button(buttonframe, style='Left.TButton', text='', command=self.decrease_speed)
        self.lbutton.pack(side=LEFT)
        #self.lbutton.grid(column=2)

        style.layout(
            'Right.TButton',[
                ('Button.focus', {'children': [
                    ('Button.rightarrow', None),
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nsew'}
                         )]}
                     )]}
                 )]
            )
        style.configure('Right.TButton',font=('','40','bold'), width=1, arrowcolor='black')
        self.rbutton = ttk.Button(buttonframe, style='Right.TButton', text='', command=self.increase_speed)
        self.rbutton.pack(side=LEFT)
        #self.rbutton.grid(column=3)

        self.root.bind("<space>", lambda e: self.pause())
        self.root.bind("c", lambda e: self.unpause())

        self.n = 0
        self.do_scroll()
        self.root.mainloop()

        #while True:
        #    self.do_scroll()


    def increase_speed(self):
        self.speed *= 2

    
    def decrease_speed(self):
        self.speed /= 2


    def pause(self):
        self.paused = True


    def unpause(self):
        self.paused = False
    

    def do_scroll(self):
        if self.paused:
            self.root.after(100, self.do_scroll)
            return

        #cropped_image = self.image.crop((0, n, self.image_width * self.scale_multiplier, self.screen_height * self.scale_multiplier + n))
        cropped_image = self.image.crop((0, self.n, self.image_width, self.screen_height + self.n))
        
        image = PIL.ImageTk.PhotoImage(cropped_image)
        #imagesprite = self.canvas.create_image(self.image_width / 2, self.screen_height / 2, image=image)
        #self.canvas.update()

        self.label.config(image=image)
        self.label.image = image # otherwise image will be garbage collected

        #self.root.update_idletasks()
        #self.root.update()
        #time.sleep(0.01)

        self.n += self.speed
        self.n = self.n % (self.image_height - self.screen_height)

        frame_end = time.perf_counter()
        frame_elapsed = frame_end - self.frame_start
        frame_delay = max(0., self.frame_t - frame_elapsed)
        self.frame_start = frame_end
        #print ("elapsed:", frame_elapsed, "delay:", frame_delay)

        self.root.after(round(1000 * frame_delay), self.do_scroll)

        #self.root.update()
        #if self.n % 100 == 0:
        #    self.root.update_idletasks()


text = "In the study today, you read two chapters of a Bill Bryson book and completed questions regarding the task and attention questionnaires. We conducted this study to assess comprehension and mind wandering when reading text. In particular we are interested in the differences between scrolling text and static text. We appreciate you giving your time and if you have any questions please contact us."


def main():
    mw = MindWandering()


if __name__ == "__main__":
    main()