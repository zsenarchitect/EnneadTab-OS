import os
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import datetime
from tkinterdnd2 import DND_FILES
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _GUI_Base_Util
EXPIRATION_DATE = datetime.date(2025, 1, 1)

class BaseApp(_GUI_Base_Util.BaseGUI):
    def __init__(self, root):
        self.root = root
        self.root.configure(bg=self.BACKGROUND_COLOR_HEX)
        self.root.geometry("1000x800")
        self.setup_icon()
        self.create_widgets()
        self.setup_bindings()
        self.update_title_with_days_left()
        self.create_dashboard()

    def setup_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon_ennead-e.ico")
        self.root.iconbitmap(icon_path)
        self.logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        self.logo_image = Image.open(self.logo_path)
        self.logo_image = self.logo_image.resize((self.logo_image.width // 2, self.logo_image.height // 2), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

    def create_widgets(self):
        self.logo_label = tk.Label(self.root, image=self.logo_photo, bg=self.BACKGROUND_COLOR_HEX)
        self.logo_label.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.editing_files_frame = tk.Frame(self.root, bg=self.BACKGROUND_COLOR_HEX)
        self.editing_files_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.editing_files_text = scrolledtext.ScrolledText(self.editing_files_frame, width=60, height=15, bg=self.BACKGROUND_COLOR_HEX, fg='white', font=('Helvetica', 12, 'bold'), wrap=tk.WORD)
        self.editing_files_text.pack(fill=tk.BOTH, expand=True)
        self.editing_files_text.config(height=10)
        self.editing_files_text.config(height=10)  # Setting fixed height

        note = "The file will open automatically after picked/dropped."
        note += "\nAccepting File types of Indesign, Rhino, Word, Excel, PDF, Photoshop, Illustrator"
        self.instructions_label = tk.Label(self.root, text=note, bg=self.BACKGROUND_COLOR_HEX, fg='white', font=('Helvetica', 12), wraplength=800, justify=tk.LEFT)
        self.instructions_label.grid(row=2, column=0, columnspan=3, sticky="nw", padx=20, pady=10)

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

        self.dashboard_label.bind("<Button-1>", self.open_file_dialog)
        self.dashboard_frame.bind("<Button-1>", self.open_file_dialog)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_file_drop)

        self.dashboard_label.bind("<Enter>", self.change_cursor_to_hand)
        self.dashboard_label.bind("<Leave>", self.change_cursor_to_arrow)
        self.dashboard_frame.bind("<Enter>", self.change_cursor_to_hand)
        self.dashboard_frame.bind("<Leave>", self.change_cursor_to_arrow)

    def change_cursor_to_hand(self, event):
        return
        event.widget.config(cursor="hand2")

    def change_cursor_to_arrow(self, event):
        return
        event.widget.config(cursor="")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseApp(root)
    root.mainloop()
