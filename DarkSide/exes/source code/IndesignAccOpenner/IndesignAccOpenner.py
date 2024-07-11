import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import traceback

def log_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = traceback.format_exc()
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  # Windows
            error_file_path = os.path.join(desktop_path, "file_processor_error_log.txt")
            
            with open(error_file_path, "w") as error_file:
                error_file.write(error_message)
            
            os.startfile(error_file_path)
    return wrapper

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InDesign File Opener")
        self.root.configure(bg='#2e2e2e')

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon_ennead-e.ico")
        self.root.iconbitmap(icon_path)

        self.logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        self.logo_image = Image.open(self.logo_path)
        self.logo_image = self.logo_image.resize((self.logo_image.width // 2, self.logo_image.height // 2), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

        self.create_widgets()
        self.selected_file = ""
        self.output_file = ""
        self.indesign_version = "2024"

        self.root.bind("<Motion>", self.rotate_logo)

    def create_widgets(self):
        self.logo_label = tk.Label(self.root, image=self.logo_photo, bg='#2e2e2e')
        self.logo_label.grid(row=0, column=0, columnspan=3)

        self.pick_file_button = tk.Button(self.root, text="Pick InDesign File", command=self.pick_file, bg='#2e2e2e', fg='white')
        self.pick_file_button.grid(row=1, column=0, padx=10, pady=10)

        self.indesign_version_label = tk.Label(self.root, text="InDesign Version:", bg='#2e2e2e', fg='white')
        self.indesign_version_label.grid(row=2, column=0, padx=10, pady=10)

        self.indesign_version_entry = tk.Entry(self.root)
        self.indesign_version_entry.insert(0, "2024")
        self.indesign_version_entry.grid(row=2, column=1, padx=10, pady=10)

        self.selected_file_label = tk.Label(self.root, text="", bg='#2e2e2e', fg='white')
        self.selected_file_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.process_button = tk.Button(self.root, text="Open in InDesign", command=self.process_file, bg='#2e2e2e', fg='white')
        self.process_button.grid(row=4, column=0, columnspan=3, padx=10, pady=20)
        self.process_button.config(state=tk.DISABLED)

    @log_error
    def rotate_logo(self, event):
        max_rotation = 20
        width = self.root.winfo_width()
        relative_x = event.x / width
        angle = (relative_x * 2 - 1) * max_rotation
        angle = max(min(angle, max_rotation), -max_rotation)
        rotated_image = self.logo_image.rotate(angle)
        self.logo_photo = ImageTk.PhotoImage(rotated_image)
        self.logo_label.configure(image=self.logo_photo)

    @log_error
    def pick_file(self):
        file = filedialog.askopenfilename(filetypes=[("InDesign files", "*.indd")])
        self.selected_file = file
        if file:
            self.selected_file_label.config(text=f"Selected File: {os.path.basename(file)}")
            self.process_button.config(state=tk.NORMAL)
    
    @log_error
    def process_file(self):
        if not self.selected_file:
            messagebox.showwarning("Warning", "Please select an InDesign file.")
            return
        
        username = os.getenv('USERNAME')  # Get current user's name
        prefix = "[{}]_".format(username)
        file_name = os.path.basename(self.selected_file)
        
        # Check if the file already has a prefix using a regular expression
        if re.match(r'\[\w+\]_', file_name):
            existing_user = re.match(r'\[(\w+)\]_', file_name).group(1)
            messagebox.showwarning("Warning", f"This file is currently edited by {existing_user}.")
            return
        
        self.indesign_version = self.indesign_version_entry.get()

        original_file = self.selected_file[:]
        renamed_file = os.path.join(os.path.dirname(self.selected_file), "{}{}".format(prefix, file_name))
        os.rename(self.selected_file, renamed_file)

        
        indesign_script_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', "EnneadTab_Indesign_Save_Opener.jsx")
        with open(indesign_script_path, "w") as script_file:
            script_file.write(self.generate_indesign_script(renamed_file, original_file))

        self.open_indesign(indesign_script_path)
    
    def generate_indesign_script(self, renamed_file, original_file):
        return f"""
        #target InDesign

        var myDocument = app.open("{renamed_file}");

        myDocument.addEventListener("afterClose", function(event) {{
            # rename file from renamed_file to original_file
            # need help
            
        }});
        """
    
    def open_indesign(self, script_path):
        try:
            indesign_exe = f"C:\\Program Files\\Adobe\\Adobe InDesign {self.indesign_version}\\InDesign.exe"
            subprocess.run([indesign_exe, '-executeScript', script_path], check=True)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find InDesign executable. Make sure version {self.indesign_version} is installed.")
            error_message = traceback.format_exc()
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            error_file_path = os.path.join(desktop_path, "file_processor_error_log.txt")
            
            with open(error_file_path, "w") as error_file:
                error_file.write(error_message)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Could not open InDesign. Make sure version {self.indesign_version} is installed.")
            error_message = traceback.format_exc()
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            error_file_path = os.path.join(desktop_path, "file_processor_error_log.txt")
            
            with open(error_file_path, "w") as error_file:
                error_file.write(error_message)

@log_error
def main():
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
