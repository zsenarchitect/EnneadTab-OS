import tkinter as tk
from tkinter import ttk
import os
import time
import shutil
import _Exe_Util



class BaseGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.configure(bg='white')
        self.overrideredirect(True)  # Remove window decorations

        self.rounded_corners()
        self.center_window()
        self.bind_events()

    def rounded_corners(self):
        self.canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', self.create_rounded_rectangle)

    def create_rounded_rectangle(self, event=None):
        self.canvas.delete("all")
        self.canvas.create_rectangle(10, 10, self.winfo_width()-10, self.winfo_height()-10, outline="white", width=2, fill="white")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = event.x_root - self._x
        y = event.y_root - self._y
        self.geometry("+{}+{}".format(x, y))

    def stop_move(self, event):
        self._x = None
        self._y = None

class App(BaseGUI):
    def __init__(self, exe_folder, *args, **kwargs):
        BaseGUI.__init__(self, *args, **kwargs)
        self.exe_folder = exe_folder
        self.title("EnneadTab App Store")
        self.geometry("400x350")

        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.canvas, text="Available Apps", background="white")
        self.label.pack(pady=10)

        self.exe_list = tk.Listbox(self.canvas)
        self.exe_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.populate_list()

        self.start_button = ttk.Button(self.canvas, text="Open App", command=self.start_selected)
        self.start_button.pack(pady=10)

        self.close_button = ttk.Button(self.canvas, text="Close", command=self.close_window)
        self.close_button.pack(pady=10)

    def populate_list(self):
        for exe in os.listdir(self.exe_folder):
            if exe.endswith(".exe") and "_temp_" not in exe:
                self.exe_list.insert(tk.END, exe)

    def start_selected(self):
        selected_exe = self.exe_list.get(tk.ACTIVE)
        if selected_exe:
            exe_path = os.path.join(self.exe_folder, selected_exe)
            self.safe_open(exe_path)

    def safe_open(self, path):
        # Placeholder for the safe-opening method from the main lib
        print("Opening:", path)
        exe_name = os.path.basename(path)
        temp_exe_name = "_temp_exe_{}_{}.exe".format(exe_name, int(time.time()))
        temp_exe = _Exe_Util.DUMP_FOLDER + "\\" + temp_exe_name
        shutil.copyfile(path, temp_exe)
        os.startfile(temp_exe)
        for file in os.listdir(_Exe_Util.DUMP_FOLDER):
            if file.startswith("_temp_exe_"):
                try:
                    os.remove(os.path.join(_Exe_Util.DUMP_FOLDER, file))
                except:
                    pass

    def close_window(self):
        self.destroy()

if __name__ == "__main__":
    exe_folder = os.path.join(_Exe_Util.ESOSYSTEM_FOLDER, 'EA_Dist', 'Apps', "lib", "ExeProducts")
    app = App(exe_folder)
    app.mainloop()
