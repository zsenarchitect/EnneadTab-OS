__description__ = """
demo video, no audio: https://www.youtube.com/watch?v=2Sb3At124AY
 
Main problem:
Indesign only understand .idlk file extension as lock, but ACC Desktop Connector ignore .idlk file for syncing.
 
Result:
Multiple users could unintentionally open/save same indesign file over acc folder and override.
 
Alternative solution:
Customized locker file system that acc desktop connector can sync. 
When other user is editing, you cannot open same file, but can place request.
The request will be converted to edit lock when original editor leave the document AND if you want to edit the document.
All lock and request file will be generated/cleaned automatically by toolbox.
Please keep it running in the background. Close only after you close the indesign document.
 
What if one of the team member is not using this toolbox to open files?
He will not be able to quickly generate a lock file to stop other people from opening same file. He and other people are at rick overriding.
BUT you don't need this tool to see the other lock/request file. Those are natively visible in any file explorer window.
"""

import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import traceback
import time
import threading
import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util
EXPIRATION_DATE = datetime.date(2025, 1, 1)


class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg='#2e2e2e')

        self.update_title_with_days_left()

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

    def update_title_with_days_left(self):
        today = datetime.date.today()
        days_left = (EXPIRATION_DATE - today).days
        if days_left <= 0:
            self.root.title("InDesign File Opener - Tool Expired")
        elif days_left <= 30:
            self.root.title(f"InDesign File Opener - {days_left} days left")
        else:
            self.root.title("InDesign File Opener")

    def create_widgets(self):
        self.logo_label = tk.Label(self.root, image=self.logo_photo, bg='#2e2e2e')
        self.logo_label.grid(row=0, column=0, columnspan=3)

        self.pick_file_button = tk.Button(self.root, text="Pick InDesign File From ACC Connector", command=self.pick_file, bg='#2e2e2e', fg='white')
        self.pick_file_button.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.indesign_version_label = tk.Label(self.root, text="InDesign Version:", bg='#2e2e2e', fg='white')
        self.indesign_version_label.grid(row=2, column=1, padx=10, pady=10)

        self.indesign_version_entry = tk.Entry(self.root)
        self.indesign_version_entry.insert(0, "2024")
        self.indesign_version_entry.grid(row=3, column=1, padx=10, pady=10)

        self.selected_file_label = tk.Label(self.root, text="", bg='#2e2e2e', fg='white')
        self.selected_file_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.process_button = tk.Button(self.root, text="Open ACC InDesign Safety", command=self.process_file, bg='#2e2e2e', fg='white')
        self.process_button.grid(row=5, column=0, columnspan=3, padx=10, pady=20)
        self.process_button.config(state=tk.DISABLED)

        self.warning_frame = tk.Frame(self.root, bg='#2e2e2e')
        self.warning_label = tk.Label(self.warning_frame, text="", bg='#2e2e2e', fg='red', font=("Helvetica", 16, "bold"))
        self.warning_label.pack(padx=20, pady=20)


        self.request_users_label = tk.Label(self.warning_frame, text="", bg='#2e2e2e', fg='white')
        self.request_users_label.pack(padx=20, pady=20)

        self.warning_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
        self.warning_frame.grid_remove()  # Initially hide the frame

        self.note = tk.Label(self.root, text="Only close this toolbox after indesign document closed.\nIt is OK to minimize.", bg='#2e2e2e', fg='white', font=("Helvetica", 12))
        self.note.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        note = """Features:
1. Open ACC InDesign safely by setting customized locker file.
2. Other user can see who is editing the file, and place request to open.
3. When previous editor relinquish, requster can convert request lock to edit lock.
4. The cleanup of locker files and request files are done automatically over ACC drive.
"""
        self.note2 = tk.Label(self.root, text=note, bg='#2e2e2e', fg='white', font=("Helvetica", 8), justify='left')
        self.note2.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.copy_right = tk.Label(self.root, text="CopyRight @ 2024 By Ennead Architects", bg='#2e2e2e', fg='white', font=("Helvetica", 6))
        self.copy_right.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

        # Center the widgets
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)


    @_Exe_Util.try_catch_error
    def rotate_logo(self, event):
        max_rotation = 20
        width = self.root.winfo_width()
        relative_x = event.x / width
        angle = (relative_x * 2 - 1) * max_rotation
        angle = max(min(angle, max_rotation), -max_rotation)
        rotated_image = self.logo_image.rotate(angle)
        self.logo_photo = ImageTk.PhotoImage(rotated_image)
        self.logo_label.configure(image=self.logo_photo)

    @_Exe_Util.try_catch_error
    def pick_file(self):
        today = datetime.date.today()
        if (EXPIRATION_DATE - today).days <= 0:
            messagebox.showerror("Error", "Your tool has expired.")
            return
        
        file = filedialog.askopenfilename(filetypes=[("InDesign files", "*.indd")])
        self.selected_file = file
        if file:
            self.selected_file_label.config(text=f"Selected File: {os.path.basename(file)}")
            self.process_button.config(state=tk.NORMAL)
    
    @_Exe_Util.try_catch_error
    def process_file(self):
        original_file = self.selected_file
        if not original_file:
            messagebox.showwarning("Warning", "Please select an InDesign file.")
            return
        
        username = os.getenv('USERNAME')  # Get current user's name
        file_name = os.path.basename(original_file)
        prefix = "[{}_editing]_".format(username)

        
        for file in os.listdir(os.path.dirname(original_file)):
            #  cleanup files reuqested by this user
            search = re.match(r'\[{}_requesting\]_{}'.format(username, file_name), file)
            if search:
                os.remove(os.path.join(os.path.dirname(original_file), file))


            # Check if the file is being edited by other
            search = re.match(r'\[(\w+)_editing\]_{}'.format(file_name), file)
            if search:
                existing_user = search.group(1)
                self.create_request_file(username, original_file)
                messagebox.showwarning("Warning", f"This file is currently edited by {existing_user}.\n\nA request file has been placed.")
                return


        
        self.indesign_version = self.indesign_version_entry.get()

        acc_marker_file = os.path.join(os.path.dirname(original_file), "{}{}".format(prefix, file_name))
        acc_marker_file = acc_marker_file.replace("\\", "/")

        # even it is a txt file, still use .indd as extension so openning file dialog can it see there is such lock
        with open(acc_marker_file, "w") as f:
            f.write("This file is currently being edited by " + username + ".")
        
        # Show the warning frame
        self.show_warning_frame(username)

        # Wait until desktop copy ready
        desktop_file = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', os.path.basename(original_file))
        shutil.copy(original_file, desktop_file)
        while True:
            if os.path.exists(desktop_file):
                print ("desktop file copied")
                break
            time.sleep(1)

        indesign_script_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', "EnneadTab_Magic.jsx")
        with open(indesign_script_path, "w") as script_file:
            script_file.write(self.generate_indesign_script(desktop_file))


        # Run open_indesign in a separate thread
        indesign_thread = threading.Thread(target=self.open_indesign, args=(indesign_script_path,))
        indesign_thread.start()

        # Wait until file to open
        max_wait = 90
        wait = 0
        while wait<max_wait:
            native_indesign_locker_file = self.get_locker_file(desktop_file)
            if native_indesign_locker_file:
                print ("lock file found, document has open")
                break
            time.sleep(1)
            wait += 1
            print ("waiting")

        if wait == max_wait: return
            

        # Wait until file closed
        while True:
            if not os.path.exists(native_indesign_locker_file):
                print ("lock file removed, document has been closed")
                break
            time.sleep(1)
            request_users = self.check_request_files(original_file)
            if request_users:
                self.show_warning_frame(username, request_users)

        shutil.copy(desktop_file, original_file)
        print ("copy back to ACC")

        os.remove(desktop_file)
        print ("remove desktop file")

        for _ in range(10):
            os.remove(acc_marker_file)
            print ("try remove marker file: " + acc_marker_file)
            if not os.path.exists(acc_marker_file):
                break
            time.sleep(2)

        # Hide the warning frame
        self.hide_warning_frame()

    def get_locker_file(self, desktop_path):
        for file in os.listdir(os.path.dirname(desktop_path)):
            # ~monday~jsjvbp.idlk
            if not file.endswith(".idlk"):
                continue

            if file.lower().startswith("~" + os.path.basename(desktop_path).replace(".indd", "").lower()):
                return os.path.join(os.path.dirname(desktop_path), file)
            print (file)
        return None

    def create_request_file(self, username, original_file):
        request_file_name = "[{}_requesting]_{}".format(username, os.path.basename(original_file))
        request_file_path = os.path.join(os.path.dirname(original_file), request_file_name)
        with open(request_file_path, "w") as f:
            f.write("Request to edit the file by " + username)

    def check_request_files(self, original_file):
        request_users = []
        for file in os.listdir(os.path.dirname(original_file)):
            if re.match(r'\[(\w+)_requesting\]_{}'.format(os.path.basename(original_file)), file):
                request_users.append(file.split('_')[0][1:])  # Extract username from file name
        return request_users

    def generate_indesign_script(self, desktop_path):
        desktop_path = desktop_path.replace("\\", "/")
        return """
app.open("{}");
""".format(desktop_path)
    
    def open_indesign(self, script_path):
        vbs_content = """
Set app = CreateObject("InDesign.Application.{version}")
app.DoScript "{script_path}", 1246973031
""".format(version=self.indesign_version, script_path=script_path.replace("\\", "\\\\"))
        vbs_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', "EnneadTab_Magic.vbs")
        with open(vbs_path, "w") as f:
            f.write(vbs_content)
        
        subprocess.call(["wscript", vbs_path])

    def show_warning_frame(self, editing_user, requesting_users=None):
        self.warning_label.config(text="{} is editing, DO NOT CLOSE THIS TOOLBOX UNTIL YOU HAVE CLOSED INDESIGN\nOk to minimize it though.".format(editing_user))
        self.warning_frame.grid()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))

        if requesting_users:
            self.request_users_label.config(text="Requesting Users: " + ", ".join(requesting_users))

    def hide_warning_frame(self):
        self.warning_frame.grid_remove()
        self.request_users_label.config(text="")

@_Exe_Util.try_catch_error
def main():
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
