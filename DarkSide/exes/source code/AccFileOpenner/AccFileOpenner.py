"""
Actively search through ACC folder for all kinds of lock files. Because those lock files never sync, so every lock file belongs to the current user.
When a lock file is detected, make an editing file marker. When a lock file is removed, delete the editing file marker.

When looping for lock files, also look for any other editing marker files, so when you are opening a file (and about to make an editing marker) you will be warned
with a flashing screen that another user is already editing, suggesting you quit editing. Then the tool places a request file.

When opening a file (and about to make an editing marker), if there is no editing marker file, then try to remove any of your previous request markers.

There is a panel displaying all editing and requesting files in the ACC folder.

Customized locker file system that ACC desktop connector can sync. 
When another user is editing, you cannot open the same file but can place a request.
The request will be converted to an edit lock when the original editor leaves the document AND if you want to edit the document.
All lock and request files will be generated/cleaned automatically by the toolbox.
Please keep it running in the background. Close only after you close the InDesign document.

What if one of the team members is not using this toolbox to open files?
They will not be able to quickly generate a lock file to stop other people from opening the same file. They and other people are at risk of overriding.
BUT you don't need this tool to see the other lock/request files. Those are natively visible in any file explorer window.
"""

import os
import re
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import sys
import time
from gui import BaseApp
from tkinterdnd2 import TkinterDnD, DND_FILES

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util

FILE_CATELOG = {
    "indesign": {
        "lock_file_extension": ".idlk",
        "file_extension": ".indd",
    },
    "rhino": {
        "lock_file_extension": ".rhl",
        "file_extension": ".3dm",
    }
}

class FileProcessorApp(BaseApp):
    def __init__(self, root):
        self.username = os.getenv("USERNAME")
        super().__init__(root)
        self.selected_file = ""
        self.output_file = ""
        self.acc_folder = f"{os.getenv('USERPROFILE')}\\ACCDocs\\Ennead Architects LLP"
        self.create_dashboard()
        self.monitor_acc_folder()

    def create_dashboard(self):
        self.dashboard_frame = tk.Frame(self.root, bg='#3e3e3e', height=100)
        self.dashboard_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self.root.grid_rowconfigure(2, weight=1)

        self.canvas = tk.Canvas(self.dashboard_frame, bg='#3e3e3e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.draw_rounded_rect(10, 10, 580, 120, 20, fill='#E91E63', width=4, dash=(10, 10))
        self.dashboard_label = tk.Label(self.dashboard_frame, text="Drag and Drop a file here or Click to Select a file", bg='#3e3e3e', fg='white', font=('Helvetica', 14, 'bold'))
        self.dashboard_label.pack(pady=20)

        self.dashboard_label.bind("<Button-1>", self.open_file_dialog)
        self.dashboard_frame.bind("<Button-1>", self.open_file_dialog)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_file_drop)

    def draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        self.canvas.create_line(x1+radius, y1, x2-radius, y1, **kwargs)
        self.canvas.create_line(x2, y1+radius, x2, y2-radius, **kwargs)
        self.canvas.create_line(x2-radius, y2, x1+radius, y2, **kwargs)
        self.canvas.create_line(x1, y2-radius, x1, y1+radius, **kwargs)
        self.canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, style='arc', **kwargs)
        self.canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, style='arc', **kwargs)
        self.canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, style='arc', **kwargs)
        self.canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, style='arc', **kwargs)

    def open_file_dialog(self, event=None):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.process_file(file_path)

    def handle_file_drop(self, event):
        file_path = event.data.strip("{}")
        print(f"File dropped: {file_path}")
        if file_path:
            self.process_file(file_path)

    @_Exe_Util.try_catch_error
    def process_file(self, original_file):
        print(f"Processing file: {original_file}")
        file_name = os.path.basename(original_file)
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        desktop_file = os.path.join(desktop_path, file_name)

        shutil.copy2(original_file, desktop_file)
        os.startfile(desktop_file)

        self.cleanup_old_request_files(original_file)
        if self.check_existing_editors(original_file):
            self.create_request_file(original_file)
            messagebox.showwarning("Warning", f"This file is currently edited by another user.\n\nA request file has been placed.")
            return
        self.create_editing_marker(original_file, file_name)
        self.monitor_file_lock(original_file, desktop_file)

    def cleanup_old_request_files(self, original_file):
        file_name = os.path.basename(original_file)
        dir_name = os.path.dirname(original_file)
        print(f"Cleaning up old request files in {dir_name}")
        for file in os.listdir(dir_name):
            if re.match(rf'\[{self.username}_requesting\]_{file_name}', file):
                print(f"Removing request file: {file}")
                os.remove(os.path.join(dir_name, file))

    def check_existing_editors(self, original_file):
        file_name = os.path.basename(original_file)
        dir_name = os.path.dirname(original_file)
        print(f"Checking for existing editors in {dir_name}")
        for file in os.listdir(dir_name):
            if re.match(rf'\[(\w+)_editing\]_{file_name}', file):
                print(f"File is currently being edited by: {file}")
                return True
        return False

    def create_editing_marker(self, original_file, file_name):
        marker_file = os.path.join(os.path.dirname(original_file), f"[{self.username}_editing]_{file_name}")
        with open(marker_file, "w") as f:
            f.write(f"This file is currently being edited by {self.username}.")
        print(f"Created editing marker: {marker_file}")

    def monitor_file_lock(self, original_file, desktop_file):
        lock_file_extension = FILE_CATELOG["indesign"]["lock_file_extension"]
        lock_file = original_file.replace(FILE_CATELOG["indesign"]["file_extension"], lock_file_extension)
        print(f"Monitoring lock file: {lock_file}")
        while os.path.exists(lock_file):
            time.sleep(1)
        self.copy_back_to_original(original_file, desktop_file)

    def copy_back_to_original(self, original_file, desktop_file):
        print(f"Copying back to original: {desktop_file} to {original_file}")
        shutil.copy2(desktop_file, original_file)
        os.remove(desktop_file)
        self.remove_editing_marker(original_file)

    def remove_editing_marker(self, original_file):
        marker_file = os.path.join(os.path.dirname(original_file), f"[{self.username}_editing]_{os.path.basename(original_file)}")
        if os.path.exists(marker_file):
            print(f"Removing editing marker: {marker_file}")
            os.remove(marker_file)

    def create_request_file(self, original_file):
        request_file_name = f"[{self.username}_requesting]_{os.path.basename(original_file)}"
        request_file_path = os.path.join(os.path.dirname(original_file), request_file_name)
        with open(request_file_path, "w") as f:
            f.write(f"Request to edit the file by {self.username}")
        print(f"Created request file: {request_file_path}")

    def check_request_files(self, original_file):
        request_users = []
        dir_name = os.path.dirname(original_file)
        for file in os.listdir(dir_name):
            if re.match(rf'\[(\w+)_requesting\]_{os.path.basename(original_file)}', file):
                request_users.append(file.split('_')[0][1:])  # Extract username from file name
        return request_users

    def monitor_acc_folder(self):
        self.update_editing_and_requesting_files()
        self.root.after(2000, self.monitor_acc_folder)

    def update_editing_and_requesting_files(self):
        editing_files = []
        requesting_files = []
        for root, dirs, files in os.walk(self.acc_folder):
            if "_D" in root:
                continue
            for file in files:
                if re.match(r'\[\w+_editing\]', file):
                    editing_files.append(os.path.join(root, file))
                elif re.match(r'\[\w+_requesting\]', file):
                    requesting_files.append(os.path.join(root, file))
        self.update_editing_files_panel(editing_files, requesting_files)

    def update_editing_files_panel(self, editing_files, requesting_files):
        self.editing_files_text.configure(state='normal')
        self.editing_files_text.delete('1.0', tk.END)
        self.editing_files_text.insert(tk.END, "Editing Files:\n")
        for file in editing_files:
            self.editing_files_text.insert(tk.END, f"{file}\n")
        self.editing_files_text.insert(tk.END, "\nRequesting Files:\n")
        for file in requesting_files:
            self.editing_files_text.insert(tk.END, f"{file}\n")
        self.editing_files_text.configure(state='disabled')

@_Exe_Util.try_catch_error
def main():
    root = TkinterDnD.Tk()
    app = FileProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
