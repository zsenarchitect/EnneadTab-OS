#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import traceback
import os

import math
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util
import _GUI_Util
import pygame

TITLE = u"EnneadTab Revit Last Sync Monitor."




    
class LastSyncMonitor(_GUI_Util.BasePyGameGUI):
    def __init__(self):

        self.app_title = TITLE
        self.SCREEN_WIDTH = 900
        self.SCREEN_HEIGHT = 900
        self.content_folder = os.path.dirname(__file__)

        self.wait_time = int(_Exe_Util.get_setting("textbox_sync_monitor_interval", 45))
    
        
        self.life_max = 12 * 60 * 60 * 20
        self.life_count = self.life_max

        self.taskbar_icon = "{}\\images\\icon.png".format(self.content_folder)
        



        self.setup_GUI()


    def display_record(self):
        record = _Exe_Util.read_json_as_dict_in_dump_folder("Last_Sync_Record.sexyDuck")
           
        now = time.time()
        records = sorted(record.items(), key=lambda x: now - x[1])
        self.POINTER_Y = 150
        check_interval = self.wait_time
        yell_interval = int(self.wait_time * 1.5)

        self.draw_text("Time Since Sync (Sync interval every {} mins*):".format(check_interval), self.FONT_SUBTITLE, self.TEXT_COLOR)
        self.draw_text("{} mins after timer begins, it will become orange.".format(check_interval), self.FONT_SUBTITLE, self.TEXT_COLOR)  
        self.draw_text("{} mins after timer begins, it will become red and try to talk**".format(yell_interval), self.FONT_SUBTITLE, self.TEXT_COLOR)
        self.draw_text("Every minutes after {} mins will cost {} coins.".format(yell_interval, 2), self.FONT_SUBTITLE, self.TEXT_COLOR)
        self.draw_text("Methods to avoid paying coins:", self.FONT_SUBTITLE, self.TEXT_COLOR_FADE)
        self.draw_text("- Closing file without sync, even when running overtime.", self.FONT_SUBTITLE, self.TEXT_COLOR_FADE)
        self.draw_text("- Saving file locally will reset timer.", self.FONT_SUBTITLE, self.TEXT_COLOR_FADE)
        self.draw_text("- No changes made into the file since last sync.", self.FONT_SUBTITLE, self.TEXT_COLOR_FADE)
        self.draw_text("- Manually kill a monitor progress from EnneadTab.", self.FONT_SUBTITLE, self.TEXT_COLOR_FADE)
        self.draw_text("Footnote *: This interval can be set in your EnneadTab setting.", self.FONT_BODY, self.TEXT_COLOR_FADE)
        self.draw_text("Footnote**: Unless you have killed the talkie lady:)", self.FONT_BODY, self.TEXT_COLOR_FADE)
        self.POINTER_Y += 20
        frame_upper_left_H = self.POINTER_Y
        bad_docs = ""

        for key, value in records:
            text = "{} >>> {}".format(key, self.format_seconds(now - value))
            if now - value > check_interval * 60:
                self.draw_text(text, self.FONT_BODY, self.TEXT_COLOR_WARNING)
            elif now - value > yell_interval * 60:
                self.draw_text(text, self.FONT_BODY, self.TEXT_COLOR_BIG_WARNING)
                if len(bad_docs) == 0:
                    bad_docs += "{}".format(key)
                else:
                    bad_docs += ", and {}".format(key)

                if int(now - value) % (60 * 5) == 0:
                    pass

            else:
                self.draw_text(text, self.FONT_BODY, self.TEXT_COLOR)


        # draw soft corner box
        pygame.draw.rect(self.screen, 
                         self.TEXT_COLOR, 
                         pygame.Rect(40, 
                                    frame_upper_left_H - 5, 
                                    self.SCREEN_WIDTH - 100, 
                                    self.POINTER_Y - frame_upper_left_H + 15), 
                         width=2, 
                         border_radius=12)

        
        if len(bad_docs) > 0 and self.life_count % (self.FPS * 60 * 30) == 0:
            pass
            # SPEAK.speak("Document {} has not been synced for too long.".format(bad_docs))
            # if not is_hate_toast():
            #     EA_TOASTER.toast(message=bad_docs, title="You have documents not synced in a while.", app_name="EnneadTab Monitor", icon=None, click=None, actions=None)

    @_Exe_Util.try_catch_error
    def main(self):

        while self.run:
            self.reset_pointer()# move pointer to initial position
            self.screen.fill(self.BACKGROUND_COLOR)# fill background color before drawing anything elese
            
            self.update_logo_angle()# update animated logo
            self.update_title()
            self.update_footnote()


            
            self.display_record()# main function of this app
            

            self.check_exit()

            # refresh all drawing by order
            self.clock.tick(self.FPS)
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    LastSyncMonitor().main()

