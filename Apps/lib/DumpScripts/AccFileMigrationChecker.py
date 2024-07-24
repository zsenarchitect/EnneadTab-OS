import os
import asyncio
import winsound
from tqdm import tqdm
from colorama import Fore, Style

class ACCMigrationChecker:
    def __init__(self, drive, prefix, limit):
        self.drive = drive
        self.prefix = prefix
        self.limit = limit

    def get_job_folders(self):
        """Get main job folders in the drive"""
        return sorted([os.path.join(self.drive, f) for f in os.listdir(self.drive) if os.path.isdir(os.path.join(self.drive, f))])

    async def check_path_length(self, job_folder):
        """Check if any file path will exceed the limit after adding the prefix"""
        affected_files = []
        file_paths = []
        
        # Collect all file paths first to get the correct count
        for root, dirs, files in os.walk(job_folder):
            for file in files:
                file_paths.append(os.path.join(root, file))
        
        # Use tqdm for the progress bar with custom color and style
        with tqdm(total=len(file_paths), desc=Fore.GREEN + f"Checking files in {os.path.basename(job_folder)}" + Style.RESET_ALL, unit="file", bar_format="{l_bar}{bar:20}{r_bar}{bar:-10b}") as pbar:
            for original_path in file_paths:
                new_path = os.path.join(self.prefix, original_path.replace(":", "").replace("\\", "_"))
                # Replace double backslashes with a single backslash to mimic Windows OS behavior
                new_path = new_path.replace("\\\\", "\\")
                if len(new_path) > self.limit:
                    affected_files.append((original_path, new_path))
                pbar.update(1)
        
        return affected_files

    def generate_report_content(self, job_folder, affected_files):
        """Generate report content for the job folder"""
        report_content = []
        if affected_files:
            summary = f"Summary: {len(affected_files)} files will be affected.\n"
            report_content.append(summary)
            details_header = "Details of affected files:\n"
            report_content.append(details_header)
            for original, new in affected_files:
                detail = f"Original: {original}\nNew: {new}\nLength: {len(new)}\n"
                report_content.append(detail)
        else:
            summary = f"Summary: All paths are below {self.limit} length limit.\n"
            report_content.append(summary)
        return "\n".join(report_content)

    def save_text_report(self, job_folder, report_content, status):
        """Save a text report for the job folder"""
        job_number = os.path.basename(job_folder)
        report_folder = "L:\\4b_Applied Computing\\EnneadTab-DB\\ACC Report"
        if not os.path.exists(report_folder):
            os.makedirs(report_folder)
        
        txt_filename = f"Acc Migration Filepath Length PreCheck [{job_number}]_{status}.txt"
        txt_output_path = os.path.join(report_folder, txt_filename)
        
        # Remove old reports with the same job number
        for file in os.listdir(report_folder):
            if file.startswith(f"Acc Migration Filepath Length PreCheck [{job_number}]_"):
                os.remove(os.path.join(report_folder, file))
        
        # Save the new text report
        with open(txt_output_path, 'w') as f:
            f.write(report_content)

        print(f"Generated text report: {txt_output_path}")
        # Play Windows system alert sound
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

async def process_drive(drive, prefix, limit):
    checker = ACCMigrationChecker(drive, prefix, limit)
    job_folders = checker.get_job_folders()

    for job_folder in job_folders:
        affected_files = await checker.check_path_length(job_folder)
        report_content = checker.generate_report_content(job_folder, affected_files)
        status = "bad" if affected_files else "good"
        checker.save_text_report(job_folder, report_content, status)
    
    if not job_folders:
        print(f"No job folders found in {drive}.")

if __name__ == "__main__":
    prefix = "C:\\Users\\SAMPLE.USERNAME\\DC\\ACCDocs\\Ennead Architects LLP\\"
    limit = 240

    drives = ["J:\\", "I:\\"]

    async def main():
        tasks = [process_drive(drive, prefix, limit) for drive in drives]
        await asyncio.gather(*tasks)

    asyncio.run(main())
