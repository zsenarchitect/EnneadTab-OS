import threading
import time

import REVIT_EVENT
"""
Also make a versionfor Rhino maybe...
"""

"""the idea is simple, this contain a abstract class that can use to make a thread that attach any funcs. 
The args of the func might need to be stored in runtime sticky
it auto run every 2 seconds under revit. It is not a idle hook!
Probaly need to use external command.

some potential usage might be:
    - there is no post command hook, so this is helpful to catch any post stage changes and make action
    - pop ask if want to place new crated view at sheet(The is no post command hook so use this to monitor the creation of new view)


Intentionally not using args to pass around, becasue 
#1, there might be more func to bind, it might have overlapping keys in small risk
#2, script.get_evno_variable should use tiny memory, it is better to not allow it to avoid accidental huge memory usage

"""

class RevitUpdater:
    tasks = []
    """
    probally make more sense if register at startup.

    example:
    def my_func():
        doc = __revit__.ActiveUIDocument.Document # pyright: ignore
        if not doc:
            return
        all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).ToElements()
        print (len(all_sheets))
        
    updater = EnneadTab.REVIT.REVIT_AUTO.RevitUpdater(my_func)
    updater.start()
    """

    # check if passing func arg already exist in cls task, do not initate again if already exist


    
    def __init__(self, func, interval = 2, max_life = -1):
        if func.__name__ in RevitUpdater.tasks:
            print ("func {} already exist in RevitUpdater".format(func.__name__))
            return
        self.func = func #############!!!!!! this is not good, this means there are only one func allow to auto run. Need to upgrade to a dict toallow parrell run funcs. Need change to the runner logic as well.

        self.interval = interval
        self.max_life = max_life
        
        self.stop_flag = False
        self.starting_time = time.time()



        # register func
        self.registered_func_runner = REVIT_EVENT.ExternalEventRunner(self.func)


        RevitUpdater.tasks.append(func.__name__)
        


    def main_player(self):
        if self.max_life > 0:
            if time.time() - self.starting_time > self.max_life:
                self.stop_flag = True
                return

        # do not pass any args. just let the func figure out internally.
        self.registered_func_runner.run(self.func.__name__, )

        if not self.stop_flag:
            self.timer = threading.Timer(self.interval, self.main_player)
            self.timer.start()
        else:
            self.timer.cancel()
        
            #NOTIFICATION.messenger (main_text = "Monitor terminated.")

           
    def start(self): 
        
        self.timer = threading.Timer(0.1, self.main_player) # immediately call first action
        self.timer.start()

    def stop(self):
        self.stop_flag = True
