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
import datetime
import random

from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox

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
        self.image_width = 1600
        self.image_height = 1500
        self.screen_height = 1000
        self.scale_multiplier = 1

        self.speed = 0.5
        self.paused = False

        self.frame_t = 1. / 30

        self.frame_start = time.perf_counter()

        self.csv_fields = ["user_ID", "protocol", "timestamp", "text_format", "text", "action", "page", "question", "correct", "speed"]
        self.csv_file = None

        self.root = Tk()
        self.root.wm_title("MindWandering")
        self.root.geometry(str(self.image_width + 1) + "x" + str(self.screen_height + 100))

        self.main_frame = Frame(self.root)
        self.main_frame.pack()

        self.remaining_screens = [self.run_experimenter_selections,
            self.run_wait_begin,
            self.run_instructions,
            self.run_text_a,
            self.run_break,
            self.run_text_b,
            self.run_comprehension_questions,
            self.run_questionnaires,
            self.run_debriefing]
        
        self.next_screen()
        self.root.mainloop()


    def next_screen(self):
        self.main_frame.destroy() # destroy all the widgets from the previous screen
        self.main_frame = Frame(self.root)
        self.main_frame.pack()
        if len(self.remaining_screens) > 0:
            next_fn = self.remaining_screens.pop(0)
            next_fn()
        else:
            if self.csv_file is not None:
                self.csv_file.close()


    def run_experimenter_selections(self):
        '''
        The experimenter selects the CSV location, experiment protocol, userID, etc.
        '''
        datestamp = datetime.datetime.today().strftime("%b_%d_%Y_%H_%M_%S")
        default_csv_dir = os.path.expanduser("~")
        csv_filename = "experiment_%s.csv" % datestamp
        self.csv_path = os.path.join(default_csv_dir, csv_filename)

        csv_folder_label = Label(self.main_frame, text=default_csv_dir)
        csv_folder_label.pack()

        def do_csv_folder_dialog():
            csv_dir = filedialog.askdirectory(title="Choose destination folder for CSV", initialdir=default_csv_dir)
            if csv_dir != "":
                self.csv_path = os.path.join(csv_dir, csv_filename)
                csv_folder_label.config(text=csv_dir)

        csv_filename_button = ttk.Button(self.main_frame, text="Select CSV folder", command=do_csv_folder_dialog)
        csv_filename_button.pack(padx=100, pady=50)

        
        protocol_label = Label(self.main_frame, text="Select the experimental protocol. The initial choice has been randomly selected.")
        protocol_label.pack()

        protocol_options = "1", "2", "3", "4"
        protocol_var = StringVar(self.main_frame)
        self.protocol = random.choice(protocol_options)
        protocol_var.set(self.protocol) # default value
        def set_protocol():
            self.protocol = protocol_var.get()
        protocol_menu = OptionMenu(self.main_frame, protocol_var, protocol_options, command=set_protocol)
        protocol_menu.pack()


        userid_label = Label(self.main_frame, text="Enter the user_ID for this session")
        userid_label.pack()
        userid_var = StringVar(self.main_frame, value="0001")
        userid_entry = Entry(self.main_frame, textvariable=userid_var)
        userid_entry.pack()

        def finish_and_next():
            self.experiment_start_t = time.perf_counter()
            self.user_id = userid_var.get()

            if os.path.exists(self.csv_path):
                messagebox.showerror("CSV file error", "CSV file already exists: " + self.csv_path)
                return

            try:
                print ("csv path:", self.csv_path)
                self.csv_file = open(self.csv_path, "w", newline="", buffering=1) # buffering=1 writes each line
            except Exception as e:
                messagebox.showerror("CSV file error", "Could not create CSV file: " + str(e))
                return

            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.csv_fields)
            self.csv_writer.writeheader()
            self.next_screen()


        next_button = ttk.Button(self.main_frame, text="Next", command=finish_and_next)
        next_button.pack(padx=100, pady=50)
    

    def run_wait_begin(self):
        '''
        Wait for the subject to click the "Begin" button
        '''
        self.write_csv_row(action="started")
        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_instructions(self):
        '''
        Show the instructions
        '''
        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_text_a(self):
        '''
        Run the task for Text A
        '''
        self.canvas = Canvas(self.root, width=self.image_width, height=self.screen_height)
        self.canvas.pack()

        text = open(os.path.join(app_dir, "data/text_a.txt")).read()

        image = PIL.Image.new("L", (self.image_width * self.scale_multiplier, self.image_height * self.scale_multiplier), 255)# (255,255,255))
        draw = PIL.ImageDraw.Draw(image)
        fontsize = 24
        fontpath = os.path.join(app_dir, "fonts/Merriweather/Merriweather-Regular.ttf")
        font = PIL.ImageFont.truetype(fontpath, fontsize)
        lines = textwrap.wrap(text, width=117)
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

        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_break(self):
        '''
        Wait for the break to be over
        '''
        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_text_b(self):
        '''
        Run the task for Text B
        '''
        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_comprehension_questions(self):
        '''
        Display the comprehension questions and record the answers
        '''
        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_questionnaires(self):
        '''
        Display the questionnaires and record the answers
        '''
        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_debriefing(self):
        '''
        Display the debriefing
        '''
        next_button = ttk.Button(self.main_frame, text="Finished", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def write_csv_row(self, action):
        self.csv_writer.writerow({"user_ID": self.user_id, "protocol": self.protocol, "timestamp": "%09d" % int(time.perf_counter() - self.experiment_start_t), "action": action})
    

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
        print ("elapsed:", frame_elapsed, "delay:", frame_delay, "frame_t:", self.frame_t, "n:", self.n / self.image_height)
        

        self.canvas.yview_moveto(self.n / self.image_height)

        self.root.after(round(1000 * (self.frame_t - frame_delay)), self.do_scroll)


def main():
    mw = MindWandering()


if __name__ == "__main__":
    main()