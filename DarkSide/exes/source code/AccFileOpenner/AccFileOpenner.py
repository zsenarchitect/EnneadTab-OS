import os
import re
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import sys
from gui import BaseApp
from tkinterdnd2 import TkinterDnD

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util

FILE_CATELOG = {
    "indesign": {
        "lock_file_extension": ".idlk",
        "lock_file_begin_template": "~{}",
        "file_extension": ".indd",
    },
    "rhino": {
        "lock_file_extension": ".rhl",
        "lock_file_begin_template": "{}",
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
        self.monitor_acc_folder()


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
        
        if self.check_self_editing(original_file):
            messagebox.showwarning("Warning", "You are already editing this file.")
            return

        self.update_file_path_label(original_file)

        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        desktop_file = os.path.join(desktop_path, file_name)

        shutil.copy2(original_file, desktop_file)
        os.startfile(desktop_file)

        self.cleanup_old_request_files(original_file)
        current_editor = self.check_existing_editors(original_file)
        if current_editor:
            self.create_request_file(original_file)
            messagebox.showwarning("Warning", f"This file is currently edited by {current_editor}.\n\nA request file has been placed.")
            return
        self.create_editing_marker(original_file, file_name)
        
        # Start monitoring the lock file using tkinter's after method
        self.monitor_file_lock(original_file, desktop_file)

    def update_file_path_label(self, file_path):
        wrap_length = int(self.windowX * 0.8)
        self.file_path_label.config(text=file_path, wraplength=wrap_length)

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
            search = re.match(rf'\[(\w+)_editing\]_{file_name}', file)
            if search:
                username = search.group(1)
                print(f"File is currently being edited by: {username}")
                return username
        return None

    def check_self_editing(self, original_file):
        file_name = os.path.basename(original_file)
        dir_name = os.path.dirname(original_file)
        for file in os.listdir(dir_name):
            if re.match(rf'\[{self.username}_editing\]_{file_name}', file):
                return True
        return False

    def create_editing_marker(self, original_file, file_name):
        marker_file = os.path.join(os.path.dirname(original_file), f"[{self.username}_editing]_{file_name}")
        with open(marker_file, "w") as f:
            f.write(f"This file is currently being edited by {self.username}.")
        print(f"Created editing marker: {marker_file}")

    def get_lock_file(self, desktop_file):
        file_category_data = self.get_file_category_data(desktop_file)
        lock_file_extension = file_category_data["lock_file_extension"]
        lock_file_begin_template = file_category_data["lock_file_begin_template"]
        base_name = os.path.basename(desktop_file)
        lock_file_begin = lock_file_begin_template.format(base_name.replace(file_category_data["file_extension"], ""))

        def check_for_lock_file():
            for f in os.listdir(os.path.dirname(desktop_file)):
                if f.endswith(lock_file_extension) and f.lower().startswith(lock_file_begin.lower()):
                    print(f"File lock found: {f}")
                    return os.path.join(os.path.dirname(desktop_file), f)
            print("File lock not found")
            self.root.after(1000, check_for_lock_file)
            return None
        
        return check_for_lock_file()

    def monitor_file_lock(self, original_file, desktop_file):
        def check_lock_file():
            lock_file = self.get_lock_file(desktop_file)
            if lock_file and os.path.exists(lock_file):
                self.root.after(1000, check_lock_file)
            else:
                self.copy_back_to_original(original_file, desktop_file)

        check_lock_file()

    
    def get_file_category_data(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        for category, info in FILE_CATELOG.items():
            if info["file_extension"] == file_extension:
                return FILE_CATELOG[category]
        return None

    def copy_back_to_original(self, original_file, desktop_file):
        print(f"Copying back to original: {desktop_file} to {original_file}")
        shutil.copy2(desktop_file, original_file)
        os.remove(desktop_file)
        self.remove_editing_marker(original_file)

    def remove_editing_marker(self, original_file):
        marker_file = os.path.join(os.path.dirname(original_file), f"[{self.username}_editing]_{os.path.basename(original_file)}")
        def try_remove_marker():
            if os.path.exists(marker_file):
                try:
                    os.remove(marker_file)
                except Exception as e:
                    print(f"Error removing editing marker: {e}")
                    self.root.after(1000, try_remove_marker)

        try_remove_marker()

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
