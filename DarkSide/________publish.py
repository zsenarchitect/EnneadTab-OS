import os
import shutil
import datetime
import subprocess
import time
import traceback
import winsound
import threading
import sys
import tkinter as tk
import re



# Setup paths
OS_REPO_FOLDER = os.path.dirname(os.path.dirname(__file__))
sys.path.append(OS_REPO_FOLDER + "\\Apps\\lib\\EnneadTab")

import NOTIFICATION  # pyright: ignore
import SOUND  # pyright: ignore
import VERSION_CONTROL  # pyright: ignore
import ENVIRONMENT  # pyright: ignore

class NoGoodSetupException(Exception):
    def __init__(self):
        super().__init__("The setup is not complete or you are working on a new computer.")

# Locate Git executable
locations = [
    "{}\\Local\\Programs\\Git\\cmd\\git.exe".format(ENVIRONMENT.USER_APPDATA_FOLDER),
    "C:\\Program Files\\Git\\cmd\\git.exe"
]
for location in locations:
    if os.path.exists(location):
        GIT_LOCATION = location
        break
else:
    raise NoGoodSetupException()

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        blue_text = "\033[34m"
        reset_color = "\033[0m"
        print("\n\n{}Publish took {:.1f} seconds to complete.{}\n\n".format(blue_text, elapsed_time, reset_color))
        NOTIFICATION.duck_pop("Publish took {:.1f} seconds to complete.".format(elapsed_time))
        SOUND.play_sound("sound_effect_spring")
        return result
    return wrapper

def update_exes():
    sys.path.append(os.path.dirname(__file__) + "\\exes")
    from ExeMaker import recompile_exe  # pyright: ignore
    recompile_exe()

def copy_to_EA_Dist_and_commit():
    EA_dist_repo_folder = os.path.join(os.path.dirname(OS_REPO_FOLDER), "EA_Dist")
    for folder in ["Apps", "Installation"]:
        try_remove_content(os.path.join(EA_dist_repo_folder, folder))
        shutil.copytree(os.path.join(OS_REPO_FOLDER, folder), os.path.join(EA_dist_repo_folder, folder))
    commit_changes(EA_dist_repo_folder)
    reset_and_force_push(EA_dist_repo_folder)
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

def commit_changes(repository_path):
    try:
        os.chdir(repository_path)
        add_result = subprocess.call([GIT_LOCATION, "add", "."])
        if add_result != 0:
            raise Exception("Git add command failed with return code {}".format(add_result))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        commit_message = "Auto Commit {}".format(current_time)
        commit_result = subprocess.call([GIT_LOCATION, "commit", "-m", commit_message])
        if commit_result != 0:
            if commit_result == 1:
                print("No changes to commit.")
                return
            raise Exception("Git commit command failed with return code {}".format(commit_result))
        else:
            print("Git commit successful.")
    except Exception as e:
        print("An error occurred while committing changes")
        print(traceback.format_exc())
        raise e

def try_remove_content(folder_path):
    if os.path.exists(folder_path):
        if os.path.isfile(folder_path):
            os.remove(folder_path)
        else:
            shutil.rmtree(folder_path)

def get_nth_commit_number():
    result = subprocess.Popen([GIT_LOCATION, "log", "--since=midnight", "--oneline"], stdout=subprocess.PIPE)
    commits = result.stdout.readlines()
    return len(commits) + 1

def pull_changes_from_main(repository_path):
    try:
        os.chdir(repository_path)
        stash_result = subprocess.call([GIT_LOCATION, "stash"])
        if stash_result != 0:
            print("Warning: Git stash command failed, continuing with pull anyway.")
        pull_result = subprocess.call([GIT_LOCATION, "pull", "origin", "main"])
        if pull_result != 0:
            raise Exception("Git pull command failed with return code {}".format(pull_result))
        pop_result = subprocess.call([GIT_LOCATION, "stash", "pop"])
        if pop_result != 0:
            print("Warning: Git stash pop command failed with return code {}. Attempting to force stash.".format(pop_result))
            force_stash(repository_path)
    except Exception as e:
        print("An error occurred while pulling changes from the main branch")
        print(traceback.format_exc())
        raise e

def force_stash(repository_path):
    os.chdir(repository_path)
    subprocess.call([GIT_LOCATION, "stash", "push", "--include-untracked"])

def reset_and_force_push(repository_path):
    try:
        os.chdir(repository_path)
        reset_result = subprocess.call([GIT_LOCATION, "reset", "--hard"])
        if reset_result != 0:
            raise Exception("Git reset command failed with return code {}".format(reset_result))
        print("Current branch:\n", subprocess.run([GIT_LOCATION, "branch"], capture_output=True, text=True).stdout)
        print("Remote URL:\n", subprocess.run([GIT_LOCATION, "remote", "-v"], capture_output=True, text=True).stdout)
        push_result = subprocess.call([GIT_LOCATION, "push", "--force", "origin", "main"])
        if push_result != 0:
            raise Exception("Git push command failed with return code {}".format(push_result))
        else:
            print("Git push successful.")
    except Exception as e:
        print("An error occurred while force pushing changes to the main branch")
        print(traceback.format_exc())
        raise e

def copy_to_standalone_collection():
    print_title("\n\nBegin updating stand alone exe...\n")
    exe_product_folder = os.path.join(OS_REPO_FOLDER, "Apps", "lib", "ExeProducts")
    stand_alone_folder = "L:\\4b_Applied Computing\\EnneadTab-DB\\Stand Alone Tools"
    good_list = [
        "IndesignAccOpenner.exe",
        "AccFileOpenner.exe",
        "Pdf2OrderedJpgs.exe",
        "AvdResourceMonitor.exe",
        "AppStore.exe"
    ]
    for i, exe in enumerate([f for f in os.listdir(exe_product_folder) if f in good_list]):
        src_path = os.path.join(exe_product_folder, exe)
        dest_path = os.path.join(stand_alone_folder, exe)
        print("Copying {}/{} [{}] to standalone collection".format(i + 1, len(good_list), exe))
        try:
            if not os.path.exists(dest_path) or os.path.getmtime(src_path) > os.path.getmtime(dest_path):
                shutil.copy(src_path, dest_path)
                print("Successfully copied {} to standalone collection".format(exe))
            else:
                print("   - Skipped copying {} as it is up to date".format(exe))
        except Exception as e:
            print("Failed to copy {} to standalone collection: {}".format(exe, e))

def update_installer_folder_exes():
    print_title("\n\nBegin updating installation folder for public easy install...")
    installation_folder = os.path.join(OS_REPO_FOLDER, "Installation")
    for file in os.listdir(installation_folder):
        if file.endswith(".exe"):
            os.remove(os.path.join(installation_folder, file))
    app_list = [
        "EnneadTab_OS_Installer.exe",
        "EnneadTab_For_Revit_Installer.exe",
        "EnneadTab_For_Revit(Legacy)_Installer.exe",
        "EnneadTab_For_Revit_UnInstaller.exe",
        "RevitIniDeployer.exe",
        "AccFileOpenner.exe",
        "AppStore.exe"
    ]
    for i, file in enumerate(app_list):
        print("Copying {}/{} [{}] to EA_dist installer folder".format(i + 1, len(app_list), file))
        shutil.copy(os.path.join(OS_REPO_FOLDER, "Apps", "lib", "ExeProducts", file), os.path.join(OS_REPO_FOLDER, "Installation", file))

def remind_all_to_do_items():
    print_title("\n\nBegin scanning for 'to-do' items...")
    print('-' * 40)
    todo_pattern = re.compile(r'to-do', re.IGNORECASE)
    todo_count = 0
    current_file = os.path.abspath(__file__)

    def read_file(file_path):
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.readlines()
            except UnicodeDecodeError:
                continue
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()

    for root, dirs, files in os.walk(OS_REPO_FOLDER):
        dirs[:] = [d for d in dirs if d not in ['.venv', '.git']]
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.py') and file_path != current_file:
                lines = read_file(file_path)
                for i, line in enumerate(lines):
                    if todo_pattern.search(line):
                        todo_count += 1
                        start = max(i - 2, 0)
                        end = min(i + 3, len(lines))
                        print(f'File: {file_path}')
                        for j in range(start, end):
                            print(f'{j + 1}: {lines[j].rstrip()}')
                        print('-' * 40)
    red_color = "\033[91m"
    reset_color = "\033[0m"
    print(f'{red_color}Total "to-do" items found: {todo_count}\n When you have time you should review.{reset_color}')



class CompileConfirmation:
    def __init__(self):
        self.should_compile = False

    def get_result(self):
        self.root = tk.Tk()
        self.root.title("Compile Confirmation")
        window_width = 400
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
        self.label = tk.Label(self.root, text="", font=('Helvetica', 16))
        self.label.pack(pady=20)
        button_yes = tk.Button(self.root, text="Yes", font=('Helvetica', 16), command=self.on_yes)
        button_yes.pack(side="left", padx=20, pady=20)
        button_no = tk.Button(self.root, text="No", font=('Helvetica', 16), command=self.on_no)
        button_no.pack(side="right", padx=20, pady=20)
        self.countdown(15)
        self.root.mainloop()
        return self.should_compile

    def countdown(self, count):
        if count > 0:
            note = "default as Yes" if self.should_compile else "default as No"
            self.label['text'] = f"Do you want to compile the exe today?\n{note}\nTime remaining: {count} seconds"
            self.root.after(1000, self.countdown, count-1)
        else:
            self.root.quit()
            self.root.destroy()

    def on_yes(self):
        self.should_compile = True
        self.root.quit()
        self.root.destroy()

    def on_no(self):
        self.should_compile = False
        self.root.quit()
        self.root.destroy()

def print_title(text):
    large_text = "\033[1m" + text + "\033[0m"
    print(large_text)

def purge_by_extension():
    bad_extensions = [
        ".3dmbak",
        ".rui_bak"
        ]

    for folder, _, files in os.walk(OS_REPO_FOLDER):
        for file in files:
            for ext in bad_extensions:
                if file.endswith(ext):
                    os.remove(os.path.join(folder, file))

@time_it
def publish_duck():

    purge_by_extension()

    
    if ENVIRONMENT.IS_AVD:
        NOTIFICATION.messenger("Not going to publish from AVD...")
        return
    
    if CompileConfirmation().get_result():
        print_title("\n\nBegin compiling all exes...")
        NOTIFICATION.messenger("Recompiling all exes...kill VScode if you want to cancel..")
        update_exes()
    else:
        NOTIFICATION.messenger("NOT compiling exes today...")

        
    update_installer_folder_exes()

    
    import RuiWriter
    RuiWriter.run()

    
    print_title("\n\npush update to EA dist folder")
    copy_to_EA_Dist_and_commit()

    
    VERSION_CONTROL.update_EA_dist()

    
    remind_all_to_do_items()

    
    thread = threading.Thread(target=copy_to_standalone_collection)
    thread.start()

    
if __name__ == '__main__':
    publish_duck()
