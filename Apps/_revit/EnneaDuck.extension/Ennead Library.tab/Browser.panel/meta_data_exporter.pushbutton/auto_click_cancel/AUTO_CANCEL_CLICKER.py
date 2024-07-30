#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
sys.path.append(r'L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib')
import EnneadTab
import pygame
import pyautogui
import random
import traceback
import os
import button
import math
import sys

sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules')
import EA_TOASTER
import json


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

def is_another_auto_clicker_running():

    #print [x.title for x in pyautogui.getAllWindows()]
    for window in pyautogui.getAllWindows():
        #print window.title
        if window.title == u"EnneadTab Revit Auto Clicker":
            return True
    return False






def main():
    if is_another_auto_clicker_running():
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

    pygame.display.set_caption("EnneadTab Revit Auto Clicker")

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
    exe_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\AUTO_CANCEL_CLICKER"
    print(exe_folder)
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

    #game loop
    run = True

    life_max =  24*60 * 60 * FPS
    life_count = life_max

    count_down_found = -1
    while run:
        #print count_down_found
        # when safty count down <0, i should be allowed to search
        if count_down_found < 0 :
            """
            if life_count % (5 * FPS) == 0:
                print(123)
            """
                #print "trying to find icon" + cancel_button_icon_file
            if life_count % (5 * FPS) == 0 and is_there_cancel_button(cancel_button_icon_file):
                print("found icon")
                
               


                count_down_found = 30 * FPS
                life_count = life_max



        # safty count down > 0----> it is still in waiting period, proceed to count down but no action taken
        else:
            #print "foudn icon, now waitng"
            draw_text("found that icon " + str(count_down_found), font, TEXT_COL, 50, 20)
            count_down_found -= 1


        screen.fill((52, 78, 91))


        angle = get_pointer_angle(*logo_rect.center)# this is to keep it facing mouse
        EA_logo, logo_rect = rotate_img_around_center(original_logo, logo_rect, angle)
        screen.blit(EA_logo, logo_rect)

        #check if game is paused
        draw_text("EnneadTab Revit Cancel Auto Clicker. ", font, TEXT_COL, 50, 50)
        draw_text("Keep this window alive. ", font_title, TEXT_COL_FADE, 50, 100)
        draw_text("Keep Revit app on top.", font_title, TEXT_COL_FADE, 50, 130)


        draw_text("This tool actively look for", font, TEXT_COL_HIGHTLIGHT, 50, 300)
        draw_text("the warning cancel icon on your screen.", font, TEXT_COL_HIGHTLIGHT, 50, 320)
        draw_text("And click it to bypass warning popup.", font, TEXT_COL_HIGHTLIGHT, 50, 340)





        if quit_button.draw(screen):
            run = False

        if life_count < 0:
            run = False
        text_life = int(life_count / FPS)
        text_min = int(math.floor(text_life / 60))
        text_secs = text_life % 60
        draw_text("To save memory, EnneadTab Auto Clicker will close itself in {}m {}s if there is nothing to monitor.".format(text_min, text_secs), font_note, TEXT_COL, 50, SCREEN_HEIGHT - 20)
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

if __name__ == '__main__':
    try:

    main()

    except:
    error = traceback.format_exc()
    print(error)
    exe_folder = os.path.abspath( os.path.dirname( __file__ ) )
    with open(r"{}\error_log.txt".format(exe_folder), "w") as f:
        f.write(error)
        EnneadTab.EXE.open_file_in_default_application(r"{}\error_log.txt".format(exe_folder))
