import sys
import os
import random
import tkinter as tk

sys.path.append(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules")
import pyautogui # need pyautogui to show the label for dependecy reason, but for pyrevit might just import from site package
from PIL import Image as pim



root_folder = os.path.abspath(os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(root_folder)
#print (root_folder)
import FOLDER
import USER
import DATA_FILE
import ERROR_HANDLE

EXE_NAME = u"EnneaDuck"

def try_catch_error(func):
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:
            pass
            #print (e)
    return wrapper



class EnneaDuck:
    @try_catch_error
    def __init__(self):
        self.x = 900
        self.y = 1000
        self.last_click_x = 0
        self.last_click_y = 0
        self.window_width = 600
        self.window_height = 250
        self.FPS = 12
        self.animation_wait_time = int(1000 / self.FPS)
        self.bubble_life = 0
        self.last_time_check = 0
        self.user_name = USER.get_user_name()
        self.autodesk_user_name = USER.get_autodesk_user_name()

        self.image_path = "{}\img_assets\\".format(os.path.dirname(os.path.abspath(__file__)))
        #print (self.image_path)

        self.window = tk.Tk()
        self.window.title(EXE_NAME)

        # 100x100 size window, location 700, 500. No space between + and numbers
        self.window.geometry("{}x{}+{}+{}".format(self.window_width,\
                                                    self.window_height,\
                                                    self.x,\
                                                    self.y))
        # add green screen
        #self.window.config(highlightbackground = "green")
        self.window.config(background = "green")

        self.window.overrideredirect(True)
        # self.window.attributes('-alpha',0)
        self.window.wm_attributes('-transparentcolor', 'green')
        self.window.wm_attributes('-topmost', True)

        self.window.bind('<Button-1>', self.save_last_click_pos)
        self.window.bind('<B1-Motion>', self.dragging)
        """https://www.geeksforgeeks.org/right-click-menu-using-tkinter/
        see above helper doc for making a right click menu pop."""

        self.create_popup_menu()

        self.talk_bubble = tk.Label(self.window,text = "talk bubble text", font=("Comic Sans MS", 18), borderwidth = 3, relief = "solid")
        # pady ====> pad in Y direction
        self.talk_bubble.pack(pady = 15)
        #self.talk_bubble.bind("<Button-3>", self.do_popup)
        self.hide_widget(self.talk_bubble)


        self.duck_label = tk.Label(self.window,  bd=0, bg='green')
        self.duck_label.pack(pady = 15)
        self.duck_label.bind("<Button-3>", self.do_popup)

        self.stage_list =  ["idle",\
                            "rotate",\
                            "swing",\
                            "attention",\
                            "walking_left",\
                            "walking_right"]
        for stage in self.stage_list:
            gif_path = "{}{}.gif".format(self.image_path, stage)
            frame_count = self.count_frames_in_gif(gif_path)
            frames = [tk.PhotoImage(file = gif_path, format = 'gif -index %i' % (i)) for i in range(frame_count)]

            # bind the event name to the list of frames
            setattr(self, stage, frames)

        # this is the map to determine what event will queue after
            # follow the current event. But before the queued event is
            # happening. can run other checks such as sync turn check
            # if True, then the next queeded event will be overriden.
        self.next_event_mapping = {
            "idle": ["idle"]*15 + ["rotate"] + ["walking_left"] + ["walking_right"] + ["swing"]*3,
            "rotate": ["idle"]*3 + ["rotate"]*0 + ["walking_left"]*2 + ["walking_right"] + ["swing"]*3,
            "walking_left": ["idle"]*0 + ["rotate"]*2+ ["walking_left"]*0 + ["walking_right"] + ["swing"]*3,
            "walking_right": ["idle"]*10 + ["rotate"]*2 + ["walking_left"] + ["walking_right"] + ["swing"]*3,
            "swing": ["idle"]*10 + ["rotate"]*2 + ["walking_left"] + ["walking_right"] + ["swing"]*10,
            "attention": ["idle"]*0 + ["rotate"]*10 + ["walking_left"]*10 + ["walking_right"]*10 + ["swing"]*2 + ["attention"]*8

        }

        # prepare the initialization of frame index and frames
        self.cycle_animation_frame_index = 0
        self.current_event = "idle"
        self.reset_animation_data()





        self.window.after(1, self.update_animation)


    def reset_animation_data(self):
        self.frames = getattr(self, self.current_event)
        self.current_event_length = len(self.frames)

    def update_animation(self):


        if self.cycle_animation_frame_index < self.current_event_length - 1:
            self.cycle_animation_frame_index += 1

            if self.current_event == "walking_left":
                self.x -= 3
            if self.current_event == "walking_right":
                self.x += 3

        else:
            self.cycle_animation_frame_index = 0
            possible_next_events = self.next_event_mapping[self.current_event]
            # print (possible_next_events)
            random_index = random.randrange(0, len(possible_next_events) , 1)
            # print (random_index)
            self.current_event = possible_next_events[random_index]
            self.frames = getattr(self, self.current_event)
            self.current_event_length = len(self.frames)

        self.window.geometry('{}x{}+{}+{}'.format(self.window_width, self.window_height, self.x, self.y))
        #print ("current cycle = {}, current event = {}".format(self.cycle_animation_frame_index, self.current_event))
        self.duck_label.configure(image=self.frames[self.cycle_animation_frame_index])

        # here do not wait animation gap time because i want to check immediately
        self.window.after(1, self.check_other_event)



    def check_other_event(self):
        # check for sync queue status, when cycle is at 0, then can override current event for attention stage

        if self.cycle_animation_frame_index == 0 and self.last_time_check == 0:
            # boost up to 200 frame, within this 100 frames there will be not more checking
            self.last_time_check = 200

            is_my_turn, docs, records = self.is_sync_queue_turn()
            #print (is_my_turn, docs, records)
            if is_my_turn:
                self.say_hello(text = "{}\nis your turn to sync.".format(docs.lstrip("\n")))
                self.current_event = "attention"
                self.reset_animation_data()
            pass

        if self.bubble_life > 0:
            self.bubble_life -= 1
        if self.bubble_life == 0:
            self.hide_widget(self.talk_bubble)

        # lower check time toward 0
        if self.last_time_check > 0:
            self.last_time_check -= 1



        # if there is nothing elese to do, call update_animation again.
        #  ONLY here use animation gap time
        self.window.after(self.animation_wait_time, self.update_animation)


    def is_sync_queue_turn(self):

        docs = ""
        records = ""
        is_my_turn = False
        # find all the queue file that has the user name
        folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Sync_Queue"

        monitor_file = FOLDER.get_EA_dump_folder_file("EA_Last_Sync_Record.json")
        if not FOLDER.is_path_exist(monitor_file):
            return False, docs, records

        data = DATA_FILE.read_json_file_safely(monitor_file)

        for doc in data.keys():
            filepath = "{}\Sync Queue_{}.queue".format(folder,doc)
            if not FOLDER.is_path_exist(filepath):
                continue
            #print (filepath)

            # in py3, map return a map object instead of a list. To read the content, use list to convert.
            content = list(DATA_FILE.read_txt_file_safely(filepath))

            #print (content)

            for i,line_record in enumerate(content):
                if self.autodesk_user_name in line_record:
                    records += "\n{}\n{}".format(docs, content)
                    docs += "\n{}".format(doc)
                    if i == 0:
                        is_my_turn = True
                        #print (9999999999999999999999)
                    break

                # if user name is first, override event to be attention, and pop the bubble.

        return is_my_turn, docs, records


    def create_popup_menu(self):
        self.popup_menu = tk.Menu(self.window, tearoff=0)
        self.popup_menu.add_command(label="Hello.", command=self.say_hello)
        self.popup_menu.add_command(label="Show queue.", command=self.show_queue)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Kill Me.", command=self.window.destroy)


    def is_hate_talking_duck(self):
        return DATA_FILE.get_revit_ui_setting_data(key_defaule_value = ("checkbox_is_dumb_duck", False))


    def say_hello(self, text = "Quack-Quack!!"):
        #print("Hello!")
        if self.is_hate_talking_duck():
            return
        self.talk_bubble.configure(text = text)
        self.bubble_life = 15 * self.FPS
        self.hide_widget(self.duck_label)
        self.show_widget(self.talk_bubble)
        self.show_widget(self.duck_label)

    def show_queue(self):
        #print("Hello!")
        is_my_turn, docs, records = self.is_sync_queue_turn()
        if len(records.strip("\n")) == 0:
            text = "No queue to show."
        else:
            text = records.lstrip("\n")
        self.talk_bubble.configure(text = text)
        self.bubble_life = 30 * self.FPS
        self.hide_widget(self.duck_label)
        self.show_widget(self.talk_bubble)
        self.show_widget(self.duck_label)

    def show_widget(self, item):
        item.pack()
    def hide_widget(self, item):
        item.pack_forget()


    def do_popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            pass
            #print (e)
        finally:
            self.popup_menu.grab_release()

    def save_last_click_pos(self, event):
        self.last_click_x = event.x
        self.last_click_y = event.y


    def dragging(self, event):
        x, y = event.x - self.last_click_x + self.window.winfo_x(), event.y - self.last_click_y + self.window.winfo_y()
        self.window.geometry("+%s+%s" % (x, y))
        self.x, self.y = x,y

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
            pass
            #print("The file {} could not be found.".format(file_path))
        return frame_count


    def run(self):
        self.window.mainloop()


def is_another_duck_running():

    #print [x.title for x in pyautogui.getAllWindows()]
    for window in pyautogui.getAllWindows():
        #print window.title
        if window.title == EXE_NAME:
            return True
    return False


@ERROR_HANDLE.try_catch_error
def main():
    if is_another_duck_running():
        return
    app = EnneaDuck()
    app.run()

###############################################
if __name__ == "__main__":
    main()



# allow duck to not given warning at all