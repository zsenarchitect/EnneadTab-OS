#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Quick display of family tree for current and all nesting family of the current family."
__title__ = "Family\nTree"
__context__ = "doc-family"
__tip__ = True
# from pyrevit import forms #
from pyrevit import script #



from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, EXE, FOLDER
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

class Solution:
    def __init__(self):
        self.docs_to_be_closed = []


    @ERROR_HANDLE.try_catch_error()
    def family_tree(self):
        output.print_md("#The family tree of [{}]#".format(doc.Title))
        indent = ""
        output.print_md("**{}< {} >**".format(indent, doc.Title))
        self.process_family(family_doc = doc, indent = indent)

        dest_file = FOLDER.get_EA_dump_folder_file("Family Tree of {}.html".format(doc.Title))
        output.save_contents(dest_file)
        output.close()
        EXE.open_file_in_default_application(dest_file)


        for family_doc in self.docs_to_be_closed:
            family_doc.Close(False)


    def process_family(self, family_doc, indent):


        nested_families = list(DB.FilteredElementCollector(family_doc).OfClass(DB.Family).ToElements())
        indent += "+------------"
        if len(indent)> 100:
            print ("tree branch depth too deep, either you should try to make it shallower, or there might be a circular reference in the family.\n\nFor example, A --> B --> C --> A")
            return

        nested_families.sort(key = lambda x: x.FamilyCategory.Name + "_" + x.Name)


        for nested_family in nested_families:
            if nested_family.FamilyCategory.Name in ["Section Marks", "Level Heads"]:
                continue

            if nested_family.Name:
                output.print_md("{}[{}] **< {} >**".format(indent, nested_family.FamilyCategory.Name, nested_family.Name))

            if not nested_family.IsEditable:
                continue
            nested_family_doc = family_doc.EditFamily(nested_family)
            self.process_family(nested_family_doc, indent)
            self.docs_to_be_closed.append(nested_family_doc)
        #self.docs_to_be_closed.append(family_doc)

        #
        # try:
        #     family_doc.Close(False)
        # except:
        #     pass


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    Solution().family_tree()
    
