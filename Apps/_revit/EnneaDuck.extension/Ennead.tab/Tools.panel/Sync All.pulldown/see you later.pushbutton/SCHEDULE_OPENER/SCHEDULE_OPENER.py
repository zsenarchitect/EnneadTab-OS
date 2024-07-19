#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
sys.path.append(r'L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib')

from EnneadTab import EXE, DATA_FILE, FOLDER
import pygame
import pyautogui
import random
import traceback
import os
import button
import math
import sys
import datetime
import subprocess

sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')


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

def is_another_schedule_opener_running():

    #print [x.title for x in pyautogui.getAllWindows()]
    for window in pyautogui.getAllWindows():
        #print window.title
        if window.title == u"EnneadTab Revit Schedule Openner":
            return True
    return False






def main():
    if is_another_schedule_opener_running():
        #speak("there is another 'EnneadTab Talkie' opened. Now quiting")
        return



    #script_dir = os.path.abspath( os.path.dirname( __file__ ) )
    #print "A GUI designed by Sen Zhang for Ennead Architect."
    # print ("%%%%%%%%%%%%%%%%%%%%%")
    # print (script_dir)
    pygame.init()


    #create game window
    SCREEN_WIDTH = 700
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.iconify()

    pygame.display.set_caption("EnneadTab Revit Schedule Openner")

    #game variables
    game_paused = False
    menu_state = "main"

    #define fonts
    font = pygame.font.SysFont("arialblack", 20)
    font_title = pygame.font.SysFont("arialblack", 30)
    font_note = pygame.font.SysFont("arialblack", 10)

    #define colours
    TEXT_COL = (255, 255, 255)
    TEXT_COL_HIGHTLIGHT = (209, 187, 119)
    TEXT_COL_FADE = (150, 150, 150)

    # logo
    #exe_folder = os.path.abspath( os.path.dirname( __file__ ) )
    exe_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\SCHEDULE_OPENER"
    print (exe_folder)
    EA_logo = pygame.image.load("{}\images\\Ennead_Architects_Logo.png".format(exe_folder)).convert_alpha()
    target_img_size = (100, 100)
    EA_logo = pygame.transform.scale(EA_logo, target_img_size)
    original_logo = EA_logo
    logo_rect = EA_logo.get_rect(center=(100, SCREEN_HEIGHT - 100))
    angle = 0


    cancel_button_icon_file = "{}\\images\\icon_lookup.png".format(exe_folder)


    # Clock
    clock = pygame.time.Clock()
    FPS = 30

    #load button images

    quit_img = pygame.image.load("{}\images\\button_quit.png".format(exe_folder)).convert_alpha()

    #create button instances

    quit_button = button.Button(SCREEN_WIDTH/2 + 120, SCREEN_HEIGHT - 120, quit_img, 1)

    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))
        
    

    def display_data(data):
        # Set your specific date and time for the task to run
        # For example: Aug 24, 2023 at 2:30 PM
        

        
        
        draw_text("Below are docs that will be opened:", font_title, TEXT_COL_FADE, 50, 120)

        target_time = data["open_time"]
        print(target_time)
        #  use re to convert isoformat to datetime without using strptime
        # datetime.datetime
        try:
            # this is for 2mins version where it has .000s
            target_time = datetime.datetime.strptime(target_time, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            # this is for the whole clock time
            target_time = datetime.datetime.strptime(target_time, "%Y-%m-%dT%H:%M:%S")
            
            
        draw_text("Time Till Scheduled Open Time: {}".format( target_time - datetime.datetime.now()), font, TEXT_COL_FADE, 50, 150)
        for i, doc in enumerate(data["docs"]):
            draw_text("    [{}]".format( doc), font, TEXT_COL_FADE, 50, 190 + i *30)
        
        
        if datetime.datetime.now() > target_time:
            revit_version = data['revit_version']
            start_revit(revit_version)
            FOLDER.copy_file_to_local_dump_folder(FOLDER.get_EA_dump_folder_file(data_file), file_name = "action_" + data_file )
            FOLDER.remove_file_from_dump_folder(data_file)
            return True

        
        
        
        







    #game loop
    run = True

    life_max =  4*24*60 * 60 * FPS
    life_count = life_max

    count_down_found = -1
    data = None
    while run:



        screen.fill((52, 78, 91))


        angle = get_pointer_angle(*logo_rect.center)# this is to keep it facing mouse
        EA_logo, logo_rect = rotate_img_around_center(original_logo, logo_rect, angle)
        screen.blit(EA_logo, logo_rect)

        #check if game is paused
        draw_text("EnneadTab Revit Schedule Openner. ", font, TEXT_COL, 50, 30)
        draw_text("Keep this window alive. ", font_title, TEXT_COL_FADE, 50, 80)
        
         
        if life_count % (1 * FPS) == 0:
            data_file = "EA_SCHEDULE_OPENER.sexyDuck"
            data = DATA_FILE.get_data(data_file)
        if data:
            res = display_data(data)
            if res:
                data = None#clear data to prevent repeat open revit
            
            
 





        if quit_button.draw(screen):
            run = False

        if life_count < 0:
            run = False
        text_life = int(life_count / FPS)
        text_min = int(math.floor(text_life / 60))
        text_secs = text_life % 60
        draw_text("To save memory, EnneadTab Schedule Openner will close itself in {}m {}s if there is nothing to monitor.".format(text_min, text_secs), font_note, TEXT_COL, 50, SCREEN_HEIGHT - 20)
        life_count -= 1
        draw_text(str(count_down_found), font_note, TEXT_COL, 50, SCREEN_HEIGHT - 30)



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

def start_revit(revit_version):

    revit_path = "C:\\Program Files\\Autodesk\\Revit {}\\Revit.exe".format(revit_version)


    subprocess.Popen(revit_path)



if __name__ == "__main__":
    try:

     main()

    except:
        error = traceback.format_exc()
        print (error)
        exe_folder = os.path.abspath( os.path.dirname( __file__ ) )
        with open(r"{}\error_log.txt".format(exe_folder), "w") as f:
            f.write(error)
            EXE.try_open_app(r"{}\error_log.txt".format(exe_folder))
