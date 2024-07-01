
__alias__ = "ListenToMiro"
__doc__ = "Listen to changes in the miro"


import os
import threading
import EnneadTab
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
import traceback
import System # pyright: ignore



"""the miro app should save in json every 1 sec at a location
the display pipline will listen to this json to unpack, try threading so do not rely on movemovement

"""
def try_catch_error(func):
    
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:
            error = traceback.format_exc()
            print (error)
          
    return wrapper

class RhinoMiroListener_Conduit(EnneadTab.RHINO.RHINO_CONDUIT.RhinoConduit):
    def __init__(self):

        self.life_span = 30
        self.interval = 1
        self.board_name = "TBD"
        
        self.max_repetition = self.life_span / self.interval
        self.current_count = self.max_repetition
        self.timer = None
        self.show_progress = True

        self.default_color = rs.CreateColor([87, 85, 83])


    @try_catch_error
    def on_timed_event(self):
        # if self.show_progress:
        #     print ("{}/{}".format(int(self.current_count), int(self.max_repetition )))

        # self.show_text_with_pointer(self.e, "A::::showing  " + str(self.current_count), 20)
            # self.DrawOverlay(self.e)

            
        EnneadTab.EXE.open_exe("MIRO_Headless")
        rs.Redraw()

       
        self.current_count -= 1
        # print("The Elapsed event was raised at", datetime.datetime.now())

        if self.current_count > 0:

            self.timer = threading.Timer(self.interval, self.on_timed_event)
            self.timer.start()
        else:
            print("Timer stopped after", self.life_span, "seconds")
            self.stop_timer()
            self.Enabled = False

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()

    def begin(self):
        print("Timer begins!")
        self.timer = threading.Timer(self.interval, self.on_timed_event)
        self.timer.start()
        #print(self.timer.is_alive())

    @try_catch_error
    def show_text_with_pointer(self, e, text, size, color = None, is_middle_justified = False):
        if not color:
            color = self.default_color

        position_X_offset = 500
        position_Y_offset = 100
        bounds = e.Viewport.Bounds
        if not hasattr(self, 'pointer_2d'):
            self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)
        
        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)
        self.pointer_2d += Rhino.Geometry.Vector2d(0, size*1.1 )

    @try_catch_error
    def myDrawOverlay(self, e):

        #print self.e
        self.show_text_with_pointer(e, "B showing{}".format(int(self.current_count)), 20)


    @try_catch_error
    def DrawForeground(self, e):


        position_X_offset = 20
        position_Y_offset = 40
        bounds = e.Viewport.Bounds
        self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)


        title = "Ennead Miro Listener"
        if self.board_name != "":
            title += ": {}".format(self.board_name)
        self.show_text_with_pointer(e,
                                    text = title,
                                    size = 30)

     
        self.show_text_with_pointer(e,
                                    text = "Left click icon again to leave room.",
                                    size = 15)
        self.show_text_with_pointer(e,
                                    text = "Right click to push select rhino element to miro.",
                                    size = 15)
        self.show_text_with_pointer(e,
                                    text = "Lat Update Timestamp: {}".format(EnneadTab.TIME.get_formatted_current_time()),
                                    size = 15)
        return
        self.pointer_2d += Rhino.Geometry.Vector2d(0, 20)
        pt0 = System.Drawing.Point(self.pointer_2d[0], self.pointer_2d[1] )
        pt1 = System.Drawing.Point(self.pointer_2d[0] + 500, self.pointer_2d[1] )

        e.Display.Draw2dLine(pt0, pt1, self.default_color, 5)

        self.pointer_2d += Rhino.Geometry.Vector2d(0, 20)
        for file in sorted(self.session_links.keys()):

            user = file.replace(".3dm", "")
            self.show_text_with_pointer(e,
                                        text = user,
                                        size = 15,
                                        color = self.color_lookup[user] )



        
def listen_to_miro():

    key = "RECENT_MIRO_URL_RHINO"
    recent_url = EnneadTab.DATA_FILE.get_revit_ui_setting_data(key_defaule_value=(key,"https://miro.com/app/board/uXjVNsgWNfA=/"))
    miro_url = rs.StringBox(
        message = "Please input the Miro board URL:",
        default_value= recent_url,
        title = "Listen To Miro")

    print ("Miro URL: " + miro_url)
    EnneadTab.DATA_FILE.set_revit_ui_setting_data(key, miro_url)

    with EnneadTab.DATA_FILE.update_data("miro.json") as data:
        data['url'] = miro_url
        data["app"] = "rhino_listener"
        data["frequency"] = 1

    


    timer_example = RhinoMiroListener_Conduit()
    timer_example.Enabled = True
    timer_example.begin()
#################
if __name__ == "__main__":
    listen_to_miro()

