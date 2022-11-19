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
from tkinter import filedialog, messagebox, font

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
        self.image_width = 800# 1600
        self.image_height = 1500
        self.screen_height = 500 #1000
        self.scale_multiplier = 1

        self.paused = False

        self.csv_fields = ["user_ID", "protocol", "timestamp", "text_format", "text", "action", "page", "question", "correct", "speed"]
        self.csv_file = None

        self.root = Tk()
        self.root.wm_title("MindWandering")
        self.root.geometry(str(self.image_width + 1) + "x" + str(self.screen_height + 100))

        self.main_frame = None

        self.remaining_screens = [self.run_experimenter_selections,
            self.run_instructions,
            self.run_task1,
            self.run_break,
            self.run_task2,
            self.run_comprehension_questions,
            self.run_questionnaires,
            self.run_debriefing]
        
        self.next_screen()
        self.root.mainloop()


    def next_screen(self):
        '''
        Move on to the next screen in remaining_screens
        '''
        if self.main_frame is not None:
            self.main_frame.destroy() # destroy all the widgets from the previous screen
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, padx=30, pady=30)
        for n in range(10):
            self.main_frame.grid_rowconfigure(n, minsize=50)
            self.main_frame.grid_columnconfigure(n, minsize=10)

        if len(self.remaining_screens) > 0:
            next_fn = self.remaining_screens.pop(0)
            next_fn()
        else:
            if self.csv_file is not None:
                self.csv_file.close()
            self.root.destroy()


    def run_experimenter_selections(self):
        '''
        The experimenter selects the CSV location, experiment protocol, userID, etc.
        '''
        large_bold_font = font.Font(family=font.nametofont("TkDefaultFont").cget("family"),
            weight=font.BOLD, size=24)
        bold_font = font.Font(family=font.nametofont("TkDefaultFont").cget("family"),
            weight=font.BOLD)

        heading_label = Label(self.main_frame, font=large_bold_font, text="Experiment Settings")
        heading_label.pack(anchor=W, pady=30)

        datestamp = datetime.datetime.today().strftime("%b_%d_%Y_%H_%M_%S")
        default_csv_dir = os.path.expanduser("~")
        csv_filename = "experiment_%s.csv" % datestamp
        self.csv_path = os.path.join(default_csv_dir, csv_filename)

        csv_frame = Frame(self.main_frame)
        csv_frame.pack(anchor=W, fill=BOTH, pady=30)
        
        csv_instructions_label = Label(csv_frame, font=bold_font, text="Choose destination folder for the CSV")
        csv_instructions_label.grid(row=0, column=0, sticky=W)
        csv_folder_label = Label(csv_frame, text="Current selection: " + default_csv_dir)
        csv_folder_label.grid(row=1, column=1, sticky=W, padx=0)


        def do_csv_folder_dialog():
            csv_dir = filedialog.askdirectory(title="Choose destination folder for the CSV", initialdir=default_csv_dir)
            if csv_dir != "":
                self.csv_path = os.path.join(csv_dir, csv_filename)
                csv_folder_label.config(text="Current selection: " + csv_dir)

        csv_filename_button = ttk.Button(csv_frame, text="Select CSV folder", command=do_csv_folder_dialog)
        csv_filename_button.grid(row=1, column=0, sticky=W, padx=20, pady=5)

        protocol_frame = Frame(self.main_frame)
        protocol_frame.pack(anchor=W, fill=BOTH, pady=30)
        protocol_label = Label(protocol_frame, font=bold_font, text="Select the experimental protocol. The initial choice has been randomly selected.")
        protocol_label.grid(row=0, column=0, sticky=W)

        protocol_options = "1", "2", "3", "4"
        protocol_var = StringVar(protocol_frame)
        self.protocol = random.choice(protocol_options)
        protocol_var.set(self.protocol) # default value
        def set_protocol(protocol):
            self.protocol = protocol
        protocol_menu = OptionMenu(protocol_frame, protocol_var, *protocol_options, command=set_protocol)
        protocol_menu.grid(row=1, column=0, sticky=W, padx=30)


        userid_frame = Frame(self.main_frame)
        userid_frame.pack(anchor=W, fill=BOTH, pady=30)
        userid_label = Label(userid_frame, font=bold_font, text="Enter the user_ID for this session")
        userid_label.grid(row=0, column=0, sticky=W)
        userid_var = StringVar(userid_frame, value="0001")
        userid_entry = Entry(userid_frame, textvariable=userid_var)
        userid_entry.grid(row=1, column=0, sticky=W, padx=20)

        def finish_and_next():
            self.experiment_start_t = time.perf_counter()
            self.user_id = userid_var.get()

            if os.path.exists(self.csv_path):
                messagebox.showerror("CSV file error", "CSV file already exists: " + self.csv_path)
                return

            try:
                self.csv_file = open(self.csv_path, "w", newline="", buffering=1) # buffering=1 writes each line
            except Exception as e:
                messagebox.showerror("CSV file error", "Could not create CSV file: " + str(e))
                return

            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.csv_fields)
            self.csv_writer.writeheader()
            self.next_screen()


        next_button = ttk.Button(self.main_frame, text="Run experiment", command=finish_and_next)
        next_button.pack(anchor=W, pady=20)


    def run_instructions(self):
        '''
        Show the instructions
        '''
        self.write_csv_row(action="started")

        label = Label(self.main_frame, text="Instructions")
        label.pack()

        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_task1(self):
        self.run_task(1)
    def run_task2(self):
        self.run_task(2)


    def run_task(self, task_number):
        '''
        Run the task for Text A
        '''
        print ("running task:", task_number, "protocol:", self.protocol)
        if (task_number == 1 and self.protocol in {"1", "3"}) or (task_number == 2 and self.protocol in {"2", "4"}):
            text_id = "a"
        else:
            text_id = "b"

        text = open(os.path.join(app_dir, "data/text_%s.txt" % text_id)).read()

        if (task_number == 1 and self.protocol in {"1", "2"}) or (task_number == 2 and self.protocol in {"3", "4"}):
            self.do_still_task(text)
        else:
            self.do_scrolling_task(text, "example text")

    
    def do_scrolling_task(self, main_text, example_text):
        '''
        The scrolling task. First prompt to select a comfortable speed, then scroll
        through the text, recording events in the CSV.
        '''
        print ("scrolling task")

        self.main_frame.bind("<space>", lambda e: self.pause())
        self.main_frame.bind("c", lambda e: self.unpause())

        def do_select():
            instructions = Label(self.main_frame, text="Find your preferred speed by pressing the left or right arrow. When you have arrived at your preferred speed press SELECT.")
            instructions.pack(pady=10)

            example_text = open(os.path.join(app_dir, "data/text_option1.txt")).read()
            
            scrolling_canvas = ScrollingCanvas(self.main_frame, example_text, self.image_width, self.image_height, self.screen_height, self.scale_multiplier)
            scrolling_canvas.pack(fill=BOTH)

            buttonframe = Frame(self.main_frame)
            self.make_arrow_button("left", buttonframe, scrolling_canvas)
            select_button = ttk.Button(buttonframe, text="Select", command=do_reset)
            select_button.pack(side=LEFT, padx=10)
            self.make_arrow_button("right", buttonframe, scrolling_canvas)
            buttonframe.pack(pady=10)

            scrolling_canvas.do_scroll()

        def do_reset():
            print ("do_reset")

        def do_select_done():
            pass

        def do_instructions():
            pass

        def do_task():
            pass

        do_select()

        return


    def make_arrow_button(self, direction, parent, scrolling_canvas):
        '''
        direction: "left" or "right"
        '''
        if direction == "left":
            sticky = "nswe"
            command = scrolling_canvas.decrease_scrolling_speed
        else:
            sticky = "nsew"
            command = scrolling_canvas.increase_scrolling_speed

        style = ttk.Style()
        style.layout(
            '%s.TButton' % direction.capitalize(),[
                ('Button.focus', {'children': [
                    ('Button.%sarrow' % direction, None),
                    ('Button.padding', {'sticky': sticky, 'children': [
                        ('Button.label', {'sticky': sticky}
                        )]}
                    )]}
                )]
            )
        style.configure('%s.TButton' % direction.capitalize(), font=('','40','bold'), width=1, arrowcolor='black')
        button = ttk.Button(parent, style='%s.TButton' % direction.capitalize(), text='', command=command)
        button.pack(side=LEFT)
        return button

        '''
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
        '''



    def do_still_task(self, text):
        '''

        '''
        label = Label(self.main_frame, text="Still task: " + text[:40] + "...")
        label.pack()

        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_break(self):
        '''
        Wait for the break to be over
        '''
        label = Label(self.main_frame, text="Break")
        label.pack()

        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_comprehension_questions(self):
        '''
        Display the comprehension questions and record the answers
        '''
        label = Label(self.main_frame, text="Comprehension questions")
        label.pack()

        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_questionnaires(self):
        '''
        Display the questionnaires and record the answers
        '''
        label = Label(self.main_frame, text="Questionnaires")
        label.pack()

        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_debriefing(self):
        '''
        Display the debriefing
        '''
        label = Label(self.main_frame, text="Debriefing")
        label.pack()

        next_button = ttk.Button(self.main_frame, text="Finished", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def write_csv_row(self, action):
        self.csv_writer.writerow({"user_ID": self.user_id, "protocol": self.protocol, "timestamp": "%09d" % int(time.perf_counter() - self.experiment_start_t), "action": action})


class ScrollingCanvas:
    def __init__(self, parent_widget, text, image_width, image_height, screen_height, scale_multiplier):
            self.parent_widget = parent_widget
            self.image_height = image_height
            self.screen_height = screen_height
            self.canvas = Canvas(parent_widget, width=image_width, height=screen_height - 100)

            image = PIL.Image.new("L", (image_width * scale_multiplier, image_height * scale_multiplier), 255)# (255,255,255))
            draw = PIL.ImageDraw.Draw(image)
            fontsize = 24
            fontpath = os.path.join(app_dir, "fonts/Merriweather/Merriweather-Regular.ttf")
            font = PIL.ImageFont.truetype(fontpath, fontsize)
            lines = textwrap.wrap(text, width=117)
            lines_text = "\n\n".join(lines)
            draw.text((10, screen_height * scale_multiplier / 2.), lines_text, 0, font=font)

            self.image = image.resize((image_width, image_height), PIL.Image.Resampling.LANCZOS)

            self.photo_image = PIL.ImageTk.PhotoImage(self.image)
            self.canvas.create_image(10, 10, anchor=NW, image=self.photo_image)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            self.n = 0
            self.paused = False
            self.speed = 0.5
            self.frame_start = time.perf_counter()
            self.frame_t = 1. / 30


    def pack(self, *args, **kwargs):
            self.canvas.pack(*args, **kwargs)
    

    def do_scroll(self):
        if self.paused:
            self.parent_widget.after(100, self.do_scroll)
            return

        self.n += self.speed
        self.n = self.n % (self.image_height - self.screen_height)

        frame_end = time.perf_counter()
        frame_elapsed = frame_end - self.frame_start
        frame_delay = frame_elapsed - self.frame_t
        self.frame_start = frame_end
        #print ("elapsed:", frame_elapsed, "delay:", frame_delay, "frame_t:", self.frame_t, "n:", self.n / self.image_height)
        
        self.canvas.yview_moveto(self.n / self.image_height)
        self.parent_widget.after(round(1000 * (self.frame_t - frame_delay)), self.do_scroll)


    def increase_scrolling_speed(self):
        self.speed *= 2

    
    def decrease_scrolling_speed(self):
        self.speed /= 2


    def pause(self):
        self.paused = True


    def unpause(self):
        self.paused = False


def main():
    mw = MindWandering()


if __name__ == "__main__":
    main()