
import math
import sys
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"
import pygame

class BasePyGameGUI:
    BACKGROUND_COLOR = (52, 78, 91)
    TEXT_COLOR = (255, 255, 255)
    TEXT_COLOR_FADE = (150, 150, 150)
    TEXT_COLOR_WARNING = (252, 127, 3)
    TEXT_COLOR_BIG_WARNING = (242, 52, 39)

    
    FONT_TITLE = ("arialblack", 30)
    FONT_SUBTITLE = ("arialblack", 20)
    FONT_BODY = ("arial", 15)
    FONT_NOTE = ("arialblack", 10)

    run = True

    
    def reset_pointer(self):
        self.POINTER_X = self.POINTER_Y = 50

    def setup_GUI(self):
        if self.is_another_app_running():
            sys.exit()
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(self.app_title)

        self.FONT_TITLE = pygame.font.SysFont(*BasePyGameGUI.FONT_TITLE)
        self.FONT_SUBTITLE = pygame.font.SysFont(*BasePyGameGUI.FONT_SUBTITLE)
        self.FONT_BODY = pygame.font.SysFont(*BasePyGameGUI.FONT_BODY)
        self.FONT_NOTE = pygame.font.SysFont(*BasePyGameGUI.FONT_NOTE)

        EA_logo = pygame.image.load("{}\\images\\Ennead_Architects_Logo.png".format(self.content_folder)).convert_alpha()
        target_img_size = (100, 100)
        EA_logo = pygame.transform.scale(EA_logo, target_img_size)
        self.original_logo = EA_logo
        self.logo_rect = EA_logo.get_rect(center=(100, self.SCREEN_HEIGHT - 100))

        self.clock = pygame.time.Clock()
        self.FPS = 20

        quit_img = pygame.image.load("{}\\images\\button_quit.png".format(self.content_folder)).convert_alpha()
        self.quit_button = Button(self.SCREEN_WIDTH - 180, self.SCREEN_HEIGHT - 150, quit_img, 1)

    def check_exit(self):
        if self.quit_button.draw(self.screen):
            self.run = False

        if self.life_count < 0:
            self.run = False
            
        
        self.life_count -= 1
        self.update_footnote()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = True
            if event.type == pygame.QUIT:
                self.run = False


                
    def is_another_app_running(self):
        import pyautogui
        for window in pyautogui.getAllWindows():
            if window.title == self.app_title:
                return True
        return False

    def draw_text(self, text, font, text_col):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (self.POINTER_X, self.POINTER_Y))
        self.POINTER_Y += font.get_height()

    def update_title(self):
        self.POINTER_Y = 50
        self.draw_text(self.app_title, self.FONT_TITLE, self.TEXT_COLOR)# draw the title tezt

        
    def update_footnote(self):
        text_life = int(self.life_count / self.FPS)
        text_hours = str(text_life // 3600)
        text_min = str((text_life % 3600) // 60)
        text_secs = str((text_life % 3600) % 60)
        self.POINTER_Y = self.SCREEN_HEIGHT - 20
        self.draw_text("To save memory, {} will close itself in {}h {}m {}s, AKA end of the day.".format(self.app_title, text_hours, text_min, text_secs), self.FONT_NOTE, self.TEXT_COLOR)

    def update_logo_angle(self):
        if not hasattr(self, "logo_angle"):
            self.logo_angle = 0
            
        self.logo_angle = self._get_pointer_logo_angle(*self.logo_rect.center)

        self.EA_logo, self.logo_rect = self._rotate_img_around_center(self.original_logo, self.logo_rect, self.logo_angle)
        self.screen.blit(self.EA_logo, self.logo_rect)

    def _rotate_img_around_center(self, image, rect, angle):

        """Rotate the image while keeping its center."""
        new_image = pygame.transform.rotate(image, angle)
        rect = new_image.get_rect(center=rect.center)
        return new_image, rect

    
    def _get_pointer_logo_angle(self, pt_x, pt_y):
        """Get the angle of a line[current mouse position to a given pt] to X axis"""

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x == pt_x:
            return 90 + 180 * (mouse_y > pt_y)
        angle = math.atan(-float(mouse_y - pt_y) / float(mouse_x - pt_x)) * 180 / math.pi
        angle += 180 * (mouse_x < pt_x)
        return angle

    def format_seconds(self, time_stamp):
        text_min = int(math.floor(time_stamp / 60))
        text_secs = int(time_stamp % 60)
        return "{}m {}s".format(text_min, text_secs)

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

