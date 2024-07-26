import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import datetime
import subprocess
import traceback
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util
# Set the expiration date
EXPIRATION_DATE = datetime.datetime(2025, 1, 31)
WARNING_DATE = EXPIRATION_DATE - datetime.timedelta(days=15)


class FileProcessorApp:
    def __init__(self, root):
        self.check_expiration()

        self.root = root
        self.root.title("File Processor")
        self.root.configure(bg='#2e2e2e')  # Even darker grey

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon_ennead-e.ico")
        self.root.iconbitmap(icon_path)

        self.logo_path = os.path.join(os.path.dirname(__file__), "logo.png")  # Ensure logo.png is in the same directory as this script
        self.logo_image = Image.open(self.logo_path)
        self.logo_image = self.logo_image.resize((self.logo_image.width // 2, self.logo_image.height // 2), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

        self.create_widgets()
        self.selected_files = []
        self.output_folder = ""

        self.root.bind("<Motion>", self.rotate_logo)

        if datetime.datetime.now() >= WARNING_DATE:
            self.warning_label = tk.Label(self.root, text=f"The tool will expire on {EXPIRATION_DATE.strftime('%B %d, %Y')}", bg='#2e2e2e', fg='red')
            self.warning_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def check_expiration(self):
        if datetime.datetime.now() > EXPIRATION_DATE:
            messagebox.showerror("Expired", "The tool has expired, contact Sen Z. for renewal.")
            raise SystemExit("This tool has expired.")

    def create_widgets(self):
        self.logo_label = tk.Label(self.root, image=self.logo_photo, bg='#2e2e2e')
        self.logo_label.grid(row=0, column=0, columnspan=3)

        self.pick_files_button = tk.Button(self.root, text="Pick Files", command=self.pick_files, bg='#2e2e2e', fg='white')
        self.pick_files_button.grid(row=1, column=0, padx=10, pady=10)

        self.pick_output_folder_button = tk.Button(self.root, text="Pick Output Folder", command=self.pick_output_folder, bg='#2e2e2e', fg='white')
        self.pick_output_folder_button.grid(row=1, column=1, padx=10, pady=10)

        self.prefix_label = tk.Label(self.root, text="Prefix:", bg='#2e2e2e', fg='white')
        self.prefix_label.grid(row=2, column=0, padx=10, pady=10)

        self.prefix_entry = tk.Entry(self.root)
        self.prefix_entry.grid(row=2, column=1, padx=10, pady=10)

        self.example_label = tk.Label(self.root, text="Example: [prefix] processedName.extension", bg='#2e2e2e', fg='white')
        self.example_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.process_button = tk.Button(self.root, text="Process", command=self.process_files, bg='#2e2e2e', fg='white')
        self.process_button.grid(row=4, column=0, columnspan=3, padx=10, pady=20)

        self.open_output_folder_button = tk.Button(self.root, text="Open Output Folder", command=self.open_output_folder, bg='#2e2e2e', fg='white', state=tk.DISABLED)
        self.open_output_folder_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    @_Exe_Util.try_catch_error
    def rotate_logo(self, event):
        max_rotation = 20
        width = self.root.winfo_width()
        relative_x = event.x / width
        angle = (relative_x * 2 - 1) * max_rotation  # Range from -max_rotation to +max_rotation
        angle = max(min(angle, max_rotation), -max_rotation)  # Limit the angle to ±20 degrees
        rotated_image = self.logo_image.rotate(angle)
        self.logo_photo = ImageTk.PhotoImage(rotated_image)
        self.logo_label.configure(image=self.logo_photo)

    @_Exe_Util.try_catch_error
    def pick_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF and DWG files", "*.pdf *.dwg")])
        self.selected_files = self.root.tk.splitlist(files)

    @_Exe_Util.try_catch_error
    def pick_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_folder = os.path.join(folder, f"RenamedExport_{timestamp}")
            os.makedirs(self.output_folder, exist_ok=True)
            self.open_output_folder_button.config(state=tk.NORMAL)

    @_Exe_Util.try_catch_error
    def open_output_folder(self):
        if self.output_folder:
            if os.name == 'nt':  # Windows
                os.startfile(self.output_folder)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.call(['open', self.output_folder])

    @_Exe_Util.try_catch_error
    def process_files(self):
        if not self.selected_files or not self.output_folder:
            messagebox.showwarning("Warning", "Please select files and output folder.")
            return

        prefix = self.prefix_entry.get()

        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            processed_name = file_name.split("Sheet - ", 1)[-1]
            if prefix:
                new_name = "[{}] {}".format(prefix, processed_name)
            else:
                new_name = processed_name
            output_path = os.path.join(self.output_folder, new_name)
            shutil.copy(file_path, output_path)

        messagebox.showinfo("Success", "Files processed successfully.")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = FileProcessorApp(root)
        root.mainloop()
    except Exception as e:
        error_message = traceback.format_exc()
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  # Windows
        error_file_path = os.path.join(desktop_path, "file_processor_error_log.txt")
        
        with open(error_file_path, "w") as error_file:
            error_file.write(error_message)
        
        messagebox.showerror("Error", f"An error occurred. Details have been saved to {error_file_path}")
