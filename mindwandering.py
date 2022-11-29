#-*- coding: utf-8 -*-
#
#  mindwandering.py
#
#  Created by Craig Baker on 10/31/2022.
#

import sys
#stderr_f = open("/tmp/mindwandering_stderr.txt", "w") # find launch bugs
#sys.stdout = stderr_f
#sys.stderr = stderr_f

import os
import sys
import time
import textwrap
import csv
import datetime
import random
import functools

from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox, font

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageTk


app_dir = os.path.dirname(sys.argv[0])


class MindWandering:
    def __init__(self):
        window_title = "MindWandering"
        self.image_width = 1300 # 1600
        self.image_height = 1500
        self.screen_height = 700

        fontsize = 24
        fontpath = os.path.join(app_dir, "fonts/Merriweather/Merriweather-Regular.ttf")
        self.max_chars_per_line = 96

        ###

        self.root = Tk()
        self.root.wm_title(window_title)
        self.root.geometry(str(self.image_width + 1) + "x" + str(self.screen_height + 100))

        self.prepare_texts(fontpath, fontsize)

        self.csv_fields = ["user_ID", "protocol", "timestamp", "text_format", "text", "action", "page", "question", "correct", "speed"]
        self.csv_file = None

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

    
    def prepare_texts(self, fontpath, fontsize):
        '''
        Render text images for display in the scrolling and still tasks.
        This is done early because PIL text rendering incurs a significant delay.
        '''
        font = PIL.ImageFont.truetype(fontpath, fontsize)

        # Determine the maximum number of lines that can fit on one screen
        lines_per_screen = 8 # double-spaced lines
        text_height = 0
        text_width = None
        while text_height < self.screen_height - 100:
            lines_per_screen += 1
            text_width, text_height = get_text_image_size("\n\n".join(["M" * self.max_chars_per_line] * lines_per_screen), font)
        lines_per_screen -= 1
        print ("lines per screen:", lines_per_screen)

        # Render the texts
        self.rendered_texts_scrolling = {} # a single long page
        self.rendered_texts_still = {}     # paginated into "screens"
        for textid in "a", "b", "option1", "option2", "option3":
            print ("textid:", textid)
            text = open(os.path.join(app_dir, "data/text_%s.txt" % textid),
                        encoding="utf-8").read()
            lines = textwrap.wrap(text, width=self.max_chars_per_line)
            wrapped_text = "\n\n".join(lines)
            rendered_image = RenderedImage(wrapped_text, font, screen_height=self.screen_height)
            self.rendered_texts_scrolling[textid] = rendered_image

            if "option" not in textid:
                # paginated versions of the optional texts are not needed
                line_count = len(lines)
                pages = []
                for start_line in range(0, line_count, lines_per_screen):
                    wrapped_text = "\n\n".join(lines[start_line: start_line + lines_per_screen])
                    page_rendered_image = RenderedImage(wrapped_text, font, image_width=text_width, image_height=text_height)
                    pages.append(page_rendered_image)
                self.rendered_texts_still[textid] = pages
        print ("done preparing texts")


    def next_screen(self):
        '''
        Move on to the next screen in remaining_screens
        '''
        self.clear_main_frame()

        if len(self.remaining_screens) > 0:
            next_fn = self.remaining_screens.pop(0)
            next_fn()
        else:
            if self.csv_file is not None:
                self.csv_file.close()
            self.root.destroy()


    def do_simple_next(self, instructions, command):
        '''
        Show the instructions, with a "Next" button
        '''
        self.clear_main_frame()
        label = Label(self.main_frame, text=instructions)
        label.pack()
        next_button = ttk.Button(self.main_frame, text="Next", command=command)
        next_button.pack(padx=100, pady=50)

    
    def clear_main_frame(self):
        if self.main_frame is not None:
            self.main_frame.destroy() # destroy all the widgets from the previous screen
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, padx=30, pady=30)
        for n in range(10):
            self.main_frame.grid_rowconfigure(n, minsize=50)
            self.main_frame.grid_columnconfigure(n, minsize=10)


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

        label = Label(self.main_frame, text='''Welcome to the Reading Comprehension Study, where we are interested in how individuals process and comprehend content when reading.

You can end the experiment at any time by alerting the researcher.''')
        label.pack()

        next_button = ttk.Button(self.main_frame, text="Next", command=self.next_screen)
        next_button.pack(padx=100, pady=50)


    def run_task1(self):
        self.run_task(1)
    def run_task2(self):
        self.run_task(2)


    def run_task(self, task_number):
        '''
        Run task number 1 or 2, either still or scrolling depending on the protocol
        '''
        if (task_number == 1 and self.protocol in {"1", "3"}) or (task_number == 2 and self.protocol in {"2", "4"}):
            text_id = "a"
        else:
            text_id = "b"

        if (task_number == 1 and self.protocol in {"1", "2"}) or (task_number == 2 and self.protocol in {"3", "4"}):
            self.do_still_task(text_id)
        else:
            self.do_scrolling_task(text_id)

    
    def do_scrolling_task(self, main_text_id):
        '''
        The scrolling task. First prompt to select a comfortable speed, then scroll
        through the text, recording events in the CSV.
        '''

        def do_introduction():
            intro = '''
The text you will read, will be scrolling from the bottom to the top of the page.

Before you begin, you will set the speed of the scrolling text. Try to choose the speed that would be most comfortable to continuously read for the duration of the task.'''
            self.do_simple_next(intro, do_select)

        def do_select():
            self.clear_main_frame()
            instructions = Label(self.main_frame, text="Find your preferred speed by pressing the left or right arrow. When you have arrived at your preferred speed press SELECT.")
            instructions.pack(pady=10)

            speed_options = [200, 216, 232, 248, 264, 280, 296] # wpm

            scrolling_canvas = ScrollingCanvas(self.main_frame, self.rendered_texts_scrolling["option1"], self.image_width, self.screen_height, speed_options=speed_options, speed_selection_idx=3)
            scrolling_canvas.pack(fill=BOTH)

            def do_select():
                self.selected_speed = scrolling_canvas.speed
                self.write_csv_row(action="select", text_format="scroll", text=main_text_id, page="speed_select", speed=str(self.selected_speed))
                do_confirm()

            buttonframe = Frame(self.main_frame)
            self.make_arrow_button("left", buttonframe, scrolling_canvas)
            select_button = ttk.Button(buttonframe, text="Select", command=do_select)
            select_button.pack(side=LEFT, padx=10)
            self.make_arrow_button("right", buttonframe, scrolling_canvas)
            buttonframe.pack(pady=10)

            scrolling_canvas.do_scroll()

        def do_confirm():
            self.clear_main_frame()

            instructions = Label(self.main_frame, text="We would now like you to briefly read this example text to confirm this is your preferred speed.")
            instructions.pack(pady=10)

            def confirm_command():
                instructions.config(text="If it is not comfortable to continuously read at this speed, select RESET. Otherwise choose NEXT.")

                buttonframe = Frame(self.main_frame)
                reset_button = ttk.Button(buttonframe, text="Reset", command=do_reset)
                reset_button.pack(side=LEFT, padx=10)
                next_button = ttk.Button(buttonframe, text="Next", command=do_instructions)
                next_button.pack(side=LEFT, padx=10)
                buttonframe.pack(pady=10)
            
            scrolling_canvas = ScrollingCanvas(self.main_frame, self.rendered_texts_scrolling["option1"], self.image_width, self.screen_height, speed_options=[self.selected_speed])
            scrolling_canvas.pack(fill=BOTH)

            scrolling_canvas.do_scroll()
            confirm_wait_time = 30 * 1000
            #confirm_wait_time = 5 * 1000
            self.root.after(confirm_wait_time, confirm_command)

        def do_reset():
            self.clear_main_frame()
            do_select()

        def do_instructions():
            self.clear_main_frame()
            self.write_csv_row(action="confirm", text_format="scroll", text=main_text_id, page="speed_select", speed=str(self.selected_speed))

            instructions = ['''Thank you for selecting your speed, you will now begin the reading tasks.

Please read each text in full to be included in the study. A break will be available to you after completing the first text.''',
                "It is possible that your mind may wander from the text, this is understandable, try to be aware of when it occurs and return your attention to the text.",
                "If you need to briefly pause the scrolling text while reading, you can press the SPACEBAR. To continue, press the “C” button.",
                '''After you have finished reading the text, we will ask you some questions related to what you read.

To begin, click next.'''
            ]

            command = do_task
            for inst in instructions[::-1]:
                command = functools.partial(self.do_simple_next, inst, command)
            command()


        def do_task():
            self.clear_main_frame()
            instructions = Label(self.main_frame, text='If you need to briefly pause the scrolling text while reading, you can press the SPACEBAR. To continue, press the "C" button.')
            instructions.pack(pady=10)
            
            scrolling_canvas = ScrollingCanvas(self.main_frame, self.rendered_texts_scrolling[main_text_id], self.image_width, self.screen_height, done_command=self.next_screen, speed_options=[self.selected_speed])

            def pause_fn(event):
                scrolling_canvas.pause()
                self.write_csv_row(action="pause", text_format="scroll", text=main_text_id, page="scrolling_video", speed=str(self.selected_speed))

            def unpause_fn(event):
                scrolling_canvas.unpause()
                self.write_csv_row(action="unpause", text_format="scroll", text=main_text_id, page="scrolling_video", speed=str(self.selected_speed))

            self.root.bind("<space>", pause_fn)
            self.root.bind("c", unpause_fn)

            scrolling_canvas.pack(fill=BOTH)
            scrolling_canvas.do_scroll()

            self.write_csv_row(action="video_start", text_format="scroll", text=main_text_id, page="scrolling_video", speed=str(self.selected_speed))

        do_introduction()

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


    def do_still_task(self, main_text_id):
        '''
        The still task. Display the text page by page, recording Next and Mind Wandered
        events in the CSV.
        '''
        def do_instructions():
            self.clear_main_frame()
            #self.write_csv_row(action="confirm", text_format="scroll", text=main_text_id, page="speed_select", speed=str(self.selected_speed))

            instructions = ["The text you will read will be displayed on the screen, page by page. You can progress through the text by clicking NEXT.",
                "It is possible that your mind may wander from the text, this is understandable, anytime this occurs, click the “mind wandered” button and then return your attention to the text.",
                '''After you have finished reading the text, we will ask you some questions related to what you read.
To begin, click next.''']

            command = do_task
            for inst in instructions[::-1]:
                command = functools.partial(self.do_simple_next, inst, command)
            command()

        def do_task():
            self.clear_main_frame()
            instructions = Label(self.main_frame, text='You can progress through the text by clicking NEXT. If you mind wanders, click the purple button and continue reading.')
            instructions.pack(pady=10)

            paginated_canvas = PaginatedCanvas(self.main_frame, self.rendered_texts_still[main_text_id])
            paginated_canvas.pack(fill=BOTH)

            def do_next():
                self.write_csv_row(action="next", text_format="still", text=main_text_id, page="still_text_pg%d" % (paginated_canvas.current_page + 1))
                if paginated_canvas.at_last_page():
                    self.next_screen()
                else:
                    paginated_canvas.next_page()

            def do_mind_wandered():
                self.write_csv_row(action="mind wandered", text_format="still", text=main_text_id, page="still_text_pg%d" % (paginated_canvas.current_page + 1))
            
            buttonframe = Frame(self.main_frame)
            wandered_button = ttk.Button(buttonframe, text="Mind Wandered", command=do_mind_wandered)
            wandered_button.pack(side=LEFT, padx=10)
            next_button = ttk.Button(buttonframe, text="Next", command=do_next)
            next_button.pack(side=LEFT, padx=10)
            buttonframe.pack(pady=10)

            self.write_csv_row(action="still_start", text_format="still", text=main_text_id)

        do_instructions()

        return


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


    def write_csv_row(self, action, **row_dict):
        row_dict["user_ID"] = self.user_id
        row_dict["protocol"] = self.protocol
        row_dict["timestamp"] = "%09d" % int(time.perf_counter() - self.experiment_start_t)
        row_dict["action"] = action

        self.csv_writer.writerow(row_dict)


def wrap_text(text, max_chars_per_line=96):
    lines = textwrap.wrap(text, width=max_chars_per_line)
    wrapped_text = "\n\n".join(lines)
    return wrapped_text


def get_text_image_size(lines_text, font):
    '''
    Use a scratch image to determine the rendered text dimensions in pixels
    lines_text: a string containing newlines
    '''
    
    image = PIL.Image.new("RGBA", (1,1))
    draw = PIL.ImageDraw.Draw(image)
    _, _, image_width, image_height = draw.textbbox((0, 0), lines_text, font) #draw.textsize(lines_text, font)

    # long lines seem to get cut off
    image_width += 20
    image_height += 20

    return image_width, image_height


class RenderedImage:
    def __init__(self, wrapped_text, font, image_width=None, image_height=None, screen_height=None):
        '''
        wrapped_text: a string, the text to be rendered, with newlines
        font: a PIL.ImageFont
        image_width: a width in pixels, or None for automatic
        image_height: a height in pixels, or None for automatic
        screen_height: an integer, the height of the scrolling screen,
            used to start the text at 1/2 screen height and end it off-screen
        '''
        if image_width is None:
            image_width, image_height = get_text_image_size(wrapped_text, font)

        # calculations for determining scrolling speed
        # get the number of words per vertical pixel
        word_count = len(wrapped_text.replace("\n", " ").replace("  ", " ").split())
        self.words_per_vpixel = word_count / image_height

        if screen_height is not None:
            # the top of the text starts at the center of the screen (.5), and the end
            # finishes by scrolling off the screen (1.)
            image_height += int(1.5 * screen_height)
            start_height = screen_height / 2.
        else:
            # the text starts at the top of the page
            start_height = 10
        
        self.image_width = image_width
        self.image_height = image_height

        print ("image")
        self.image = PIL.Image.new("L", (image_width, image_height), 255)
        draw = PIL.ImageDraw.Draw(self.image)
        draw.text((10, start_height), wrapped_text, 0, font=font)

        #if scale_multiplier != 1.:
        #    print ("resize")
        #    self.image = image.resize((image_width, image_height), PIL.Image.Resampling.LANCZOS)

        print ("photoimage")
        self.photo_image = PIL.ImageTk.PhotoImage(self.image)


class PaginatedCanvas: # for the Still task
    def __init__(self, parent_widget, rendered_images):
        self.rendered_images = rendered_images

        canvas_width = 0
        canvas_height = 0
        for im in rendered_images:
            canvas_width = max(canvas_width, im.image_width)
            canvas_height = max(canvas_height, im.image_height)

        self.canvas = Canvas(parent_widget, width=canvas_width, height=canvas_height)

        self.current_page = 0
        self.show_current_page()

    
    def next_page(self):
        assert not self.at_last_page()
        self.current_page += 1
        self.show_current_page()


    def at_last_page(self):
        return self.current_page == len(self.rendered_images) - 1

    
    def show_current_page(self):
        '''
        Show the current page
        '''
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, anchor=NW, image=self.rendered_images[self.current_page].photo_image)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def pack(self, *args, **kwargs):
            self.canvas.pack(*args, **kwargs)


class ScrollingCanvas:
    '''
    A widget that scrolls an image vertically at a specific speed
    '''
    def __init__(self, parent_widget, rendered_image, image_width, screen_height, speed_options, speed_selection_idx=0, done_command=None):
            '''
            speed_options: a list of speeds in wpm
            speed_selection_idx: the initial speed selection, an index into speed_options
            '''
            self.parent_widget = parent_widget
            self.rendered_image = rendered_image
            self.done_command = done_command
            self.speed_options = speed_options
            self.speed_selection_idx = speed_selection_idx
            self.screen_height = screen_height

            self.canvas = Canvas(parent_widget, width=image_width, height=screen_height - 100)
            self.canvas.create_image(10, 10, anchor=NW, image=self.rendered_image.photo_image)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            self.n = 0
            self.paused = False
            self.speed = self.speed_options[self.speed_selection_idx]
            self.frame_start = time.perf_counter()
            self.set_rate()

            self.recent_delays = []


    def pack(self, *args, **kwargs):
            self.canvas.pack(*args, **kwargs)
    

    def do_scroll(self):
        if self.paused:
            self.parent_widget.after(100, self.do_scroll)
            return

        self.n += 1 # self.speed / 200.
        if self.n > self.rendered_image.image_height - self.screen_height:
            if self.done_command is not None:
                self.done_command()
                return
            else:
                self.n = 0

        frame_end = time.perf_counter()
        frame_elapsed = frame_end - self.frame_start
        frame_delay = frame_elapsed - self.frame_t
        frame_delay = min(frame_delay, self.frame_t)
        self.recent_delays.append(frame_delay)
        mean_delay = sum(self.recent_delays) / len(self.recent_delays)
        #print ("mean delay:", mean_delay, "frame_t:", self.frame_t)
        if len(self.recent_delays) > 10:
            self.recent_delays = self.recent_delays[-10:]
        self.frame_start = frame_end
        #print ("elapsed:", frame_elapsed, "delay:", frame_delay, "frame_t:", self.frame_t, "n:", self.n / self.image_height)
        
        self.canvas.yview_moveto(self.n / self.rendered_image.image_height)
        self.parent_widget.after(round(1000 * (self.frame_t - mean_delay)), self.do_scroll)


    def increase_scrolling_speed(self):
        assert self.speed_options is not None
        if self.speed_selection_idx < len(self.speed_options) - 1:
            self.speed_selection_idx += 1
            self.speed = self.speed_options[self.speed_selection_idx]
            self.set_rate()

    
    def decrease_scrolling_speed(self):
        assert self.speed_options is not None
        if self.speed_selection_idx > 0:
            self.speed_selection_idx -= 1
            self.speed = self.speed_options[self.speed_selection_idx]
            self.set_rate()


    def set_rate(self):
        self.frame_t = 60. * self.rendered_image.words_per_vpixel / self.speed
    

    def pause(self):
        self.paused = True


    def unpause(self):
        self.paused = False


def main():
    mw = MindWandering()


if __name__ == "__main__":
    main()