import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import logging
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileOrganizerUI:
    def __init__(self, master):
        self.master = master
        self.master.title("File Organizer")
        self.master.geometry('400x400')  # Adjusted size for the new options

        # Define your root folder and study names
        self.ROOT_FOLDER = r"J:\1643\1_Presentation\01_P-Base\01_Base Renderings"
        self.STUDY_NAMES = [
            "angled_frame",
            "angled_frame_alt",
            "angled_frame_alt_alt",
            "sawtooth",
            "hori",
            "solar_panel",
            "offset_frame",
            "simple_punch"
        ]

        # Version selection variable
        self.version_var = tk.StringVar(value="glass version")  # Default selection

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        self.study_var = tk.StringVar(value=self.STUDY_NAMES[0])
        self.study_selection_frame = tk.Frame(self.master)  # Create a frame
        self.study_selection_frame.pack(pady=10)  # Pack the frame into the master window

        tk.Label(self.study_selection_frame, text="Select a Study Name:").pack()

        # Now, radio buttons will be packed inside this frame instead of directly in self.master
        for opt in self.STUDY_NAMES:
            rb = tk.Radiobutton(self.study_selection_frame, text=opt, variable=self.study_var, value=opt)
            rb.pack(anchor='w')  # Pack each radio button inside the frame

        ttk.Separator(self.master, orient='horizontal').pack(fill='x', pady=10)


        # Version selection UI
        tk.Label(self.master, text="Select Version:").pack()
        tk.Radiobutton(self.master, text="Glass Version", variable=self.version_var, value="glass version").pack()
        tk.Radiobutton(self.master, text="Chrome Version", variable=self.version_var, value="chrome version").pack()

        ttk.Separator(self.master, orient='horizontal').pack(fill='x', pady=10)


        action_btn = tk.Button(self.master, text="Relocate Images!", command=self.on_submit)
        action_btn.pack()

    def get_png_files(self, folder):
        return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.png')]

    def move_files_to_version_folder(self, study_name, files):
        target_folder = os.path.join(self.ROOT_FOLDER, study_name, self.version_var.get())
        logging.info("Would clear files in: {}".format(target_folder))
        for f in os.listdir(target_folder):
            os.remove(os.path.join(target_folder, f))
        logging.info("Would move files to: {}".format(target_folder))
        for file in files:
            shutil.move(file, target_folder)

    def on_submit(self):
        study_name = self.study_var.get()
        if not study_name:
            messagebox.showerror("Error", "Please select a study name")
            return
        latest_files = self.get_png_files(self.ROOT_FOLDER)
        if not latest_files:
            messagebox.showerror("Error", "No PNG files found in the root folder")
            return
        logging.info("Found PNG files: {}".format(latest_files))
        self.move_files_to_version_folder(study_name, latest_files)
        messagebox.showinfo("Success", "{} images relocated to {}.".format(len(latest_files), self.version_var.get()))


        # Reorder the STUDY_NAMES list
        if study_name in self.STUDY_NAMES:
            self.STUDY_NAMES.remove(study_name)
            self.STUDY_NAMES.append(study_name)

        # Update the UI to reflect the new order
        self.update_study_selection_ui()


    def update_study_selection_ui(self):
        # Clear the frame
        for widget in self.study_selection_frame.winfo_children():
            widget.destroy()

        # Recreate the label and radio buttons inside the frame
        tk.Label(self.study_selection_frame, text="Select a Study Name:").pack()

        for opt in self.STUDY_NAMES:
            rb = tk.Radiobutton(self.study_selection_frame, text=opt, variable=self.study_var, value=opt)
            rb.pack(anchor='w')  # Use anchor='w' to align the radio buttons to the left

def main():
    root = tk.Tk()
    app = FileOrganizerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
