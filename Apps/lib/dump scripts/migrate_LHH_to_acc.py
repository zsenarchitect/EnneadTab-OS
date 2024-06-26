import os
import shutil
from tqdm import tqdm

J_DRIVE_ACC_FOLDER = "J:\\1643"
LHH_ACC_FOLDER = "C:\\Users\\szhang\\DC\\ACCDocs\\Ennead Architects LLP\\1643_LHH\\Project Files\\00_1643 LHH"

def main():
    # Collect all jpg files and their paths
    jpg_files = []
    for root, dirs, files in os.walk(J_DRIVE_ACC_FOLDER):
        for file in files:
            if file.lower().endswith('.jpg') or True:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, J_DRIVE_ACC_FOLDER)
                destination_dir = os.path.join(LHH_ACC_FOLDER, relative_path)
                destination_file = os.path.join(destination_dir, file)
                jpg_files.append((source_file, destination_file))

    # Copy files with progress bar
    for source_file, destination_file in tqdm(jpg_files, desc="Copying files"):
        # Create directories in the destination path if they don't exist
        destination_dir = os.path.dirname(destination_file)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # Copy the file to the destination directory
        shutil.copy2(source_file, destination_file)

if __name__ == "__main__":
    main()
