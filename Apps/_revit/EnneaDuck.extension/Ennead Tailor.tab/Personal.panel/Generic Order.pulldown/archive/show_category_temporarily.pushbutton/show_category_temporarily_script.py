#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "for selected sheets, and selected categories, turn on the categories temperarly."
__title__ = "Show Category Temporarily"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


class Solution:
    def process_view(self, view):
        #print view.ViewType.ToString()
        if view.ViewType.ToString() in ["Schedule", "Legend", "Rendering", "ColumnSchedule"]:
            return

        print("\n\n Processing <{}>".format(view.Name))
        view.EnableTemporaryViewPropertiesMode(view.Id)

        to_be_hidden = False  # True
        status = "shown"  # "hidden"
        for cate in self.categories:
            if view.GetCategoryHidden (cate.Id) == to_be_hidden:
                print(cate.Name + " already " + status)
                continue
            try:
                view.SetCategoryHidden (cate.Id, to_be_hidden)
                print(cate.Name + " is now " + status)
            except:
                print("$$ Cannot turn on " + cate.Name)



    def show_category_temporarily(self):
        pass
        # get sheets
        sheets = forms.select_sheets()

        # get cateogry to turn on
        all_categories = [x for x in doc.Settings.Categories if ".dwg" not in x.Name.lower()]
        all_categories.sort(key = lambda x: x.Name)
        selected_categories = forms.SelectFromList.show(all_categories,
                                                multiselect = True,
                                                name_attr = "Name",
                                                title = "Pick categories that you want to process.",
                                                button_name = 'Select Categories to Turn On')

        if not selected_categories:
            return


        self.categories = selected_categories


        # get views on sheets
        views = []
        for sheet in sheets:
            views.extend([doc.GetElement(x) for x in sheet.GetAllPlacedViews()])




        t = DB.Transaction(doc, __title__)
        t.Start()
        # process view
        map(self.process_view, views)
        t.Commit()

 
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    Solution().show_category_temporarily()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







