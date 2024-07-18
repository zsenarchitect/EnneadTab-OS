#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
sys.path.append(r'L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version\ENNEAD.extension\lib')

from EnneadTab import DATA_FILE, NOTIFICATION, SPEAK, ERROR_HANDLE, FOLDER
import pygame
import pyautogui
import random
import traceback
import os
import button
import math
import sys
import time
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
import EA_TOASTER
import json

"""
def is_hate_toast():
    dump_folder = EA_UTILITY.get_EA_local_dump_folder()
    file_name = "EA_TOASTER_KILL.kill"
    return EA_UTILITY.is_file_exist_in_folder(file_name, dump_folder)
"""


def rotate_img_around_center(image, rect, angle):
    """Rotate the image while keeping its center."""
    # Rotate the original image without modifying it.
    new_image = pygame.transform.rotate(image, angle)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect


def get_pointer_angle(pt_x, pt_y):
    """get the angle of a line[current mouse position to a given pt] to X axis"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_x == pt_x:
      return 90 + 180 * (mouse_y > pt_y)
    angle = math.atan(-float(mouse_y - pt_y) / float(mouse_x - pt_x))* 180 / math.pi
    angle += 180 * (mouse_x < pt_x)# force extra rotate
    return angle

def is_another_LAST_SYNC_MONITOR_running():

    #print [x.title for x in pyautogui.getAllWindows()]
    for window in pyautogui.getAllWindows():
        #print window.title
        if window.title == u"EnneadTab Revit Last Sync Lookup":
            return True
    return False


def get_wait_time():
    return int(DATA_FILE.get_revit_ui_setting_data(("textbox_sync_monitor_interval", 45))) 

    """
    file_name = 'revit_ui_setting.json'
    if not FOLDER.is_file_exist_in_dump_folder(file_name):
        return 45


    setting_file = FOLDER.get_EA_dump_folder_file(file_name)
    data = DATA_FILE.read_json_as_dict(setting_file)
    return  int(data.get("textbox_sync_monitor_interval", 45))
    """

    
@ERROR_HANDLE.try_catch_error_silently
def main():
    if is_another_LAST_SYNC_MONITOR_running():
        #speak("there is another 'EnneadTab Talkie' opened. Now quiting")
        return



    #script_dir = os.path.abspath( os.path.dirname( __file__ ) )
    #print "A GUI designed by Sen Zhang for Ennead Architect."
    # print ("%%%%%%%%%%%%%%%%%%%%%")
    # print (script_dir)
    pygame.init()


    #create game window
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 850

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    #pygame.display.iconify()

    pygame.display.set_caption("EnneadTab Revit Last Sync Lookup")

    #game variables
    game_paused = False
    menu_state = "main"

    #define fonts
    # font_OLD = pygame.font.SysFont("arialblack", 20)
    font_title = pygame.font.SysFont("arialblack", 30)
    font_subtitle = pygame.font.SysFont("arialblack", 20)
    font_body = pygame.font.SysFont("arial", 15)
    font_note = pygame.font.SysFont("arialblack", 10)

    #define colours
    TEXT_COL = (255, 255, 255)
    TEXT_COL_FADE = (150, 150, 150)
    TEXT_COL_WARNING = (252, 127, 3)
    TEXT_COL_BIG_WARNING = (242, 52, 39)

    # logo
    #exe_folder = os.path.abspath( os.path.dirname( __file__ ) )


    #exe_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\SEARCH_EDIT_REQUEST"
    #print exe_folder
    #EA_logo = pygame.image.load("{}\images\\Ennead_Architects_Logo.png".format(exe_folder)).convert_alpha()
    content_folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton"
    EA_logo = pygame.image.load("{}\\images\\Ennead_Architects_Logo.png".format(content_folder)).convert_alpha()
    target_img_size = (100, 100)
    EA_logo = pygame.transform.scale(EA_logo, target_img_size)
    original_logo = EA_logo
    logo_rect = EA_logo.get_rect(center=(100, SCREEN_HEIGHT - 100))
    angle = 0




    # Clock
    clock = pygame.time.Clock()
    FPS = 20

    #load button images

    #quit_img = pygame.image.load("{}\images\\button_quit.png".format(exe_folder)).convert_alpha()
    quit_img = pygame.image.load("{}\\images\\button_quit.png".format(content_folder)).convert_alpha()

    #create button instances

    quit_button = button.Button(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 150, quit_img, 1)

    wait_time = get_wait_time()

    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))


    def unpack_record():
        dump_folder = FOLDER.get_EA_local_dump_folder()

        records = [file_name for file_name in os.listdir(dump_folder) if "last_sync" in file_name.lower()]
        if len(records) == 0:
            return None

        # add this try catch in case reading file when json file is updating
        try:
            record = DATA_FILE.read_json_as_dict("{}\{}".format(dump_folder, records[0]))
            return record
        except:
            return None

        """
        records = [ EA_UTILITY.read_json_as_dict("{}\{}".format(dump_folder, file_name)) for file_name in records]
        return records
        """


    def format_seconds(time_stamp):
        text_min = int(math.floor(time_stamp / 60))
        text_secs = int(time_stamp % 60)
        return "{}m {}s".format(text_min, text_secs)

    def display_record(records):
        now = time.time()
        records = sorted(records.items(), key = lambda x: now - x[1])
        pointer_H = 150

        check_interval = wait_time # in minutes
        yell_interval = int(wait_time * 1.5) # in minutes
        draw_text("Time Since Sync (Sync interval every {} mins*):".format(check_interval), font_subtitle, TEXT_COL, 50, pointer_H)
        pointer_H += 25
        draw_text("{} mins after timer begins, it will become orange.".format(check_interval), font_subtitle, TEXT_COL, 50, pointer_H)
        pointer_H += 25
        draw_text("{} mins after timer begins, it will become red and try to talk**".format(yell_interval), font_subtitle, TEXT_COL, 50, pointer_H)
        pointer_H += 25
        draw_text("Every minutes after {} mins will cost {} coins.".format(yell_interval, 2), font_subtitle, TEXT_COL, 50, pointer_H)
        pointer_H += 25
        draw_text("Methods to avoid paying coins:", font_subtitle, TEXT_COL_FADE, 50, pointer_H)
        pointer_H += 25
        draw_text("- Closing file without sync, even when running overtime.", font_subtitle, TEXT_COL_FADE, 50, pointer_H)
        pointer_H += 20
        draw_text("- Saving file locally will reset timer.", font_subtitle, TEXT_COL_FADE, 50, pointer_H)
        pointer_H += 20
        draw_text("- No changes made into the file since last sync.", font_subtitle, TEXT_COL_FADE, 50, pointer_H)
        pointer_H += 20
        draw_text("- Mannually kill a monitor progress from EnneadTab.", font_subtitle, TEXT_COL_FADE, 50, pointer_H)
        pointer_H += 40
        draw_text("Footnote *: This interval can be set in your EnneadTab setting.", font_body, TEXT_COL_FADE, 50, pointer_H)
        pointer_H += 20
        draw_text("Footnote**: Unless you have killed the talkie lady:)", font_body, TEXT_COL_FADE, 50, pointer_H)
        pointer_H += 35
        frame_upper_left_H = pointer_H
        bad_docs = ""
        for key, value in record.items():
            text = "{} >>> {}".format(key, format_seconds(now - value))
            if now - value > check_interval * 60:
                #found_bad_condition = True
                draw_text(text, font_body, TEXT_COL_WARNING, 50, pointer_H)
                if now - value > yell_interval * 60:
                    draw_text(text, font_body, TEXT_COL_BIG_WARNING, 50, pointer_H)
                    if len(bad_docs) == 0:
                        bad_docs += "{}".format(key)
                    else:
                        bad_docs += ", and {}".format(key)

                    if int(now -value)%(60*5)==0:
                        SPEAK.speak("Document {} has not been synced for too long.".format(key))
                        NOTIFICATION.toast(main_text = "Document {} has not been synced for too long.".format(key), importance_level = 0)
            else:
                draw_text(text, font_body, TEXT_COL, 50, pointer_H)
            pointer_H += 20


        pygame.draw.rect(screen, TEXT_COL, pygame.Rect(40, frame_upper_left_H - 5, SCREEN_WIDTH - 100, pointer_H - frame_upper_left_H + 15), width = 2, border_radius = 12)
        return bad_docs




    #game loop
    run = True

    life_max =  12 * 60 * 60 * FPS
    life_count = life_max


    while run:


        screen.fill((52, 78, 91))
        #screen.fill((75, 99, 65))
        


        angle = get_pointer_angle(*logo_rect.center)# this is to keep it facing mouse
        EA_logo, logo_rect = rotate_img_around_center(original_logo, logo_rect, angle)
        screen.blit(EA_logo, logo_rect)

        #check if game is paused
        H = 50
        draw_text("EnneadTab Revit Last Sync Monitor. ", font_title, TEXT_COL, 50, H)
        H += 40
        # draw_text("Keep this window alive. ", font_title, TEXT_COL_FADE, 50, 100)
        # draw_text("Do not close after every popup.", font_title, TEXT_COL_FADE, 50, 130)
        # draw_text("Minimize it is ok though.", font_title, TEXT_COL_FADE, 50, 160)

        # draw_text("Every initiation takes a few seconds, so let's", font, TEXT_COL_FADE, 50, 210)
        # draw_text("initiate as few times as possible.", font, TEXT_COL_FADE, 50, 240)


        record = unpack_record()
        if record:
            bad_docs = display_record(record)
            if len(bad_docs) > 0 and life_count % (FPS * 60 * 30) == 0:
                pass

                #resume alert later
                """
                SPEAK.speak("Document {} has not been synced for too long.".format(bad_docs))
                if not is_hate_toast():
                    EA_TOASTER.toast(message = bad_docs, title = "You have documents not synced in a while.", app_name = "EnneadTab Monitor", icon = None, click = None, actions = None)
                """


        if quit_button.draw(screen):
            run = False

        if life_count < 0:
            run = False
        text_life = int(life_count / FPS)
        text_hours = str(text_life//3600)
        text_min = str((text_life%3600)//60)
        text_secs = str((text_life%3600)%60)
        draw_text("To save memory, EnneadTab Last Sync Monitor will close itself in {}h {}m {}s, AKA end of the day.".format(text_hours, text_min, text_secs), font_note, TEXT_COL, 50, SCREEN_HEIGHT - 20)
        life_count -= 1




        #event handler
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = True
            if event.type == pygame.QUIT:
                run = False

        clock.tick(FPS)
        pygame.display.update()

    pygame.quit()






if __name__ == "__main__":
    main()
