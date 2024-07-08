#!/usr/bin/python
# -*- coding: utf-8 -*-


import NOTIFICATION, COLOR, OUTPUT
import REVIT_SELECTION

try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = __revit__.ActiveUIDocument
    DOC = UIDOC.Document
    from pyrevit import script
except:
    pass



class ColorSchemeUpdater:
    def __init__(self, doc, naming_map, excel_path=None, is_remove_bad = False):
        self.doc = doc
        self.naming_map = naming_map
        self.excel_path = excel_path
        self.is_remove_bad = is_remove_bad
        self.output = script.get_output()
    
    def load_color_template(self):
        """Update color scheme with office template excel version."""
        # Load data from color excel
        data = COLOR.get_color_template_data(self.excel_path)

        # Update color scheme, create if not exist, update color if exist
        t = DB.Transaction(self.doc, "Update Color Scheme")
        t.Start()
        for key in self.naming_map.keys():
            self.update_color_scheme(data, key)
        t.Commit()
        
        NOTIFICATION.messenger(main_text="Color Scheme Updated!")
        print ("Finish updating Color Scheme")
        OUTPUT.display_output_on_browser()

    def update_color_scheme(self, data, lookup_key ):
        color_scheme = get_color_scheme_by_name(self.naming_map[lookup_key])
        if not color_scheme:
            NOTIFICATION.messenger(main_text="Color Scheme [{}] not found!\nCheck spelling".format(self.naming_map[lookup_key]))
            return
        
        self.output.print_md("#Working on color scheme [{}]".format(color_scheme.Name))
        department_data = data[lookup_key]

        try:
            sample_entry = list(color_scheme.GetEntries())[0]
        except:
            NOTIFICATION.messenger("Please at least have one placeholder entry in the color scheme...")
            return
        storage_type = sample_entry.StorageType

        current_entry_names = [x.GetStringValue() for x in color_scheme.GetEntries()]
        if self.is_remove_bad:
            self.remove_non_used_entry(color_scheme)
        self.add_missing_entry(color_scheme, department_data, current_entry_names, storage_type)
        self.update_entry_color(color_scheme, department_data)

    @staticmethod
    def markdown_text(text, colorRGB):
        return '<span style="color:rgb{};">{}</span>'.format(str(colorRGB), text)


    def remove_non_used_entry(self, color_scheme):
        for existing_entry in color_scheme.GetEntries():
            if color_scheme.CanRemoveEntry (existing_entry):
                color_scheme.RemoveEntry(existing_entry)
                entry_title = existing_entry.GetStringValue()
                self.output.print_md("**---** entry [{}] removed{}".format(entry_title, ", not used" if existing_entry.IsInUse else ""))

    def add_missing_entry(self, color_scheme, department_data, current_entry_names, storage_type):
        for department in department_data.keys():
            if department not in current_entry_names:
                entry = DB.ColorFillSchemeEntry(storage_type)
                entry.Color = COLOR.tuple_to_color(department_data[department]["color"])
                entry.SetStringValue(department)
                entry.FillPatternId = REVIT_SELECTION.get_solid_fill_pattern_id(self.doc)
                color_scheme.AddEntry(entry)
                self.output.print_md("**+++** entry [{}] added with **{}**".format(department, 
                                                                                   self.markdown_text("COLOR RGB={}".format(department_data[department]["color"]), department_data[department]["color"])))

    def update_entry_color(self, color_scheme, department_data):
        for existing_entry in color_scheme.GetEntries():
            entry_title = existing_entry.GetStringValue()
            existing_color = existing_entry.Color
            
            lookup_data = department_data.get(entry_title, None)
            if not lookup_data:
                
                self.output.print_md("###  ??? entry [{}] in current area scheme not found in template excel. Are you defining a new entry? Or the spelling is different?\nThis entry is skipped for now.\n".format(entry_title))
                print ("\n")
                continue
            
            lookup_color = COLOR.tuple_to_color(lookup_data["color"])
            
            if COLOR.is_same_color(existing_color, lookup_color):
                continue
            
            old_color = (existing_entry.Color.Red, existing_entry.Color.Green, existing_entry.Color.Blue)
            existing_entry.Color = lookup_color
            color_scheme.UpdateEntry(existing_entry)
            self.output.print_md("**$$$** entry [{}] updated from **{}** to **{}**".format(entry_title, 
                                                                                           self.markdown_text("OLD COLOR RGB={}".format(old_color), old_color), 
                                                                                           self.markdown_text("NEW COLOR RGB={}".format(lookup_data["color"]), lookup_data["color"])))


def get_color_scheme_by_name(scheme_name, doc = DOC):
    color_schemes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
    color_schemes = filter(lambda x: x.Name == scheme_name, color_schemes)
    if len(color_schemes)== 0:
        NOTIFICATION.messenger(main_text = "Cannot find the color scheme [{}].\nMaybe you renamed your color scheme recently? Talk to SZ for update.".format(scheme_name))
        return
    if len(color_schemes) > 1:
        NOTIFICATION.messenger(main_text = "Found more than one color scheme with the name [{}].\nNeed better naming.".format(scheme_name))
        return
    return color_schemes[0]



def load_color_template(doc, naming_map, excel_path = None, is_remove_bad = False):
    """Update color scheme with office template excel version
NOTE: excel should be saved with .xls instead of .xlsx format
Also note, the column header should be as such:
A: Department
B: Department Abbr.
C: Department Color

D: Program
E: Program Abbr.
F: Program Color

ANYTHING ELSE IN THE EXCEL FILE WILL BE IGNORED, including the hex code text on color cell and red, green, blue value number. 
Those manual color text cannot be trusted on the long run.


sample excel path
excel_path = "J:\\2151\\2_Master File\\B-70_Programming\\03_Colors\\Color Scheme_NYULI_Active.xls"


naming map should looks like this. Key are what to lookup in excel, value is the name of color scheme in revit
naming_map = {"department_color_map":"Primary_Department Category",
              "program_color_map":"Primary_Department Program Type"}
"""
    updater = ColorSchemeUpdater(doc, naming_map, excel_path, is_remove_bad)
    updater.load_color_template()