#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "List selected detail items to a dump drafting view."
__title__ = "List\nDetail Items"


import os
# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
from EnneadTab import NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_VIEW, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore
# from rpw.db import family 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

LIST_VIEW = "EnneadTab_Detail Item Dump"


class Deployer:
    def __init__(self, view, families, tag_family):
        self.view = view
        self.families = families
        # self.textnote_type = textnote_type
        self.tag_symbol = doc.GetElement(list(tag_family.GetFamilySymbolIds())[0])
        if not self.tag_symbol.IsActive:
            self.tag_symbol.Activate()

        self.pointer = DB.XYZ(0, 0, 0)



        for i, family in enumerate(families):
            NOTIFICATION.messenger("{}/{}: [{}]".format(i+1, len(families), family.Name))
            self.deploy_family(family)
            


    def step_right(self, x):
        self.pointer = self.pointer.Add(DB.XYZ(x, 0, 0))

    def step_down(self, y):
        self.pointer = self.pointer.Add(DB.XYZ(0, -y, 0))


    def reset_x(self):
        self.pointer = DB.XYZ(0, self.pointer.Y, 0)




    def deploy_family(self, family):
        if family.FamilyPlacementType != DB.FamilyPlacementType.ViewBased:
            return

        self.reset_x()
  
        max_h = -1
        min_gap = 1
        for type_id in family.GetFamilySymbolIds():
            # print (self.pointer)
            family_type = doc.GetElement(type_id)

            if not family_type.IsActive:
                family_type.Activate()

            instance = doc.Create.NewFamilyInstance(self.pointer, family_type, self.view)
            doc.Regenerate()


            # get rough 2D boundingbox
            self.view.IsolateElementTemporary (instance.Id)
            uidoc.ShowElements(instance)
            doc.Regenerate()
            bbox = self.view.Outline
            if not bbox:
                print ("no bbox for {}".format(instance))
                continue
            size_x = bbox.Max.U - bbox.Min.U
            size_y = bbox.Max.V - bbox.Min.V
            size_x, size_y = size_x * self.view.Scale, size_y * self.view.Scale
            max_h = max(max_h, size_y)
            self.view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate )



            
            DB.ElementTransformUtils.MoveElement(doc, instance.Id, DB.XYZ(size_x/2, size_y/2, 0))


            # add textnote
            # note = "[{}]\n{}".format(family.Name, family_type.LookupParameter("Type Name").AsString())

            # textnote_option = DB.TextNoteOptions()
            # textnote_option.HorizontalAlignment = DB.HorizontalTextAlignment.Center
            # textnote_option.TypeId = self.textnote_type.Id
            # DB.TextNote.Create(doc, 
            #                    self.view.Id, 
            #                    self.pointer.Add(DB.XYZ(size_x/2, -min_gap * 0.5, 0)), 
            #                    note, 
            #                    textnote_option)



            # add tag
            tag = DB.IndependentTag.Create(doc, 
                                            self.tag_symbol.Id, 
                                            self.view.Id, 
                                            DB.Reference(instance),
                                            True,
                                            DB.TagOrientation .Horizontal,
                                            self.pointer.Add(DB.XYZ(size_x/2, -min_gap * 0.2, 0)))

            DB.ElementTransformUtils.MoveElement(doc, tag.Id, self.view.ViewDirection + DB.XYZ(size_x/2, 0, 0)) # this force tag to regenreate graphic
            

            self.step_right(size_x * 1.2)

        self.step_down(max(min_gap, max_h*2))


            

            


        
        

    
@ERROR_HANDLE.try_catch_error()
def list_detail_items():
    detail_families = REVIT_SELECTION.pick_detail_componenet(multi_select=True)


    if not detail_families:
        return

    # textnote_type = REVIT_SELECTION.pick_textnote_type()
    # if not textnote_type:
    #     return

    view = REVIT_VIEW.get_view_by_name(LIST_VIEW)

    if not view:
        t = DB.Transaction(doc, "Make new view: " + LIST_VIEW)
        t.Start()
        view = DB.ViewDrafting.Create(doc, REVIT_VIEW.get_default_view_type("drafting").Id)
        view.Name = LIST_VIEW
        view.Scale = 2
        t.Commit()

    uidoc.ActiveView = view
        
    t = DB.Transaction(doc, __title__)
    t.Start()

    try:
        view.LookupParameter("Views_$Group").Set("Ennead")
        view.LookupParameter("Views_$Series").Set("List Item (´･ᆺ･`)")
    except:
        pass
    
    family_name = "EA_DetailItem_Tag"

    tag_family = REVIT_FAMILY.get_family_by_name(family_name,
                                                 load_path_if_not_exist="{}\\{}.rfa".format(os.path.dirname(__file__), family_name))
    
    Deployer(view, detail_families, tag_family)

    
    
    t.Commit()

    NOTIFICATION.messenger("Detail Items listed at view: " + view.Name)
    


    # doc.ActiveView = view





################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    list_detail_items()
    







