import psutil
import GPUtil
import time
import tkinter as tk
from PIL import Image, ImageTk
import socket
import os
import pystray
from pystray import MenuItem as item

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util

SETTINGS = {
    "cpu_threshold": 80,
    "gpu_threshold": 80,
    "user_threshold": 5,
    "uptime_threshold": 48 * 3600  # 48 hours in seconds
}

class UsageMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

        folder = os.path.dirname(os.path.abspath(__file__))
        self.icon_image_normal_path = os.path.join(folder, "normal_icon.ico")
        self.icon_image_alert_path = os.path.join(folder, "alert_icon.ico")
        self.icon_image_normal = Image.open(self.icon_image_normal_path)
        self.icon_image_alert = Image.open(self.icon_image_alert_path)

        self.status_window = None
        self.flashing = False

        self.cpu_usage = 0
        self.gpu_usage = 0

        self.tray_icon = None
        self.create_tray_icon()

    def create_tray_icon(self):
        menu = pystray.Menu(
            item("Status", self.show_status),
            item("Exit", self.exit_app)
        )
        self.tray_icon = pystray.Icon("UsageMonitor", self.icon_image_normal, "Usage Monitor", menu)
        self.tray_icon.run_detached()

        # Start updating usage in the main thread
        self.root.after(1000, self.update_usage)

    def exit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()

    def update_usage(self):
        self.cpu_usage = psutil.cpu_percent(interval=1)
        self.gpu_usage = self.get_gpu_usage()
        users = psutil.users()
        uptime_seconds = time.time() - psutil.boot_time()

        if (self.cpu_usage > SETTINGS["cpu_threshold"] or 
            self.gpu_usage > SETTINGS["gpu_threshold"] or
            len(users) > SETTINGS["user_threshold"] or
            uptime_seconds > SETTINGS["uptime_threshold"]):
            if not self.flashing:
                self.flashing = True
                self.flash_icon()
        else:
            self.flashing = False
            if self.tray_icon:
                self.tray_icon.icon = self.icon_image_normal

        if self.status_window is not None:
            self.update_status_window()

        self.root.after(1000, self.update_usage)

    def get_gpu_usage(self):
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]  # Assuming you have at least one GPU
            return gpu.load * 100
        return 0

    def flash_icon(self):
        if self.flashing:
            current_icon = self.tray_icon.icon
            if current_icon == self.icon_image_normal:
                self.tray_icon.icon = self.icon_image_alert
            else:
                self.tray_icon.icon = self.icon_image_normal
            self.root.after(200, self.flash_icon)  # Change icon every 200ms

    def show_status(self, icon=None, item=None):
        if self.status_window is None:
            self.status_window = tk.Toplevel(self.root)
            self.status_window.title("System Status")

            self.labels = {
                "pc_name": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left"),
                "num_users": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left"),
                "uptime": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left"),
                "cpu_usage": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left"),
                "gpu_usage": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left")
            }

            for label in self.labels.values():
                label.pack(padx=10, pady=2, fill='both', expand=True)

            self.status_window.protocol("WM_DELETE_WINDOW", self.close_status_window)

            self.update_status_window()

    def update_status_window(self):
        pc_name = socket.gethostname()
        users = psutil.users()
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_string = self.format_uptime(uptime_seconds)

        self.labels["pc_name"].config(text="PC Name: {}".format(pc_name))
        self.labels["num_users"].config(text="Number of Users: {}".format(len(users)))
        self.labels["uptime"].config(text="Uptime: {}".format(uptime_string))
        self.labels["cpu_usage"].config(text="Current CPU Usage: {:.2f}%".format(self.cpu_usage))
        self.labels["gpu_usage"].config(text="Current GPU Usage: {:.2f}%".format(self.gpu_usage))

        # Check thresholds and set colors independently
        self.set_label_color("cpu_usage", self.cpu_usage > SETTINGS["cpu_threshold"])
        self.set_label_color("gpu_usage", self.gpu_usage > SETTINGS["gpu_threshold"])
        self.set_label_color("num_users", len(users) > SETTINGS["user_threshold"])
        self.set_label_color("uptime", uptime_seconds > SETTINGS["uptime_threshold"])

    def set_label_color(self, label_name, condition):
        if condition:
            self.labels[label_name].config(fg="orange", font=("Helvetica", 12, "bold"))
        else:
            self.labels[label_name].config(fg="black", font=("Helvetica", 12))

    def close_status_window(self):
        self.status_window.destroy()
        self.status_window = None

    def format_uptime(self, seconds):
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return "{} days, {} hours, {} minutes, {} seconds".format(
            int(days), int(hours), int(minutes), int(seconds)
        )

    @_Exe_Util.try_catch_error
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = UsageMonitor()
    app.run()
