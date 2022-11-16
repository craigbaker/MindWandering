#-*- coding: utf-8 -*-
#
#  mindwandering.py
#
#  Created by Craig Baker on 10/31/2022.
#

import os
import sys
import time
import textwrap
import csv

from tkinter import *
from tkinter import ttk

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageTk


#stderr_f = open("/tmp/mindwandering_stderr.txt", "w")
#sys.stdout = stderr_f
#sys.stderr = stderr_f

app_dir = os.path.dirname(sys.argv[0])


class MindWandering:
    def __init__(self):
        self.image_width = 800
        self.image_height = 1500
        self.screen_height = 500
        self.scale_multiplier = 1

        self.user_ID = "0001"
        self.protocol = "1"

        self.speed = 0.5
        self.paused = False

        self.frame_t = 1. / 30

        self.experiment_start_t = time.perf_counter()
        self.frame_start = self.experiment_start_t

        csv_fields = ["user_ID", "protocol", "timestamp", "text_format", "text", "action", "page", "question", "correct", "speed"]
        self.csv_file = open("/tmp/mindwandering.csv", "w", newline="")
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=csv_fields)
        self.csv_writer.writeheader()
        self.write_csv_row(action="started")

        self.root = Tk(className=" MindWandering") # className is window title, initial char is lowered
        self.root.geometry(str(self.image_width + 1) + "x" + str(self.screen_height + 100))

        self.canvas = Canvas(self.root, width=self.image_width, height=self.screen_height)
        self.canvas.pack()

        text = open(os.path.join(app_dir, "data/text_a.txt")).read()

        image = PIL.Image.new("L", (self.image_width * self.scale_multiplier, self.image_height * self.scale_multiplier), 255)# (255,255,255))
        draw = PIL.ImageDraw.Draw(image)
        fontsize = 24
        fontpath = os.path.join(app_dir, "fonts/Merriweather/Merriweather-Regular.ttf")
        font = PIL.ImageFont.truetype(fontpath, fontsize)
        lines = textwrap.wrap(text, width=60)
        lines_text = "\n\n".join(lines)
        draw.text((10, self.screen_height * self.scale_multiplier / 2.), lines_text, 0, font=font)

        self.image = image.resize((self.image_width, self.image_height), PIL.Image.Resampling.LANCZOS)

        image = PIL.ImageTk.PhotoImage(self.image)
        self.canvas.create_image(10, 10, anchor=NW, image=image)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.pack()

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


    def write_csv_row(self, action):
        self.csv_writer.writerow({"user_ID": self.user_ID, "protocol": self.protocol, "timestamp": "%09d" % int(time.perf_counter() - self.experiment_start_t), "action": action})
    

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

        self.n += self.speed
        self.n = self.n % (self.image_height - self.screen_height)

        
        frame_end = time.perf_counter()
        frame_elapsed = frame_end - self.frame_start
        frame_delay = frame_elapsed - self.frame_t
        self.frame_start = frame_end
        #print ("elapsed:", frame_elapsed, "delay:", frame_delay, "frame_t:", self.frame_t)
        

        self.canvas.yview_moveto(self.n / self.image_height)

        self.root.after(round(1000 * (self.frame_t - frame_delay)), self.do_scroll)


def main():
    mw = MindWandering()


if __name__ == "__main__":
    main()