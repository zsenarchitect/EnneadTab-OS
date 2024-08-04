
#!/usr/bin/python
# -*- coding: utf-8 -*-


import shutil
import os
import pyautogui
import sys
import datetime
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util
import _GUI_Util
import pygame

TITLE = u"EnneadTab Revit Schedule Opener."
DATA_FILE = "schedule_opener_data.sexyDuck"

def is_there_cancel_button(cancel_button_icon_file):
    try:
        #cancel_button_icon = pyautogui.locateOnScreen(cancel_button_icon_file, confidence = 0.8)
        cancel_button_icon = pyautogui.locateOnScreen(cancel_button_icon_file)
        #print cancel_button_icon
        if not cancel_button_icon:
            return False

        pyautogui.click(pyautogui.center(cancel_button_icon))
        print ("click button")
        return True

    except Exception as e:
        #print (e.message)
        return False






def start_revit(revit_version):
    revit_path = "C:\\Program Files\\Autodesk\\Revit {}\\Revit.exe".format(revit_version)
    subprocess.Popen(revit_path)


    
class ScheduleOpener(_GUI_Util.BasePyGameGUI):
    def __init__(self):

        self.app_title = TITLE
        self.SCREEN_WIDTH = 700
        self.SCREEN_HEIGHT = 500
        self.content_folder = os.path.dirname(__file__)

        self.life_max = _GUI_Util.BasePyGameGUI.MAX_LIFE
        self.life_count = self.life_max

        self.taskbar_icon = "{}\\images\\icon.png".format(self.content_folder)
        self.cancel_button_icon_file = "{}\\images\\icon_lookup.png".format(self.content_folder)

    

        self.setup_GUI()


    

    def display_data(self, data):
        # Set your specific date and time for the task to run
        # For example: Aug 24, 2023 at 2:30 PM
        self.POINTER_Y = 150

        self.draw_text("Below are docs that will be opened:", self.FONT_SUBTITLE, self.TEXT_COLOR_FADE)
        if not data:# no data
            self.run = False
            return False
        target_time = data["open_time"]
        # print(target_time)
        #  use re to convert isoformat to datetime without using strptime
        # datetime.datetime
        try:
            # this is for 2mins version where it has .000s
            target_time = datetime.datetime.strptime(target_time, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            # this is for the whole clock time
            target_time = datetime.datetime.strptime(target_time, "%Y-%m-%dT%H:%M:%S")
            
            
        self.draw_text("Time Till Scheduled Open Time: {}".format( target_time - datetime.datetime.now()), self.FONT_BODY, self.TEXT_COLOR_FADE)
        for i, doc in enumerate(data["docs"]):
            self.draw_text("    [{}]".format( doc), self.FONT_BODY, self.TEXT_COLOR_WARNING)
        
        
        if datetime.datetime.now() > target_time:
            revit_version = data['revit_version']
            start_revit(revit_version)
            data_file = _Exe_Util.get_file_in_dump_folder(DATA_FILE)
            marker_file = os.path.dirname(data_file) + "\\action_" + DATA_FILE
            shutil.copyfile(data_file, marker_file)
            os.remove(data_file)
            return True

        

    @_Exe_Util.try_catch_error
    def main(self):

        while self.run:
            self.reset_pointer()# move pointer to initial position
            self.screen.fill(self.BACKGROUND_COLOR)# fill background color before drawing anything elese
            
            self.update_logo_angle()# update animated logo
            self.update_title()
            self.update_footnote()


            
            data = _Exe_Util.get_data(DATA_FILE)
            res = self.display_data(data)
            if res:
                data = None#clear data to prevent repeat open revit
            
            self.check_exit()

            # refresh all drawing by order
            self.clock.tick(self.FPS)
            pygame.display.update()

        pygame.quit()



if __name__ == "__main__":
    monitor = ScheduleOpener()
    monitor.main()