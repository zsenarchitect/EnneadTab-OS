__doc__ = "Move this family to the internal origin under current orienttation. \n\nThere are 3 modes for the operation:\n1: Family is placed on 3d view, but location is wrong.>>>You select it and move it.\n2: Family is placed on 3d view somewhere but you don't know where.>>>You select it from listbox and move it.\n3: The family is just loaded in, it is new, and has not been placed anywhere.>>> You select it from list and move it."
__title__ = "Move2Origin"
__tip__ = True

from pyrevit import forms
from pyrevit import script
from EA_UTILITY import dialogue


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_UNIT, REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
from EnneadTab import NOTIFICATION 
#forms.alert( "Work in progress. Coming in the next version")
from Autodesk.Revit import DB # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


class Solution:


    def pick_instances(self):
        families = DB.FilteredElementCollector(doc).OfClass(DB.Family).WhereElementIsNotElementType().ToElements()
        families = sorted(families, key = lambda x: x.Name.lower())
        family = forms.SelectFromList.show(families,
                                            multiselect = False,
                                            name_attr = 'Name',
                                            title = "Pick family",
                                            button_name = 'Select Family')
        if not family:
            return


        types = [doc.GetElement(x) for x in family.GetFamilySymbolIds ()]
        types = sorted(types, key = lambda x: x.LookupParameter("Type Name").AsString())
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}]: {}".format(self.FamilyName, self.LookupParameter("Type Name").AsString())
        types = [MyOption(x) for x in types]
        family_type = forms.SelectFromList.show(types,
                                                multiselect = False,
                                                title = "Pick family type",
                                                button_name = 'Select Type')
        if not family_type:
            return


        if not family_type.IsActive:
            #print family_type
            t = DB.Transaction(doc, "Activate Symbol")
            t.Start()
            family_type.Activate ()
            doc.Regenerate()
            t.Commit()

        self.symbol = family_type
        #print family_type
        #print "xxxxxxx"
        family_instances = DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WhereElementIsNotElementType().ToElements()
        def check_type(instance):
            try:
                #print instance.Symbol.Id
                if instance.Symbol.Id == family_type.Id:
                    return True
                return False
            except Exception as e:
                #print str(e)
                return False

        instances = filter(check_type, family_instances)
        #print instances
        return instances

    def place_new_instance(self):


        levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()
        levels = sorted(levels, key = lambda x: x.Elevation)
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "{}: {}ft = {}mm".format(self.Name, self.Elevation, REVIT_UNIT.internal_to_mm(self.Elevation))
        levels = [MyOption(x) for x in levels]
        level = forms.SelectFromList.show(levels,
                                            multiselect = False,
                                            width = 1000,
                                            title = "Pick hosting level(this has no effect on actual location, but probably make sense to pick a level closer to your intent.)",
                                            button_name = 'Select Level that is closest to absolute zero.')
        if not level:
            return


        t = DB.Transaction(doc, "Create new instance")
        t.Start()
        if doc.IsFamilyDocument:
            doc_create = doc.FamilyCreate
        else:
            doc_create = doc.Create
        try:
            instance = doc_create.NewFamilyInstance(DB.XYZ(0,0,0),
                                                    self.symbol,
                                                    level,
                                                    DB.Structure.StructuralType.NonStructural )
        except Exception as e:
            t.RollBack()
            EA_UTILITY.dialogue(main_text = str(e), sub_text = "WIP")
            return
            #EA_UTILITY.dialogue(main_text = "{}\nHas this family been placed in project at least once?",
                                #sub_text = "Not need to be in the right location yet, a random location is fine. This tool need to ")

        if level.Elevation != 0:
            offset = level.Elevation
            instance.LookupParameter("Elevation from Level").Set(-offset)

        #instance.Pinned = True
        t.Commit()
        return instance

    @ERROR_HANDLE.try_catch_error()
    def move_to_origin(self):
        selection = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
        if len(selection) < 1:
            """
            if not EA_UTILITY.IS_DEVELOPER:
                dialogue(main_text = "No fmaily instance selected.")
                return
            """
            selection = self.pick_instances()




        if not selection or len(selection) < 1:
            #dialogue(main_text = "Please select the family you want to place.")
            selection = [self.place_new_instance()]
            #maybe here it can direct to Youtube demo video.


        """
        if isinstance(doc.ActiveView, DB.View3D):
            pass
        else:
            dialogue(main_text = 'You should be doing this in a 3D view.')
            return
        """



        #with revit.Transaction("Move2Origin"):
        t = DB.Transaction(doc, "Move2Origin")
        t.Start()
        for element in selection:
            if not element:
                continue
            if element.Pinned == True:
                res1 = dialogue(main_text = "It is currently pinned.", title = "wait...", options = ["Unpin this element and move it." , "Leave it as it is."])
                # res1 = forms.alert(options = ["Unpin this element and move it." , "Leave it as it is."], msg = "It is currently pinned.", title = "wait...")
                if res1 == "Unpin this element and move it.":
                    element.Pinned = False
                else:
                    continue
            #print element.Location
            #origin = DB.XYZ(0,0,0)
            try:
                moving_vec = DB.XYZ.Negate( element.Location.Point  )
                element.Location.Move(moving_vec)
            except:
                element.Location = DB.XYZ(0,0,0)


            """
            moving_vec =DB.XYZ.Negate( element.Location  )
            #element.Location = DB.XYZ(0,0,0)
            #DB.Transform().CreateTraslation(moving_vec)
            DB.ElementTransformUtils.MoveElement(revit.doc, element, moving_vec)
            """



            """
            and it can pin it afterward
            """
            res = dialogue(main_text = "It has moved to the origin point.\nNow I want to ...", title = "good news!", options = ["Pin this element." , "Don't Pin this element."])
            # res = forms.alert(options = ["Pin this element." , "Don't Pin this element."], msg = "It has moved to the origin point.\nNow I want to ...", title = "good news!")
            if res == "Pin this element.":
                element.Pinned = True

        t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    if doc.IsFamilyDocument :
        NOTIFICATION.messenger("this function is meant to use in project environment not in family environment")
    else:
        Solution().move_to_origin()
