"""createa shortcut link at startup folder so it auto run at the start of login.
This will be helpful for AVD users."""
import os
import winshell

app = os.path.join(os.environ['USERPROFILE'], 
                   'Documents', 
                   'EnneadTab Ecosystem', 
                   'EA_Dist', 
                   'Installation', 
                   'EnneadTab_OS_Installer.exe')



if os.path.exists(app):

    startup_folder = os.path.join(os.environ['APPDATA'], 
                                  'Microsoft', 
                                  'Windows', 
                                  'Start Menu', 
                                  'Programs', 
                                  'Startup')
    shortcut_path = os.path.join(startup_folder, 'EnneadTab_OS_Installer.lnk')

    winshell.CreateShortcut(
        Path=shortcut_path,
        Target=app,
        Description='EnneadTab OS Installer'
    )