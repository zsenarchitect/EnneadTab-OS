__doc__ = "for every open document(except family document), it sync with central"
__title__ = "Sync All\nOpen Proj"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28744"
__tip__ = True
from pyrevit import  script


from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import SOUNDS

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
################## main code below #####################
if __name__ == "__main__":
    
    import ENNEAD_LOG
    ENNEAD_LOG.use_enneadtab(coin_change = 25, tool_used = "Sync All Projs.", show_toast = True)
    REVIT_APPLICATION.sync_and_close(close_others = False)
    SOUNDS.play_sound()
    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)
