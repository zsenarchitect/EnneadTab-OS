import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import random
import os

class DVDLogoApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-transparentcolor', 'white')  # Makes blue color transparent
        self.root.attributes("-topmost", True)  # Always on top
        self.root.overrideredirect(True)  # Remove window border

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Load and resize the image before creating the label
        self.load_and_resize_image(os.path.join(os.path.dirname(__file__), "dvd_logo.png"), 0.3)

        # Define the label here, after resizing image but before applying new background
        self.label = tk.Label(root, bg='blue')  # Temporarily set bg to 'blue', the transparent color
        self.label.place(relx=0.5, rely=0.5, anchor='center')

        # Now apply the initial background color, which also updates the label's image
        self.apply_new_background('green')

        # Initial random position for the window
        initial_x = random.randint(0, self.screen_width - self.window_width)
        initial_y = random.randint(0, self.screen_height - self.window_height)
        self.root.geometry(f"{self.window_width}x{self.window_height}+{initial_x}+{initial_y}")

        
        self.speed_x = 3 if random.random() > 0.5 else -3
        self.speed_y = 3 if random.random() > 0.5 else -3

        self.move()

        
        # Bind the mouse movement event
        self.root.bind('<Motion>', self.fade_on_mouse_move)

        
        # Schedule the application to close
        self.root.after(1500000, self.closing_app)

    def fade_on_mouse_move(self, event=None):
        # Start fading effect; you might want conditions to prevent re-triggering
        self.fade_out(step=0.05)

        
    def load_and_resize_image(self, image_path, scale):
        # Load and resize image, keeping transparency
        original_image = Image.open(image_path).convert("RGBA")
        original_width, original_height = original_image.size
        self.window_width = int(original_width * scale)
        self.window_height = int(original_height * scale)
        resized_image = original_image.resize((self.window_width, self.window_height), Image.Resampling.LANCZOS)
        
        self.original_resized_image = resized_image  # Store the resized image without background


    def apply_new_background(self, color):
        # Apply a new background color
        background = Image.new("RGBA", self.original_resized_image.size, color)
        composite_image = Image.alpha_composite(background, self.original_resized_image)
        self.photo = ImageTk.PhotoImage(composite_image.convert("RGB"))  # Convert back to RGB
        self.label.config(image=self.photo)
        self.label.image = self.photo  # Keep a reference

    def move(self):
        current_geometry = self.root.geometry()
        _, _, current_x, current_y = map(int, current_geometry.replace('x', '+').split('+'))

        new_x = current_x + self.speed_x
        new_y = current_y + self.speed_y

        # Reverse direction if hitting screen boundaries
        if new_x <= 0 or new_x + self.window_width >= self.screen_width:
            self.speed_x = -self.speed_x
            self.change_background_color()
        if new_y <= 0 or new_y + self.window_height >= self.screen_height:
            self.speed_y = -self.speed_y
            self.change_background_color()

        # Apply new position
        self.root.geometry(f"+{new_x}+{new_y}")

        self.root.after(10, self.move)

    def closing_app(self):
        self.fade_out()

    def fade_out(self, step=0.05):
        # Get the current alpha level
        current_alpha = self.root.attributes("-alpha")
        # Calculate the new alpha level
        new_alpha = current_alpha - step
        
        if new_alpha > 0:
            # Apply the new alpha level, making the window more transparent
            self.root.attributes("-alpha", new_alpha)
            # Continue fading after a short delay
            self.root.after(50, lambda: self.fade_out(step))
        else:
            # Once fully transparent, destroy the window
            self.root.destroy()

    def change_background_color(self):
        colors = ['red', 'blue', 'yellow', 'orange', 'purple', 'pink', "green"]
        new_color = random.choice(colors)
        self.apply_new_background(new_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = DVDLogoApp(root)
    root.mainloop()
