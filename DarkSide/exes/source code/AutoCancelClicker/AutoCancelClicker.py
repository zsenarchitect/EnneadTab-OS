#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pyautogui
import sys
import logging
import pygame
import cv2
from pyautogui import ImageNotFoundException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util
import _GUI_Util

TITLE = u"EnneadTab Auto Cancel Clicker."

def is_there_cancel_button(cancel_button_icon_file, confidence=0.8):
    try:
        cancel_button_icon = pyautogui.locateOnScreen(cancel_button_icon_file, confidence=confidence)
        logger.info(cancel_button_icon)
        if not cancel_button_icon:
            logger.info("Cancel button not found.")
            return False

        pyautogui.click(pyautogui.center(cancel_button_icon))
        logger.info("Cancel button clicked.")
        return True

    except ImageNotFoundException as e:
        logger.error("Image not found. Ensure the image is on the screen and the path is correct.", exc_info=True)
        return False
    except Exception as e:
        logger.error("Failed to locate or click the cancel button.", exc_info=True)
        return False

def take_screenshot(save_path):
    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)
    logger.info(f"Screenshot saved at {save_path}")

class AutoCancelClicker(_GUI_Util.BasePyGameGUI):
    def __init__(self):
        pygame.init()  # Ensure pygame is initialized
        self.app_title = TITLE
        self.SCREEN_WIDTH = 700
        self.SCREEN_HEIGHT = 500
        self.content_folder = os.path.dirname(__file__)

        self.life_max = _GUI_Util.BasePyGameGUI.MAX_LIFE
        self.life_count = self.life_max

        self.taskbar_icon = "{}\\images\\icon.png".format(self.content_folder)
        self.cancel_button_icon_file = "{}\\images\\icon_lookup.png".format(self.content_folder)

        self.setup_GUI()

    @_Exe_Util.try_catch_error
    def main(self):
        while self.run:
            self.reset_pointer()  # move pointer to initial position
            self.screen.fill(self.BACKGROUND_COLOR)  # fill background color before drawing anything else

            self.update_logo_angle()  # update animated logo
            self.update_title()
            self.draw_text("This tool actively looks for", self.FONT_BODY, self.TEXT_COLOR)
            self.draw_text("the warning cancel icon on your screen.", self.FONT_BODY, self.TEXT_COLOR)
            self.draw_text("And clicks it to bypass the warning popup.", self.FONT_BODY, self.TEXT_COLOR)
            self.update_footnote()

            if self.life_count % 10 == 0 and is_there_cancel_button(self.cancel_button_icon_file):
                self.life_count = self.life_max

            self.check_exit()

            # refresh all drawings by order
            self.clock.tick(self.FPS)
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    AutoCancelClicker().main()
