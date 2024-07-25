import os
import shutil
import datetime
import subprocess
import time
import traceback
import winsound
import threading
import sys

OS_REPO_FOLDER = os.path.dirname(os.path.dirname(__file__))
sys.path.append(OS_REPO_FOLDER + "\\Apps\\lib\\EnneadTab")

import UNIT_TEST  # pyright: ignore
import NOTIFICATION  # pyright: ignore
import FOLDER  # pyright: ignore
import SOUND  # pyright: ignore
import VERSION_CONTROL  # pyright: ignore
import ENVIRONMENT  # pyright: ignore

class NoGoodSetupException(Exception):
    def __init__(self):
        super().__init__("The setup is not complete or you are working on a new computer.")

# Specify the absolute path to the git executable
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
        # ANSI escape codes for blue text with a white background
        blue_text = "\033[34m"
        reset_color = "\033[0m"

        # Print the formatted message with color
        print("{}Publish took {:.1f} seconds to complete.{}".format(blue_text, elapsed_time, reset_color))
        NOTIFICATION.duck_pop("Publish took {:.1f} seconds to complete.".format(elapsed_time))
        SOUND.play_sound("sound_effect_spring")

        return result
    return wrapper

def update_exes():
    sys.path.append(os.path.dirname(__file__) + "\\exes")
    from ExeMaker import recompile_exe  # pyright: ignore
    recompile_exe()

def copy_to_EA_Dist_and_commit():
    # locate the EA_Dist repo folder and current repo folder
    # the current repo folder is 3 parent folder up
    EA_dist_repo_folder = os.path.join(os.path.dirname(OS_REPO_FOLDER), "EA_Dist")

    # process those two folders "Apps" and "Installation"
    # in EA_Dist folder, delete folder, then copy folder from current repo to EA_dist repo
    for folder in ["Apps", "Installation"]:
        # delete folder in EA_dist repo if exist
        try_remove_content(os.path.join(EA_dist_repo_folder, folder))

        # copy folder from current repo to EA_dist repo
        shutil.copytree(os.path.join(OS_REPO_FOLDER, folder), os.path.join(EA_dist_repo_folder, folder))

    # Add and commit changes
    commit_changes(EA_dist_repo_folder)

    # Reset and force push to remote
    reset_and_force_push(EA_dist_repo_folder)

    # Play Windows built-in notification sound
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)


def commit_changes(repository_path):
    try:
        # Change to the Git repository directory
        print("Changing directory to:", repository_path)
        os.chdir(repository_path)

        # Add all changes
        print("Running git add .")
        add_result = subprocess.call([GIT_LOCATION, "add", "."])
        if add_result != 0:
            raise Exception("Git add command failed with return code {}".format(add_result))

        # Generate commit message with current date and time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        commit_message = "Auto Commit {}".format(current_time)
        print(f"Running git commit -m '{commit_message}'")
        commit_result = subprocess.call([GIT_LOCATION, "commit", "-m", commit_message])
        if commit_result != 0:
            if commit_result == 1:  # No changes to commit
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
    # Count the number of commits made today
    result = subprocess.Popen([GIT_LOCATION, "log", "--since=midnight", "--oneline"], stdout=subprocess.PIPE)
    commits = result.stdout.readlines()
    return len(commits) + 1

def pull_changes_from_main(repository_path):
    try:
        print("Changing directory to:", repository_path)
        os.chdir(repository_path)

        # Stash local changes
        print("Running git stash")
        stash_result = subprocess.call([GIT_LOCATION, "stash"])
        if stash_result != 0:
            print("Warning: Git stash command failed, continuing with pull anyway.")
            # Optionally handle this error differently or log it

        # Pull the latest changes from the main branch
        print("Running git pull origin main")
        pull_result = subprocess.call([GIT_LOCATION, "pull", "origin", "main"])
        if pull_result != 0:
            raise Exception("Git pull command failed with return code {}".format(pull_result))

        # Apply stashed changes
        print("Running git stash pop")
        pop_result = subprocess.call([GIT_LOCATION, "stash", "pop"])
        if pop_result != 0:
            print("Warning: Git stash pop command failed with return code {}. Attempting to force stash.".format(pop_result))
            force_stash(repository_path)

    except FileNotFoundError as e:
        print("FileNotFoundError: Ensure Git is installed and available in PATH")
        print(traceback.format_exc())
        raise e
    except Exception as e:
        print("An error occurred while pulling changes from the main branch")
        print(traceback.format_exc())
        raise e

def force_stash(repository_path):
    print("Forcefully stashing changes...")
    os.chdir(repository_path)
    # Stash changes forcibly by using the drop command if necessary
    subprocess.call([GIT_LOCATION, "stash", "push", "--include-untracked"])  # Use the appropriate flags as needed

def reset_and_force_push(repository_path):
    try:
        # Change to the Git repository directory
        print("Changing directory to:", repository_path)
        os.chdir(repository_path)

        # Reset the repository to the current state
        print("Running git reset --hard")
        reset_result = subprocess.call([GIT_LOCATION, "reset", "--hard"])
        if reset_result != 0:
            raise Exception("Git reset command failed with return code {}".format(reset_result))
        
        # Verify the current branch
        print("Verifying current branch")
        branch_result = subprocess.run([GIT_LOCATION, "branch"], capture_output=True, text=True)
        print("Current branch:\n", branch_result.stdout)
        
        # Verify the remote URL
        print("Verifying remote URL")
        remote_result = subprocess.run([GIT_LOCATION, "remote", "-v"], capture_output=True, text=True)
        print("Remote URL:\n", remote_result.stdout)

        # Force push to the main branch
        print("Running git push --force origin main")
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

    print_title("\n\nBegin updating stand alone exe...")
    exe_product_folder = OS_REPO_FOLDER + "\\Apps\\lib\\ExeProducts"
    stand_alone_folder = "L:\\4b_Applied Computing\\EnneadTab-DB\\Stand Alone Tools"

    good_list = [
        "IndesignAccOpenner.exe",
        "AccFileOpenner.exe"
    ]


    for i, exe in enumerate([f for f in os.listdir(exe_product_folder) if f in good_list]):
    
        print("Copying {}/{} [{}] to standalone collection".format(i+1,
                                                                    len(good_list),
                                                                    exe))
        try:
            shutil.copy(os.path.join(exe_product_folder, exe),
                        os.path.join(stand_alone_folder, exe))
        except:
            print ("Failed to copy {} to standalone collection".format(exe))

    
def update_installer_folder_exes():

    print_title("\n\nBegin updating installation folder for public easy install...")
    installation_folder = os.path.join(OS_REPO_FOLDER, "Installation")
    for file in os.listdir(installation_folder):
        if file.endswith(".exe"):
            os.remove(os.path.join(installation_folder, file))

    # copy folder from deep product folder to easy installation folder
    app_list = [
        "EnneadTab_OS_Installer.exe",
        "EnneadTab_For_Revit(Legacy)_Installer.exe",
        "EnneadTab_For_Revit_UnInstaller.exe",
        "RevitIniDeployer.exe",
        "AccFileOpenner.exe"
                 ]
    for i, file in enumerate(app_list):
        print("Copying {}/{} [{}] to EA_dist installer folder".format(i+1,
                                                                    len(app_list),
                                                                    file))
        shutil.copy(os.path.join(OS_REPO_FOLDER, "Apps", "lib", "ExeProducts", file),
                    os.path.join(OS_REPO_FOLDER, "Installation", file))

@time_it
def publish_duck():
    if manual_confirm_should_compile_exe():
        print_title("\n\nBegin compiling all exes...")
        NOTIFICATION.messenger("Recompiling all exes...kill VScode if you want to cancel..")
        update_exes()
    else:
        NOTIFICATION.messenger("NOT compiling exes today...")
    
    update_installer_folder_exes()

    # recompile the rui layout for rhino
    import RuiWriter
    RuiWriter.run()

    # print_title("Start testing all module.")
    # UNIT_TEST.test_core_module()

    print_title("\n\npush update to EA dist folder")
    copy_to_EA_Dist_and_commit()
    VERSION_CONTROL.update_EA_dist()

    
    thread = threading.Thread(target=copy_to_standalone_collection)
    thread.start()


def manual_confirm_should_compile_exe():
    """manua change date to see if I should recompile exe
    so each recompile is more intentional"""
    return str(datetime.date.today()) == "2024-07-25"

def print_title(text):
    # ANSI escape code for larger text
    large_text = "\033[1m" + text + "\033[0m"
    print(large_text)

if __name__ == '__main__':
    publish_duck()
