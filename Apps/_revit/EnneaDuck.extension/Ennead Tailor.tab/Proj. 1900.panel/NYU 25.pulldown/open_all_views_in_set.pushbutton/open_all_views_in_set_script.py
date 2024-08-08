#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Open Favorite Views by Set"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error
def open_all_views_in_set():
    all_view_sheet_sets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheetSet).ToElements()



    # let user pick multuple sheetsets
    selected_print_sets = forms.SelectFromList.show(all_view_sheet_sets,
                                                    multiselect=True,
                                                    name_attr='Name',
                                                    button_name='Select Print Sets',
                                                    title = "Who are the next sexy views to open?")
    if not selected_print_sets:
        return

    for print_set in selected_print_sets:
        views = sorted(list(print_set.Views), key = lambda x: x.Name)
        for i, view in enumerate(views):
            NOTIFICATION.messenger("Openning <{}/{}>[{}] in the background, hold on...".format(i, len(views), view.Name))
            try:
                REVIT_APPLICATION.get_uidoc().ActiveView = view
            except Exception as e:
                NOTIFICATION.messenger(str(e))

                
    try:
        REVIT_APPLICATION.get_uidoc().ActiveView = views[0]
    except Exception as e:
        NOTIFICATION.messenger(str(e))


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    open_all_views_in_set()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







