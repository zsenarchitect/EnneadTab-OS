#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "TO-DO: this has potential, should revisit when there is a demand"
__title__ = "Floor Drafter"

from pyrevit import forms #
from pyrevit import script #

import traceback
import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

app = __revit__.Application





class Solution:
    def __init__(self):
        pass

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def main(self):


        opts = ["Revit Floor --> Rhino Brep",
                "Rhino Brep --> Revit Floor"]
        res = EnneadTab.REVIT.REVIT_FORMS.dialogue(options = opts, main_text = "What do you want to do?")
        if res == opts[0]:
            T = DB.TransactionGroup(doc, "Floor2Brep")
            T.Start()
            self.revit_to_rhino()
            T.Commit()
        elif res == opts[1]:
            self.rhino_to_revit()


    def revit_to_rhino(self):

        selection = EnneadTab.REVIT.REVIT_SELECTION.pick_elements(prompt = 'Pick floors in view to export')
        #print selection[0].Category.Name
        floors = filter(lambda x: x.Category.Name == "Floors", selection)
        data = dict()

        for floor in floors:
            t = DB.Transaction(doc, "make view")
            t.Start()
            doc.ActiveView.IsolateElementsTemporary(EnneadTab.DATA_CONVERSION.list_to_system_list([floor.Id]))
            doc.ActiveView.ConvertTemporaryHideIsolateToPermanent()

            data["id"] = floor.UniqueId
            setting_name = EnneadTab.REVIT.REVIT_SELECTION.get_export_setting(doc, setting_name = None, return_name = True) 
            EnneadTab.REVIT.REVIT_EXPORT.export_dwg(doc.ActiveView, floor.UniqueId , EnneadTab.FOLDER.get_EA_local_dump_folder(), dwg_setting_name = setting_name, is_export_view_on_sheet = False)
            t.RollBack()


        EnneadTab.DATA_FILE.save_dict_to_json_in_dump_folder(data, "FLOOR2BREP_DATA.json")


            
  



    def helper(self):

        file = EnneadTab.FOLDER.get_EA_dump_folder_file("FLOOR2BREP_DATA.json")
        data = EnneadTab.DATA_FILE.read_json_as_dict(file)


        floor_type_name = layer_name.split("OUT")[1]
        type = EnneadTab.REVIT.REVIT_SELECTION.pick_system_type(doc, system_type = "floor", type_name = floor_type_name)
        print(type)

        t = DB.Transaction(doc, __title__)

        t.Start()

        for layer_name, brep_data in data.items():
            
            solution.main(layer_name, brep_data)
        t.Commit()



   
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":


    Solution().main()
    EnneadTab.SOUNDS.play_sound("sound effect_mario message.wav")
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)



