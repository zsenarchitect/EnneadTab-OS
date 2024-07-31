import sys
import os
import random
import tkinter as tk
import time

sys.path.append(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules")
import pyautogui # need pyautogui to show the label for dependecy reason, but for pyrevit might just import from site package
from PIL import Image as pim

def try_catch_error(func):
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:
            print (e)
    return wrapper



class EnneaDuck:
    @try_catch_error
    def __init__(self):
        self.x = 500
        self.y = 1000
        self.cycle = 0
        self.current_event_number = 1
        self.current_event = "idle"
        self.next_event_number = random.randrange(1, 3, 1)
        self.next_event = "idle"
        self.last_click_x = 0
        self.last_click_y = 0

        self.impath = "{}\img_assets\\".format(os.path.dirname(os.path.realpath(__file__)))

        self.window = tk.Tk()
        self.window.geometry("100x100+300+300")
        self.window.config(highlightbackground='green')

        self.window.overrideredirect(True)
        self.window.wm_attributes('-transparentcolor', 'green')
        self.window.wm_attributes('-topmost', True)

        self.window.bind('<Button-1>', self.save_last_click_pos)
        self.window.bind('<B1-Motion>', self.dragging)
        """https://www.geeksforgeeks.org/right-click-menu-using-tkinter/
        see above helper doc for making a right click menu pop."""

        self.duck_label = tk.Label(self.window, bd=0, bg='green')
        self.duck_label.pack()
        self.create_popup_menu()
        self.duck_label.bind("<Button-3>", self.do_popup)

        self.talk_bubble = tk.Label(self.window,text = "123")
        self.talk_bubble.pack()



        self.stage_list =  ["idle","rotate","swing","attention","walking_left","walking_right"]
        for stage in self.stage_list:
            gif_path = "{}{}.gif".format(self.impath, stage)
            frame_count = self.count_frames_in_gif(gif_path)
            frames = [tk.PhotoImage(file=gif_path, format='gif -index %i' % (i)) for i in range(frame_count)]
            # print (stage)
            # print (frames)
            setattr(self, stage, frames)########## change this to (frame_count, frames) then when loading, it know the span


        self.next_event_mapping = {
            "idle_event": ["idle_event"]*3 + ["rotate_event"] + ["walk_left_event"] + ["walk_right_event"] + ["swing_event"]*3,
            "rotate_event": ["idle_event"]*3 + ["rotate_event"]*0 + ["walk_left_event"]*2 + ["walk_right_event"] + ["swing_event"]*3,
            "walk_left_event": ["idle_event"]*0 + ["rotate_event"]*2+ ["walk_left_event"]*0 + ["walk_right_event"] + ["swing_event"]*3,
            "walk_right_event": ["idle_event"]*3 + ["rotate_event"]*2 + ["walk_left_event"] + ["walk_right_event"] + ["swing_event"]*3,
            "swing_event": ["idle_event"]*3 + ["rotate_event"]*2 + ["walk_left_event"] + ["walk_right_event"] + ["swing_event"]*3,       
            "attention_event": ["idle_event"]*0 + ["rotate_event"]*0 + ["walk_left_event"]*3 + ["walk_right_event"]*3 + ["swing_event"]*0 + ["attention_event"]*2
        
        }
        

        self.window.after(1, self.update)

    @try_catch_error
    def run(self):

        self.window.mainloop()


    def save_last_click_pos(self, event):
        self.last_click_x = event.x
        self.last_click_y = event.y


    def dragging(self, event):
        x, y = event.x - self.last_click_x + self.window.winfo_x(), event.y - self.last_click_y + self.window.winfo_y()
        self.window.geometry("+%s+%s" % (x, y))
        self.x, self.y = x,y

    def create_popup_menu(self):
        self.popup_menu = tk.Menu(self.window, tearoff=0)
        self.popup_menu.add_command(label="Hello.", command=self.say_hello)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Kill Me.", command=self.window.destroy)

    def say_hello(self):
        print("Hello!")
        self.talk_bubble.configure(text = "He-Quack-llo!")


    def do_popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print (e)
        finally:
            self.popup_menu.grab_release()

    @try_catch_error
    def gif_work(self, frames):
        if self.cycle < len(frames) - 1:
            self.cycle += 1
        else:
            self.cycle = 0
            possible_next_events = self.next_event_mapping["{}_event".format(self.current_event)] 
            next_event_number = random.randrange(0, len(possible_next_events) + 1, 1)
            self.next_event = possible_next_events[next_event_number]

     
    @try_catch_error
    def update(self):

        frames = getattr(self, self.current_event)

        if frames:
            self.gif_work(frames)
            
        self.window.geometry('100x100+' + str(self.x) + str(self.y))
        print ("current cycle = {}, current frame = {}".format(self.cycle, self.current_event))
        self.duck_label.configure(image=frames[self.cycle])
        
        self.window.after(1, self.duck_event_update)
        if time.time() - self._last_check_time > 10:
            self._last_check_time = time.time()
            if self.is_my_turn():
                self.current_event = "attention"
                self.window.after(1, self.update)
                


    def duck_event_update(self):
        if self.cycle != 0:
            return
        
        self.current_event = self.next_event
        self.window.after(1, self.update)
        return


    def count_frames_in_gif(self, file_path):
        frame_count = 0
        try:
            with pim.open(file_path) as img:
                while True:
                    frame_count += 1
                    try:
                        img.seek(frame_count)
                    except EOFError:
                        break
        except FileNotFoundError:
            print("The file {} could not be found.".format(file_path))
        return frame_count




    def is_my_turn(self):
        return
        current_open_docs = []# lookup the last sync monitor file
        
        queue_files = [get_file(x) for x in current_open_docs]
        for file in queue_files:
            queue = open(file)
            if len(queue) == 0:
                continue
            if EnneadTab.USER.user_name == queue[0]:
                self._queue_file = file.title
                return True
            
        return False


def main():
    app = EnneaDuck()
    app.run()

###############################################
if __name__ == "__main__":
    main()
