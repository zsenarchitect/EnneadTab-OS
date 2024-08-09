import traceback
import requests
import zipfile
import os
import shutil
import time
from datetime import datetime, timedelta

import _Exe_Util

class RepositoryUpdater:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.extract_to = _Exe_Util.ESOSYSTEM_FOLDER

        if not os.path.exists(_Exe_Util.ESOSYSTEM_FOLDER):
            os.makedirs(_Exe_Util.ESOSYSTEM_FOLDER)
        if not os.path.exists(_Exe_Util.DUMP_FOLDER):
            os.makedirs(_Exe_Util.DUMP_FOLDER) 
            
        self.final_folder_name = self.extract_repo_name(repo_url)
        self.final_dir = os.path.join(self.extract_to, self.final_folder_name)
        
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.zip_path = os.path.join(self.extract_to, f"repo_{self.timestamp}.zip")
        self.temp_dir = os.path.join(self.extract_to, f"temp_extract_{self.timestamp}")

    def extract_repo_name(self, url):
        if '/archive/' in url:
            parts = url.split('/')
            repo_index = parts.index('archive') - 1
            return parts[repo_index]
        return "Repository"
    
    def run_update(self):
        try:
            self.download_zip()
            self.extract_zip()
            self.update_files()
            self.cleanup_current_cache()
            self.cleanup_empty_EA_dist_folder()
            self.create_duck_file(success=True)
            self.cleanup_old_duck_files()
            self.cleanup_old_download_cache()
        except Exception as e:
            self.create_duck_file(success=False, error_details=traceback.format_exc())
            # raise e

    
    def download_zip(self):
        response = requests.get(self.repo_url, stream=True)
        if response.status_code == 200:
            wait = 0
            while wait < 10:
                if os.path.exists(self.zip_path):
                    break
                time.sleep(1)
                wait += 1
            with open(self.zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Zip file downloaded successfully.")
        else:
            raise Exception("Failed to download the repository. Status code: {}".format(response.status_code))
    
    def extract_zip(self):
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        self.source_dir = os.path.join(self.temp_dir, os.listdir(self.temp_dir)[0])
        print("Zip file extracted.")
    
    def update_files(self):
        if not os.path.exists(self.final_dir):
            os.makedirs(self.final_dir)
        
        # Force copy everything over
        source_files = {os.path.join(dp, f): os.path.relpath(os.path.join(dp, f), self.source_dir) for dp, dn, filenames in os.walk(self.source_dir) for f in filenames}
        for src_path, rel_path in source_files.items():
            tgt_path = os.path.join(self.final_dir, rel_path)
            os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
            try:
                shutil.copy2(src_path, tgt_path)
            except:
                # often OS_installer exe will fail to override becasue it is still runing by pther process.
                pass
            
        # Delete files older than 2 day
        now = time.time()
        file_age_threshold = now - 2 * 24 * 60 * 60
        for dp, dn, filenames in os.walk(self.final_dir):
            for f in filenames:
                file_path = os.path.join(dp, f)
                if os.stat(file_path).st_mtime < file_age_threshold:
                    os.remove(file_path)
                    try:
                        os.rmdir(dp)  # Attempt to remove the directory if empty
                    except OSError:
                        pass
        print("Files have been updated.")
    
    def cleanup_current_cache(self):
        shutil.rmtree(self.temp_dir)
        os.remove(self.zip_path)
        print("Cleanup current cache download completed.")

    def cleanup_empty_EA_dist_folder(self):
        ea_dist_folder = os.path.join(_Exe_Util.ESOSYSTEM_FOLDER, "EA_Dist")
        """walk thru all the folder, remove if it is a empty folder"""
        for folder, _, filenames in os.walk(ea_dist_folder):
            if not filenames:
                try:
                    os.removedirs(folder)
                except:
                    pass
        print("Cleanup empty EA folder completed.")
            
    def create_duck_file(self, success=True, error_details=None):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        duck_file_path = os.path.join(_Exe_Util.ESOSYSTEM_FOLDER, f"{timestamp}.duck")
        if not success:
            duck_file_path = os.path.join(_Exe_Util.ESOSYSTEM_FOLDER, f"{timestamp}_ERROR.duck")
        with open(duck_file_path, 'w') as f:
            if success:
                f.write("success")
            else:
                f.write("Failed update.\nTraceback details:\n{}".format(error_details))
        print("Duck file created: {}".format(duck_file_path))
    
    def cleanup_old_duck_files(self):
        now = datetime.now()
        cutoff = now - timedelta(hours=8)
        for f in os.listdir(_Exe_Util.ESOSYSTEM_FOLDER):
            if f.endswith(".duck"):
                file_path = os.path.join(_Exe_Util.ESOSYSTEM_FOLDER, f)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff:
                    os.remove(file_path)
                    print("Old duck file removed: {}".format(file_path))


    def cleanup_old_download_cache(self):
        for file in os.listdir(self.extract_to):
            if file.startswith("repo_") and file.endswith(".zip"):
                #  if older than 1 days, remove
                file_path = os.path.join(self.extract_to, file)
                file_timestamp = os.path.getmtime(file_path)
                if datetime.fromtimestamp(file_timestamp) < datetime.now() - timedelta(days=1):
                    os.remove(file_path)
                    print("Old zip file removed.")

            # if it is a folder start with temp_extract and it is older than 1 days
            if os.path.isdir(os.path.join(self.extract_to, file)) and file.startswith("temp_extract_"):
                file_path = os.path.join(self.extract_to, file)
                file_timestamp = os.path.getmtime(file_path)
                if datetime.fromtimestamp(file_timestamp) < datetime.now() - timedelta(days=1):
                    shutil.rmtree(file_path)
                    print("Old temp folder removed.")

# do not need to try catch error becasue the error is record in ERROR_DUCK file.
# @_Exe_Util.try_catch_error
def main():
    repo_url = "https://github.com/zsenarchitect/EA_Dist/archive/refs/heads/master.zip"

    updater = RepositoryUpdater(repo_url)
    updater.run_update()

if __name__ == '__main__':
    main()
