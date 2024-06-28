import os
import shutil
from tqdm import tqdm #pyright: ignore

J_DRIVE_ACC_FOLDER = "J:\\1643"
LHH_ACC_FOLDER = "C:\\Users\\szhang\\DC\\ACCDocs\\Ennead Architects LLP\\1643_LHH\\Project Files\\00_1643 LHH"

IGNORE_TYPE_TYPE = [".3dmbak"]
def main():
    # Collect all jpg files and their paths
    work_files = []
    for root, dirs, files in os.walk(J_DRIVE_ACC_FOLDER):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in IGNORE_TYPE_TYPE:
                continue
            
            source_file = os.path.join(root, file)
            relative_path = os.path.relpath(root, J_DRIVE_ACC_FOLDER)
            destination_dir = os.path.join(LHH_ACC_FOLDER, relative_path)
            destination_file = os.path.join(destination_dir, file)
            work_files.append((source_file, destination_file))

    # Copy files with progress bar
    for source_file, destination_file in tqdm(work_files, desc="Copying files"):
        # Create directories in the destination path if they don't exist
        destination_dir = os.path.dirname(destination_file)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # Copy the file to the destination directory
        shutil.copy2(source_file, destination_file)

if __name__ == "__main__":
    main()
