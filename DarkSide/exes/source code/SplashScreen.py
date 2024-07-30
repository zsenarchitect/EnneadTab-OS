import os
import tkinter as tk
from PIL import Image, ImageTk
import _Exe_Util


class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.splash_data_file = "splash_data.sexyDuck"
        self.splash_scren_image = None
        self.check_splash_data_file()

    def show_splash_screen(self):
        self.splash = tk.Toplevel(self.root)
        self.splash.overrideredirect(True)

        # Load the splash image from splash_data_sexyDuck file
        splash_image = Image.open(self.splash_scren_image)
        splash_photo = ImageTk.PhotoImage(splash_image)

        # Calculate the position to center the window
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        width = splash_photo.width()
        height = splash_photo.height()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.splash.geometry(f"{width}x{height}+{x}+{y}")

        self.splash_label = tk.Label(self.splash, image=splash_photo)
        self.splash_label.image = splash_photo
        self.splash_label.pack()

        self.root.withdraw()

    def get_splash_image(self):
        splash_data = _Exe_Util.get_data_in_dump_folder(self.splash_data_file)
        if splash_data and "image" in splash_data:
            self.splash_scren_image = splash_data.get("image")
            return True
        return False

    def check_splash_data_file(self):
        if self.get_splash_image():
            self.show_splash_screen()
            self.monitor_splash_data_file()
        else:
            self.root.after(500, self.check_splash_data_file)

    def monitor_splash_data_file(self):
        if not os.path.exists(self.splash_data_file):
            self.hide_splash_screen()
        else:
            self.root.after(500, self.monitor_splash_data_file)

    def hide_splash_screen(self):
        self.splash.destroy()
        self.root.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    splash_screen = SplashScreen(root)
    root.mainloop()
