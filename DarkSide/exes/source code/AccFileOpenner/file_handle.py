import os
import re
import shutil
import time

class FileHandler:
    def __init__(self, username, acc_folder):
        self.username = username
        self.acc_folder = acc_folder
        self.original_file = None
        self.desktop_file = None
        self.lock_file = None
        self.finished_button = None

    def process_file(self, file_path, callback):
        self.original_file = file_path
        print(f"Processing file: {self.original_file}")

        if self.check_self_editing():
            return "Warning: You are already editing this file. Will not attempt to open twice."

        self.copy_file_to_desktop()
        callback(self.desktop_file)  # Open the file on desktop
        self.cleanup_old_request_files()
        current_editor = self.check_existing_editors()
        if current_editor:
            self.create_request_file()
            return f"Warning: This file is currently edited by {current_editor}."
        self.create_editing_marker()
        return None

    def copy_file_to_desktop(self):
        file_name = os.path.basename(self.original_file)
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        self.desktop_file = os.path.join(desktop_path, file_name)
        shutil.copy2(self.original_file, self.desktop_file)

    def get_lock_file(self, file_category_data):
        lock_file_extension = file_category_data["lock_file_extension"]
        lock_file_begin_template = file_category_data["lock_file_begin_template"]
        base_name = os.path.basename(self.desktop_file)
        lock_file_begin = lock_file_begin_template.format(base_name.replace(file_category_data["file_extension"], ""))

        if lock_file_extension is None:
            return None

        for f in os.listdir(os.path.dirname(self.desktop_file)):
            if f.endswith(lock_file_extension) and f.lower().startswith(lock_file_begin.lower()):
                print(f"File lock found: {f}")
                self.lock_file = os.path.join(os.path.dirname(self.desktop_file), f)
                return self.lock_file
        print("File lock not found")
        return None

    def check_self_editing(self):
        file_name = os.path.basename(self.original_file)
        dir_name = os.path.dirname(self.original_file)
        for file in os.listdir(dir_name):
            if re.match(rf'\[{self.username}_editing\]_{file_name}', file):
                return True
        return False

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

    def create_editing_marker(self):
        file_name = os.path.basename(self.original_file)
        marker_file = os.path.join(os.path.dirname(self.original_file), f"[{self.username}_editing]_{file_name}")
        with open(marker_file, "w") as f:
            f.write(f"This file is currently being edited by {self.username}.")
        print(f"Created editing marker: {marker_file}")

    def create_request_file(self):
        request_file_name = f"[{self.username}_requesting]_{os.path.basename(self.original_file)}"
        request_file_path = os.path.join(os.path.dirname(self.original_file), request_file_name)
        with open(request_file_path, "w") as f:
            f.write(f"Request to edit the file by {self.username}")
        print(f"Created request file: {request_file_path}")

    def copy_back_to_original(self):
        print(f"Copying back to original: {self.desktop_file} to {self.original_file}")
        shutil.copy2(self.desktop_file, self.original_file)
        os.remove(self.desktop_file)
        self.remove_editing_marker()

    def remove_editing_marker(self):
        marker_file = os.path.join(os.path.dirname(self.original_file), f"[{self.username}_editing]_{os.path.basename(self.original_file)}")

        def try_remove_marker():
            if os.path.exists(marker_file):
                try:
                    os.remove(marker_file)
                    print("Editing marker removed")
                except Exception as e:
                    print(f"Error removing editing marker: {e}")
                    time.sleep(1)
                    try_remove_marker()

        try_remove_marker()
