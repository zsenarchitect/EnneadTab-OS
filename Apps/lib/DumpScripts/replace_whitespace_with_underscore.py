import os

def replace_whitespace_with_underscore(directory):
    # List all files in the directory
    for filename in os.listdir(directory):
        # Check if there are any whitespaces in the filename
        if ' ' in filename:
            # Construct the old and new file paths
            old_file_path = os.path.join(directory, filename)
            new_file_name = filename.replace(' ', '_')
            new_file_path = os.path.join(directory, new_file_name)
            
            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f'Renamed: {old_file_path} -> {new_file_path}')

# Directory containing the files
directory = r'C:\Users\szhang\github\EnneadTab-OS\Apps\lib\EnneadTab\audios'

# Replace whitespaces with underscores in file names
replace_whitespace_with_underscore(directory)
