
import os
import sys
import subprocess

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD
from file_handle import FileHandler

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util

from ui import UIComponents
from monitor import FolderMonitor


import subprocess

class FileProcessorApp:
    def __init__(self, root):
        self.username = os.getenv("USERNAME")
        self.file_handler = FileHandler(self.username, f"{os.getenv('USERPROFILE')}\\ACCDocs\\Ennead Architects LLP")
        self.ui_components = UIComponents(root, self.open_file_dialog, self.handle_file_drop)
        self.folder_monitor = FolderMonitor(f"{os.getenv('USERPROFILE')}\\ACCDocs\\Ennead Architects LLP")
        self.monitor_acc_folder()

    def monitor_acc_folder(self):
        editing_files, requesting_files = self.folder_monitor.update_editing_and_requesting_files()
        self.ui_components.update_editing_files_panel(editing_files, requesting_files, self.open_file_folder)
        self.ui_components.root.after(2000, self.monitor_acc_folder)

    def open_file_dialog(self, event=None):
        file_path = filedialog.askopenfilename()
        self.handle_file_selection(file_path)

    def handle_file_drop(self, event):
        file_path = event.data.strip("{}")
        print(f"File dropped: {file_path}")
        self.handle_file_selection(file_path)

    def handle_file_selection(self, file_path):
        if self.file_handler.original_file:
            response = messagebox.askyesno(
                "Job in Progress",
                "You already have a file being processed. Do you want to open a new instance to process another file?",
                icon=messagebox.WARNING,
                default=messagebox.NO
            )
            if response:
                self.start_new_instance()
            return

        if file_path:
            warning = self.file_handler.process_file(file_path, os.startfile)
            if warning:
                messagebox.showwarning("Warning", warning)

    def start_new_instance(self):
        current_script = sys.argv[0]
        subprocess.Popen([sys.executable, current_script])

    def open_file_folder(self, file_path):
        folder_path = os.path.dirname(file_path)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showerror("Error", "Folder not found.")
@_Exe_Util.try_catch_error
def main():
    root = TkinterDnD.Tk()
    app = FileProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
