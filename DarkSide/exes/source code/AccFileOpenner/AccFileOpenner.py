import os
import re
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import sys
import time
from eel import sleep
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
    def process_file(self, file_path):
        self.original_file = file_path
        print(f"Processing file: {self.original_file}")

        file_name = os.path.basename(self.original_file)

        if self.check_self_editing():
            messagebox.showwarning("Warning", "You are already editing this file.")
            return

        self.update_file_path_label()

        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        self.desktop_file = os.path.join(desktop_path, file_name)

        # Start the copy process
        shutil.copy2(self.original_file, self.desktop_file)
        
        # Check if the copy is complete
        def check_copy_complete():
            if os.path.exists(self.desktop_file):
                os.startfile(self.desktop_file)

                self.cleanup_old_request_files()
                current_editor = self.check_existing_editors()
                if current_editor:
                    self.create_request_file()
                    messagebox.showwarning("Warning", f"This file is currently edited by {current_editor}.\n\nA request file has been placed.")
                    return
                self.create_editing_marker()

                # Start monitoring the lock file using tkinter's after method
                self.monitor_file_lock( )

            else:
                self.root.after(100, check_copy_complete)

        check_copy_complete()

        

    def get_lock_file(self):
        file_category_data = self.get_file_category_data()
        lock_file_extension = file_category_data["lock_file_extension"]
        lock_file_begin_template = file_category_data["lock_file_begin_template"]
        base_name = os.path.basename(self.desktop_file)
        lock_file_begin = lock_file_begin_template.format(base_name.replace(file_category_data["file_extension"], ""))


        
        while True:
            for f in os.listdir(os.path.dirname(self.desktop_file)):
                if f.endswith(lock_file_extension) and f.lower().startswith(lock_file_begin.lower()):
                    print(f"File lock found: {f}")
                  
                    return os.path.join(os.path.dirname(self.desktop_file), f)
            print("File lock not found")
                
            time.sleep(1)
            

    def monitor_file_lock(self):
        lock_file = self.get_lock_file()
        # at this point the lock file should exist
        print(f"Monitoring lock file: {lock_file}")

        def check_lock():
            if not os.path.exists(lock_file):
                print ("Lock file gone, ready to sync abck to acc")
                self.copy_back_to_original()
                print ("!!!!job done!")
            else:
                print ("Lock file still exist")
                self.root.after(1000, check_lock)

        check_lock()
        
            
       

    def copy_back_to_original(self):
        print(f"Copying back to original: {self.desktop_file} to {self.original_file}")
        shutil.copy2(self.desktop_file, self.original_file)
        os.remove(self.desktop_file)
        self.remove_editing_marker()
        self.clear_file_path_label()
         


    def clear_file_path_label(self):
        self.file_path_label.config(text="")

    def update_file_path_label(self):
        wrap_length = int(self.windowX * 0.8)
        self.file_path_label.config(text=self.original_file, wraplength=wrap_length)

    def cleanup_old_request_files(self):
        file_name = os.path.basename(self.original_file)
        dir_name = os.path.dirname(self.original_file)
        print(f"Cleaning up old request files in {dir_name}")
        for file in os.listdir(dir_name):
            if re.match(rf'\[{self.username}_requesting\]_{file_name}', file):
                print(f"Removing request file: {file}")
                os.remove(os.path.join(dir_name, file))

    def check_existing_editors(self):
        file_name = os.path.basename(self.original_file)
        dir_name = os.path.dirname(self.original_file)
        print(f"Checking for existing editors in {dir_name}")
        for file in os.listdir(dir_name):
            search = re.match(rf'\[(\w+)_editing\]_{file_name}', file)
            if search:
                username = search.group(1)
                print(f"File is currently being edited by: {username}")
                return username
        return None

    def check_self_editing(self):
        file_name = os.path.basename(self.original_file)
        dir_name = os.path.dirname(self.original_file)
        for file in os.listdir(dir_name):
            if re.match(rf'\[{self.username}_editing\]_{file_name}', file):
                return True
        return False

    def create_editing_marker(self):
        file_name = os.path.basename(self.original_file)
        marker_file = os.path.join(os.path.dirname(self.original_file), f"[{self.username}_editing]_{file_name}")
        with open(marker_file, "w") as f:
            f.write(f"This file is currently being edited by {self.username}.")
        print(f"Created editing marker: {marker_file}")
     
        
    def get_file_category_data(self):
        
        file_extension = os.path.splitext(self.original_file)[1].lower()
        for category, info in FILE_CATELOG.items():
            if info["file_extension"] == file_extension:
                return FILE_CATELOG[category]
        return None



    def remove_editing_marker(self):
        marker_file = os.path.join(os.path.dirname(self.original_file), f"[{self.username}_editing]_{os.path.basename(self.original_file)}")
        def try_remove_marker():
            if os.path.exists(marker_file):
                try:
                    os.remove(marker_file)
                    print (" editing marker Removed")
                except Exception as e:
                    print(f"Error removing editing marker: {e}")
                    self.root.after(1000, try_remove_marker)

        try_remove_marker()

    def create_request_file(self):
        request_file_name = f"[{self.username}_requesting]_{os.path.basename(self.original_file)}"
        request_file_path = os.path.join(os.path.dirname(self.original_file), request_file_name)
        with open(request_file_path, "w") as f:
            f.write(f"Request to edit the file by {self.username}")
        print(f"Created request file: {request_file_path}")

    def check_request_files(self):
        request_users = []
        dir_name = os.path.dirname(self.original_file)
        for file in os.listdir(dir_name):
            if re.match(rf'\[(\w+)_requesting\]_{os.path.basename(self.original_file)}', file):
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
