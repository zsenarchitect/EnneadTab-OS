__doc__ = "for every open document(except family document), it sync with central. Then Close"
__title__ = "Sync All Open Proj and Close"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=28744"
__tip__ = True


from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
from pyrevit import script

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def main():
    REVIT_APPLICATION.sync_and_close()
    import ENNEAD_LOG
    ENNEAD_LOG.use_enneadtab(coin_change = 30, tool_used = "Sync All Projs. and Close", show_toast = True)
    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)

################## main code below #####################
if __name__ == "__main__":
    main()