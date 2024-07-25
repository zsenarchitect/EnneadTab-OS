import os

import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import datetime
from tkinterdnd2 import DND_FILES

EXPIRATION_DATE = datetime.date(2025, 1, 1)


class UIComponents:
    def __init__(self, root, open_file_callback, handle_file_drop_callback):
        self.root = root
        self.open_file_callback = open_file_callback
        self.handle_file_drop_callback = handle_file_drop_callback
        self.logo_photo = None
        self.file_path_label = None
        self.finished_button = None
        self.editing_files_text = None
        self.dashboard_label = None  # Initialize dashboard_label
        self.setup_icon()
        self.create_widgets()
        self.create_dashboard()  # Ensure create_dashboard is called before setup_bindings
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

        self.editing_files_frame = tk.Frame(self.root, bg='#2e2e2e')
        self.editing_files_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.editing_files_text = scrolledtext.ScrolledText(self.editing_files_frame, width=60, height=15, bg='#2e2e2e', fg='white', font=('Helvetica', 12, 'bold'))
        self.editing_files_text.pack(fill=tk.BOTH, expand=True)

        self.instructions_label = tk.Label(self.root, text="The file will open automatically after picked/dropped.", bg='#2e2e2e', fg='white', font=('Helvetica', 12), wraplength=800, justify=tk.LEFT)
        self.instructions_label.grid(row=2, column=0, columnspan=3, sticky="nw", padx=20, pady=10)

        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def setup_bindings(self):
        self.root.bind("<Motion>", self.rotate_logo)
        self.dashboard_label.bind("<Button-1>", self.open_file_callback)
        self.dashboard_frame.bind("<Button-1>", self.open_file_callback)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_file_drop_callback)

    def rotate_logo(self, event):
        max_rotation = 20
        width = self.root.winfo_width()
        relative_x = event.x / width
        angle = (relative_x * 2 - 1) * max_rotation
        angle = max(min(angle, max_rotation), -max_rotation)
        rotated_image = self.logo_image.rotate(angle)
        self.logo_photo = ImageTk.PhotoImage(rotated_image)
        self.logo_label.configure(image=self.logo_photo)

    def create_dashboard(self):
        self.dashboard_frame = tk.Frame(self.root, bg='#3e3e3e', height=100)
        self.dashboard_frame.grid(row=3, column=0, columnspan=3, sticky="nsew")
        self.root.grid_rowconfigure(3, weight=1)

        self.canvas = tk.Canvas(self.dashboard_frame, bg='#3e3e3e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.root.update_idletasks()  # Ensure the window is fully rendered
        self.windowX = self.canvas.winfo_width()
        self.windowY = self.canvas.winfo_height()

        self.draw_rounded_rect(10, 10, self.windowX - 10, self.windowY - 10, 20, width=4, dash=(5, 3))  # Adjusted the bottom padding

        self.dashboard_label = tk.Label(self.canvas, text="Drag and Drop a file here or Click to Select a file", bg='#3e3e3e', fg='white', font=('Helvetica', 14, 'bold'))
        self.dashboard_label.place(relx=0.5, rely=0.1, anchor='n')  # Positioned the label at the top

        self.file_path_label = tk.Label(self.canvas, text="", bg='#3e3e3e', fg='white', font=('Helvetica', 12), wraplength=int(self.windowX * 0.8))
        self.file_path_label.place(relx=0.5, rely=0.5, anchor='center')

    def draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        # Draw the lines
        self.canvas.create_line(x1 + radius, y1, x2 - radius, y1, **kwargs)
        self.canvas.create_line(x2, y1 + radius, x2, y2 - radius, **kwargs)
        self.canvas.create_line(x2 - radius, y2, x1 + radius, y2, **kwargs)
        self.canvas.create_line(x1, y2 - radius, x1, y1 + radius, **kwargs)
        
        # Draw the arcs
        self.canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, style='arc', **kwargs)
        self.canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, style='arc', **kwargs)
        self.canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, style='arc', **kwargs)
        self.canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, style='arc', **kwargs)

    def update_title_with_days_left(self):
        days_left = (EXPIRATION_DATE - datetime.date.today()).days
        if days_left <= 0:
            self.root.title("ACC File Opener - Tool Expired")
        elif days_left <= 30:
            self.root.title(f"ACC File Opener - {days_left} days left")
        else:
            self.root.title("ACC File Opener")

    def update_file_path_label(self, file_path):
        wrap_length = int(self.windowX * 0.8)
        self.file_path_label.config(text=file_path, wraplength=wrap_length)

    def clear_file_path_label(self):
        self.file_path_label.config(text="")

    def create_finished_button(self, file_type):
        if self.finished_button:
            self.finished_button.destroy()
        self.finished_button = tk.Button(self.root, 
                                         text=f"I am finished with this {file_type} file, click to remove the [editing] marker file.", 
                                         command=self.copy_back_to_original)
        self.finished_button.grid(row=4, column=0, columnspan=3, pady=10)

    def remove_finished_button(self):
        if self.finished_button:
            self.finished_button.destroy()
            self.finished_button = None

    def insert_clickable_file(self, file_path, open_file_folder_callback):
        start_index = self.editing_files_text.index(tk.END)
        self.editing_files_text.insert(tk.END, f"{file_path}\n", 'body')
        end_index = self.editing_files_text.index(tk.END)
        tag_name = f"tag_{file_path}"  # Use a unique tag name for each file path
        self.editing_files_text.tag_add(tag_name, start_index, end_index)
        self.editing_files_text.tag_bind(tag_name, "<Button-1>", lambda e, path=file_path: open_file_folder_callback(path))
        self.editing_files_text.tag_bind(tag_name, "<Enter>", lambda e, tag=tag_name: self.on_enter(e, tag))
        self.editing_files_text.tag_bind(tag_name, "<Leave>", lambda e, tag=tag_name: self.on_leave(e, tag))

    def on_enter(self, event, tag):
        event.widget.config(cursor="cross")
        event.widget.tag_configure(tag, background="yellow", foreground="black")

    def on_leave(self, event, tag):
        event.widget.config(cursor="")
        event.widget.tag_configure(tag, background="", foreground="")

    def update_editing_files_panel(self, editing_files, requesting_files, open_file_folder_callback):
        self.editing_files_text.configure(state='normal')
        self.editing_files_text.delete('1.0', tk.END)
        self.editing_files_text.tag_configure('header', font=('Helvetica', 12, 'bold'))
        self.editing_files_text.tag_configure('body', font=('Helvetica', 8, 'normal'))
        
        self.editing_files_text.insert(tk.END, "Editing Files:\n", 'header')
        for file in editing_files:
            self.insert_clickable_file(file, open_file_folder_callback)
        
        self.editing_files_text.insert(tk.END, "\nRequesting Files:\n", 'header')
        for file in requesting_files:
            self.insert_clickable_file(file, open_file_folder_callback)
        
        self.editing_files_text.configure(state='disabled')