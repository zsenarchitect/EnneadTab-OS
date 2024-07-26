

import traceback
import os
def log_error(error):
    error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
    error_file = "{}\Documents\EnneadTab Settings\Local Copy Dump\error_log.txt".format(
        os.environ["USERPROFILE"])

    with open(error_file, "w") as f:
        f.write(error)
    if 'szhang' in os.environ["USERPROFILE"] :
        os.startfile(error_file)

        
try:
    
    import pygame
    import pyautogui
    from PIL import Image, ImageFilter
except:
    error = traceback.format_exc()
    log_error(error)



class LotteryScratch:
    def __init__(self, width=640, height=480):
        self.root_folder = os.path.dirname(__file__)
        
        self.capture_desktop()
        self.screen_width = width
        self.screen_height = height




        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.wipe_sound = pygame.mixer.Sound('{}\\wipe_sound.mp3'.format(self.root_folder))
        self.brush_shape = pygame.image.load('{}\\brush_shape.png'.format(self.root_folder)).convert_alpha()

    def capture_desktop(self):
        self.screenshot_path = '{}\\desktop_screenshot.png'.format(self.root_folder)
        self.blurry_screenshot_path = '{}\\blurry_screenshot.png'.format(self.root_folder)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(self.screenshot_path)
        original_image = Image.open(self.screenshot_path)
        blurry_image = original_image.filter(ImageFilter.GaussianBlur(radius=10))
        blurry_image.save(self.blurry_screenshot_path)

    def setup(self):
        

        self.background = pygame.image.load(self.screenshot_path).convert()
        self.scratch_layer = pygame.image.load(self.blurry_screenshot_path).convert_alpha()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if pygame.mouse.get_pressed()[0]:  # If left mouse button is pressed
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.screen.blit(self.brush_shape, 
                                     (mouse_x - self.brush_shape.get_width() / 2, 
                                      mouse_y - self.brush_shape.get_height() / 2), 
                                     special_flags=pygame.BLEND_RGBA_SUB)
                    self.wipe_sound.play()

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.scratch_layer, 
                             (0, 0), 
                             special_flags=pygame.BLEND_RGBA_MULT)
            pygame.display.flip()

        pygame.quit()
        # Clean up temporary files
        os.remove(self.screenshot_path)
        os.remove(self.blurry_screenshot_path)


def main():
    # Initial setup
    pygame.init()
    pygame.mixer.init()

    game = LotteryScratch()
    game.setup()
    game.run()

if __name__ == '__main__':
    try:
        main()
    except:
        error = traceback.format_exc()
        log_error(error)
    print ("Done")