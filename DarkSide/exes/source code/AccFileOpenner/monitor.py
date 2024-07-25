import os
import re

class FolderMonitor:
    def __init__(self, acc_folder):
        self.acc_folder = acc_folder

    def update_editing_and_requesting_files(self):
        editing_files = []
        requesting_files = []
        for root, dirs, files in os.walk(self.acc_folder):
            if "_D" in root or "_C" in root:
                continue
            for file in files:
                if re.match(r'\[\w+_editing\]', file):
                    editing_files.append(os.path.join(root, file))
                elif re.match(r'\[\w+_requesting\]', file):
                    requesting_files.append(os.path.join(root, file))
        return editing_files, requesting_files
