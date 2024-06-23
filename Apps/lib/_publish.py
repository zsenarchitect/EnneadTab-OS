"""To be run in VSCode"""
import os
import shutil
import datetime
import subprocess
import time
import winsound

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
        return result
    return wrapper


@time_it
def publish_duck():

    # locate the EA_Dist repo folder and current repo folder
    # the current repo folder is 3 parent folder up
    current_repo_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EA_dist_repo_folder = os.path.join(os.path.dirname(current_repo_folder), "EA_Dist")
    # print (current_repo_folder)
    # print (EA_dist_repo_folder)



    #  process those two folders "Apps" and "Installation"
    # in EA_Dist folder, delete folder, then copy folder from current repo to EA_dist repo
    for folder in ["Apps", "Installation"]:
        # delete folder in EA_dist repo if exist
        try_remove_folder(os.path.join(EA_dist_repo_folder, folder))
   
        # copy folder from current repo to EA_dist repo
        shutil.copytree(os.path.join(current_repo_folder, folder), os.path.join(EA_dist_repo_folder, folder))


        # delete folder called "DuckMaker.extension"
        try_remove_folder(os.path.join(EA_dist_repo_folder, folder, "_revit", "DuckMaker.extension"))


    # push EA_dist to update branch
    push_changes_to_main(EA_dist_repo_folder)



    # Play Windows built-in notification sound
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)


def try_remove_folder(folder_path):

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


def get_nth_commit_number():
    # Count the number of commits made today
    result = subprocess.Popen(["git", "log", "--since=midnight", "--oneline"], stdout=subprocess.PIPE)
    commits = result.stdout.readlines()
    return len(commits) + 1

    
def push_changes_to_main(repository_path):

    # Change to the Git repository directory
    os.chdir(repository_path)

    # Stage all changes
    subprocess.call(["git", "add", "."])

    commit_number = get_nth_commit_number()

    # Commit with today's date
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    commit_message = "Auto push changes committed on {}...{}".format(current_date, commit_number)
    subprocess.call(["git", "commit", "-m", commit_message])

    # Push to the main branch
    subprocess.call(["git", "push", "origin", "main"])




if __name__ == '__main__':
    publish_duck()