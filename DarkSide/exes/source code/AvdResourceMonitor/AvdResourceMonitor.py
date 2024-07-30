import psutil
import time
import tkinter as tk
from PIL import Image, ImageTk
import socket
import os
import pystray
from pystray import MenuItem as item
import logging
import sys
import threading
from py3nvml.py3nvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlShutdown
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import _Exe_Util
import _GUI_Base_Util

# Set up logging
desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
log_file = os.path.join(desktop_path, 'logging.txt')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

DEFAULT_SETTINGS = {
    "cpu_threshold": 80,
    "gpu_threshold": 80,
    "disk_threshold": 80,
    "memory_threshold": 75,
    "user_threshold": 5,
    "uptime_threshold": 48 * 3600  # 48 hours in seconds
}

AVD_MONITOR_SETTING_FILE = "avd_monitor_settings.sexyDuck"
SETTINGS = _Exe_Util.get_data(AVD_MONITOR_SETTING_FILE) or DEFAULT_SETTINGS

class UsageMonitor(_GUI_Base_Util.BaseGUI):
    def __init__(self):
        self.app_title = "AVD Resource Monitor"
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

        folder = os.path.dirname(os.path.abspath(__file__))
        self.icon_image_normal_path = os.path.join(folder, "normal_icon.ico")
        self.icon_image_alert_path = os.path.join(folder, "alert_icon.ico")
        self.icon_image_normal = Image.open(self.icon_image_normal_path)
        self.icon_image_alert = Image.open(self.icon_image_alert_path)
        self.root.iconbitmap(self.icon_image_normal_path)  # Set window icon

        self.status_window = None
        self.settings_window = None
        self.pc_name = socket.gethostname()
        self.flashing = False

        self.cpu_usage = 0
        self.gpu_usage = 0
        self.disk_usage = 0
        self.memory_usage = 0

        nvmlInit()  # Initialize NVML for GPU monitoring

        self.tray_icon = None
        self.create_tray_icon()

        # Track start time
        self.start_time = time.time()

    def create_tray_icon(self):
        menu = pystray.Menu(
            item("AVD Resource Status", self.show_status),
            item("Settings", self.show_settings),
            pystray.Menu.SEPARATOR,
            item("Exit", self.exit_app)
        )

        self.tray_icon = pystray.Icon("AVD Usage Monitor", self.icon_image_normal, "Usage Monitor", menu)

        def on_clicked(icon, item):
            self.show_status()

        self.tray_icon.menu = menu
        self.tray_icon.icon = self.icon_image_normal
        self.tray_icon.title = "Usage Monitor"
        self.tray_icon.run_detached()

        # Start updating usage in the main thread
        self.root.after(1000, self.update_usage)

    def exit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        nvmlShutdown()  # Shutdown NVML

    def update_usage(self):
        self.cpu_usage = psutil.cpu_percent(interval=1)
        self.gpu_usage = self.get_gpu_usage()
        self.disk_usage = self.get_disk_usage()
        self.memory_usage = self.get_memory_usage()
        self.users = psutil.users()
        self.uptime_seconds = time.time() - psutil.boot_time()

        if (self.cpu_usage > SETTINGS["cpu_threshold"] or 
            self.gpu_usage > SETTINGS["gpu_threshold"] or
            self.disk_usage > SETTINGS["disk_threshold"] or
            self.memory_usage["percent"] > SETTINGS["memory_threshold"] or
            len(self.users) > SETTINGS["user_threshold"] or
            self.uptime_seconds > SETTINGS["uptime_threshold"]):
            if not self.flashing:
                self.flashing = True
                self.flash_icon()
        else:
            self.flashing = False
            if self.tray_icon:
                self.tray_icon.icon = self.icon_image_normal

        if self.status_window is not None:
            self.update_status_window()

        # Log status
        status_message = self.get_status_message()
        logging.info(status_message)

        # Check if MAX_LIFE exceeded
        self.check_max_life()

        self.root.after(1000, self.update_usage)

    def get_gpu_usage(self):
        try:
            device_count = nvmlDeviceGetCount()
            if device_count > 0:
                handle = nvmlDeviceGetHandleByIndex(0)  # Assuming monitoring the first GPU
                utilization = nvmlDeviceGetUtilizationRates(handle)
                return utilization.gpu
        except Exception as e:
            logging.error("Failed to get GPU usage: {}".format(e))
        return 0

    def get_disk_usage(self):
        disk_usage = psutil.disk_usage('C:')
        return disk_usage.percent

    def get_memory_usage(self):
        memory_info = psutil.virtual_memory()
        return {"percent": memory_info.percent, "used_gb": memory_info.used / (1024 ** 3)}

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
            self.status_window.configure(bg='#2e2e2e')
            self.status_window.iconbitmap(self.icon_image_normal_path)

            self.labels = {
                "pc_name": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left", bg='#2e2e2e', fg='white'),
                "num_users": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left", bg='#2e2e2e', fg='white'),
                "uptime": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left", bg='#2e2e2e', fg='white'),
                "cpu_usage": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left", bg='#2e2e2e', fg='white'),
                "gpu_usage": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left", bg='#2e2e2e', fg='white'),
                "disk_usage": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left", bg='#2e2e2e', fg='white'),
                "memory_usage": tk.Label(self.status_window, text="", font=("Helvetica", 12), anchor="w", justify="left", bg='#2e2e2e', fg='white')
            }

            for label in self.labels.values():
                label.pack(padx=10, pady=2, fill='both', expand=True)

            self.status_window.protocol("WM_DELETE_WINDOW", self.close_status_window)

            self.update_status_window()

    def update_status_window(self):
        uptime_string = self.format_uptime(self.uptime_seconds)
        memory_usage_info = "{:.1f} GB ({:.2f}%)".format(self.memory_usage["used_gb"], self.memory_usage["percent"])

        self.labels["pc_name"].config(text="PC Name: {}".format(self.pc_name))
        self.labels["num_users"].config(text="Number of Users: {}".format(len(self.users)))
        self.labels["uptime"].config(text="Uptime: {}".format(uptime_string))
        self.labels["cpu_usage"].config(text="Current CPU: {:.2f}%".format(self.cpu_usage))
        self.labels["gpu_usage"].config(text="Current GPU: {:.2f}%".format(self.gpu_usage))
        self.labels["disk_usage"].config(text="C: Drive Usage: {:.2f}%".format(self.disk_usage))
        self.labels["memory_usage"].config(text="Memory Usage: {}".format(memory_usage_info))

        # Check thresholds and set colors independently
        self.set_label_color("cpu_usage", self.cpu_usage > SETTINGS["cpu_threshold"])
        self.set_label_color("gpu_usage", self.gpu_usage > SETTINGS["gpu_threshold"])
        self.set_label_color("disk_usage", self.disk_usage > SETTINGS["disk_threshold"])
        self.set_label_color("memory_usage", self.memory_usage["percent"] > SETTINGS["memory_threshold"])
        self.set_label_color("num_users", len(self.users) > SETTINGS["user_threshold"])
        self.set_label_color("uptime", self.uptime_seconds > SETTINGS["uptime_threshold"])

    def get_status_message(self):
        uptime_string = self.format_uptime(self.uptime_seconds)
        memory_usage_info = "{:.1f} GB ({:.2f}%)".format(self.memory_usage["used_gb"], self.memory_usage["percent"])
        return (
            "PC Name: {}\n"
            "Number of Users: {}\n"
            "Uptime: {}\n"
            "Current CPU: {:.2f}%\n"
            "Current GPU: {:.2f}%\n"
            "C: Drive Usage: {:.2f}%\n"
            "Memory Usage: {}"
        ).format(self.pc_name, len(self.users), uptime_string, self.cpu_usage, self.gpu_usage, self.disk_usage, memory_usage_info)

    def set_label_color(self, label_name, condition):
        if condition:
            self.labels[label_name].config(fg="orange", font=("Helvetica", 12, "bold"))
        else:
            self.labels[label_name].config(fg="white", font=("Helvetica", 12))

    def close_status_window(self):
        self.status_window.destroy()
        self.status_window = None

    def show_settings(self, icon=None, item=None):
        if self.settings_window is None:
            self.settings_window = tk.Toplevel(self.root)
            self.settings_window.title("Settings")
            self.settings_window.iconbitmap(self.icon_image_normal_path)  # Set window icon
            self.settings_window.configure(bg='#2e2e2e')

            self.settings_vars = {
                "cpu_threshold": tk.IntVar(value=SETTINGS["cpu_threshold"]),
                "gpu_threshold": tk.IntVar(value=SETTINGS["gpu_threshold"]),
                "disk_threshold": tk.IntVar(value=SETTINGS["disk_threshold"]),
                "memory_threshold": tk.IntVar(value=SETTINGS["memory_threshold"]),
                "user_threshold": tk.IntVar(value=SETTINGS["user_threshold"]),
                "uptime_threshold": tk.IntVar(value=SETTINGS["uptime_threshold"] // 3600)  # Display in hours
            }

            row = 0
            for key, var in self.settings_vars.items():
                label_text = key.replace("_", " ").capitalize()
                if key == "uptime_threshold":
                    label_text += " (hours)"
                if key in ["cpu_threshold", "gpu_threshold", "disk_threshold", "memory_threshold"]:
                    label_text += " (%)"
                if key in ["cpu_threshold", "gpu_threshold"]:
                    label_text = label_text.upper()
                label = tk.Label(self.settings_window, text=label_text, anchor="w", justify="left", bg='#2e2e2e', fg='white')
                label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
                entry = tk.Entry(self.settings_window, textvariable=var, bg='#2e2e2e', fg='white')
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
                row += 1

            tk.Button(self.settings_window, text="Save", command=self.save_settings, bg='#2e2e2e', fg='white').grid(row=row, column=0, columnspan=2, pady=10)
            self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings_window)

    def save_settings(self):
        new_settings = {key: var.get() for key, var in self.settings_vars.items()}
        new_settings["uptime_threshold"] *= 3600  # Convert back to seconds

        SETTINGS.update(new_settings)
        _Exe_Util.set_data(SETTINGS, AVD_MONITOR_SETTING_FILE)

        logging.info("Settings updated: {}".format(SETTINGS))
        self.close_settings_window()

    def close_settings_window(self):
        self.settings_window.destroy()
        self.settings_window = None

    def format_uptime(self, seconds):
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        
        uptime_string = []
        if days > 0:
            uptime_string.append("{} days".format(int(days)))
        if hours > 0 or days > 0:
            uptime_string.append("{} hours".format(int(hours)))
        uptime_string.append("{} minutes".format(int(minutes)))
        uptime_string.append("{} seconds".format(int(seconds)))
        
        return ", ".join(uptime_string)

    def check_max_life(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.MAX_LIFE:
            logging.info("Maximum life exceeded. Shutting down the application.")
            self.exit_app()

    @_Exe_Util.try_catch_error
    def run(self):
        if self.is_another_app_running():
            self.root.destroy()
            return
        self.root.mainloop()


if __name__ == "__main__":
    app = UsageMonitor()
    app.run()
