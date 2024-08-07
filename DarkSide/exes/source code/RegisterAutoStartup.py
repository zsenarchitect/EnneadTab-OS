import os
import winshell
import subprocess
import ctypes
import sys
import _Exe_Util  # Assuming _Exe_Util contains the try_catch_error decorator

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_shortcut(app_path, shortcut_name, description):
    startup_folder = os.path.join(os.environ['APPDATA'], 
                                  'Microsoft', 
                                  'Windows', 
                                  'Start Menu', 
                                  'Programs', 
                                  'Startup')
    shortcut_path = os.path.join(startup_folder, "{}.lnk".format(shortcut_name))

    winshell.CreateShortcut(
        Path=shortcut_path,
        Target=app_path,
        Description=description
    )

    print('Shortcut created successfully in the startup folder.')

def schedule_task(task_name, app_path, interval_minutes):
    cmd = 'schtasks /create /f /tn "{}" /tr "{}" /sc minute /mo {}'.format(task_name, app_path, interval_minutes)
        
    if is_admin():
        cmd += ' /rl highest'
    else:
        print('User does not have administrative rights. Scheduling task without admin privileges...')
        

    try:
        subprocess.run(cmd, check=True, shell=True)
        print('Task scheduled successfully to run every {} minutes.'.format(interval_minutes))
    except subprocess.CalledProcessError as e:
        print('Failed to schedule the task. Error:', e)

@_Exe_Util.try_catch_error
def main():
    app = os.path.join(os.environ['USERPROFILE'], 
                       'Documents', 
                       'EnneadTab Ecosystem', 
                       'EA_Dist', 
                       'Installation', 
                       'EnneadTab_OS_Installer.exe')

    if os.path.exists(app):
        create_shortcut(app, 'EnneadTab_OS_Installer', 'EnneadTab OS Installer Auto Run At The Login')

        schedule_task('EnneadTab_OS_Installer_Task', app, 30)

    else:
        print('Application not found at:', app)

if __name__ == "__main__":
    main()
