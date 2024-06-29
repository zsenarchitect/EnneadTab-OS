
#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import time
import threading

"""
'{:02d}' means minimal 2 digit long, use 0 at left padding.
For 4 digit number like years, this has no effect
"""

def get_YYYYMMDD():
    """2023-02-17 output as 230217"""
    now = datetime.datetime.now()
    year, month, day = '{:02d}'.format(now.year), '{:02d}'.format(now.month), '{:02d}'.format(now.day)

    return "{}{}{}".format(year, month, day)

def get_YYYY_MM_DD():
    """2023-02-17 output as 2023-02-17"""
    now = datetime.datetime.now()
    year, month, day = '{:02d}'.format(now.year), '{:02d}'.format(now.month), '{:02d}'.format(now.day)

    return "{}-{}-{}".format(year, month, day)

def get_date_as_tuple(return_string = True):
    """2023-02-17 output as (2023,02,17)"""
    now = datetime.datetime.now()
    year, month, day = '{:02d}'.format(now.year), '{:02d}'.format(now.month), '{:02d}'.format(now.day)
    if return_string:return year, month, day
    return int(year), int(month), int(day)

def timer(func):
    def wrapper(*args, **kwargs):
        time_start = time.time()
        out = func(*args, **kwargs)
        used_time = time.time() - time_start
        try:
            print ("Function: {} use {}".format(func.__name__, get_readable_time(used_time)))
        except:
            print (used_time)
        return out
    return wrapper


def get_formatted_current_time():
    """-->2023-05-16_11-33-55"""
    now = datetime.datetime.now()
    return get_formatted_time(now)


def get_formatted_time(input_time):
    #  if input is float, convert to datetime object first:
    if isinstance(input_time, float):
        input_time = datetime.datetime.fromtimestamp(input_time)
    
    year, month, day = '{:02d}'.format(input_time.year), '{:02d}'.format(input_time.month), '{:02d}'.format(input_time.day)
    hour, minute, second = '{:02d}'.format(input_time.hour), '{:02d}'.format(input_time.minute), '{:02d}'.format(input_time.second)
    return "{}-{}-{}_{}-{}-{}".format(year, month, day, hour, minute, second)

def get_readable_time(time_in_seconds):
    
    time_in_seconds = int(time_in_seconds)
    if time_in_seconds < 60:
        return "{}s".format(time_in_seconds)
    if time_in_seconds < 3600:
        mins = int(time_in_seconds/60)
        secs = time_in_seconds%60
        return "{}m {}s".format(mins, secs)
    
    
    # hours = int(time_in_seconds/3600)
    # mins = time_in_seconds%60
    # secs = time_in_seconds%60
    
    hours = time_in_seconds // 3600
    mins = (time_in_seconds % 3600) // 60
    secs = time_in_seconds % 60
    return "{}h {}m {}s".format(hours, mins, secs)



def time_has_passed_too_long(unix_time, tolerence = 60 * 30):
    "tolerence in seconds, default 60s x 30 = 30mins"
    import time
    current_time = time.time()
    try:
        if float(current_time) - float(unix_time) > tolerence:
            return True
        return False
    except Exception as e:
        # print ("Failed becasue: {}".format(e) )
        return False


class AutoTimer:
    def __init__(self, life_span, show_progress = False, interval = 1):
        """
        args:
        """
        self.life_span = life_span
        self.max_repetition = life_span / interval
        self.current_count = self.max_repetition
        self.timer = None
        self.interval = interval
        self.show_progress = show_progress

    def on_timed_event(self):
        if self.show_progress:
            print ("{}/{}".format(int(self.current_count), int(self.max_repetition )))



        self.current_count -= 1
        #print("The Elapsed event was raised at", datetime.datetime.now())

        if self.current_count > 0:

            self.timer = threading.Timer(self.interval, self.on_timed_event)
            self.timer.start()
        else:
            print("Timer stopped after", self.life_span, "seconds")
            self.stop_timer()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()

    def begin(self):
        print("Timer begins!")
        self.timer = threading.Timer(self.interval, self.on_timed_event)
        self.timer.start()
        #print(self.timer.is_alive())



def get_revit_uptime():
    import ENVIRONMENT
    if not ENVIRONMENT.is_Revit_environment():
        return "Not in Revit"
    from pyrevit.coreutils import envvars
    if not envvars.get_pyrevit_env_var("APP_UPTIME"):
        update_revit_uptime()
    uptime = time.time() - envvars.get_pyrevit_env_var("APP_UPTIME")
    uptime = get_readable_time(uptime)
    return uptime


def update_revit_uptime():
    from pyrevit.coreutils import envvars
    envvars.set_pyrevit_env_var("APP_UPTIME", time.time())

def unit_test():

    print ("Current Revit UpTime = {}".format(get_revit_uptime()))
        
    print ("Current Time = {}".format(get_formatted_current_time()))

if __name__ == "__main__":
    timer_example = AutoTimer(life_span=10,
                              show_progress=True,
                              interval= 0.1)
    timer_example.begin()

