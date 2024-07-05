import os

directory = r'C:\Users\szhang\github\EnneadTab-OS\Apps\lib\EnneadTab'

for filename in os.listdir(directory):
    if filename.endswith('.PY') and filename != '__init__.py':
        # Capitalize the filename
        new_filename = filename.replace(".PY", ".py")
        # Rename the file
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
