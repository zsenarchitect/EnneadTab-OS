import os
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import datetime

EXPIRATION_DATE = datetime.date(2025, 1, 1)

class BaseApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg='#2e2e2e')
        self.root.geometry("1000x800")
        self.setup_icon()
        self.create_widgets()
        self.setup_bindings()
        self.update_title_with_days_left()

    def setup_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon_ennead-e.ico")
        self.root.iconbitmap(icon_path)
        self.logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        self.logo_image = Image.open(self.logo_path)
        self.logo_image = self.logo_image.resize((self.logo_image.width // 2, self.logo_image.height // 2), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

    def create_widgets(self):
        self.logo_label = tk.Label(self.root, image=self.logo_photo, bg='#2e2e2e')
        self.logo_label.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.editing_files_text = scrolledtext.ScrolledText(self.root, width=60, height=20, bg='#2e2e2e', fg='white', font=('Helvetica', 12, 'bold'))
        self.editing_files_text.grid(row=1, column=0, columnspan=3, sticky="nsew")

        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def setup_bindings(self):
        self.root.bind("<Motion>", self.rotate_logo)

    def rotate_logo(self, event):
        max_rotation = 20
        width = self.root.winfo_width()
        relative_x = event.x / width
        angle = (relative_x * 2 - 1) * max_rotation
        angle = max(min(angle, max_rotation), -max_rotation)
        rotated_image = self.logo_image.rotate(angle)
        self.logo_photo = ImageTk.PhotoImage(rotated_image)
        self.logo_label.configure(image=self.logo_photo)

    def update_title_with_days_left(self):
        days_left = (EXPIRATION_DATE - datetime.date.today()).days
        if days_left <= 0:
            self.root.title("ACC File Opener - Tool Expired")
        elif days_left <= 30:
            self.root.title(f"ACC File Opener - {days_left} days left")
        else:
            self.root.title("ACC File Opener")