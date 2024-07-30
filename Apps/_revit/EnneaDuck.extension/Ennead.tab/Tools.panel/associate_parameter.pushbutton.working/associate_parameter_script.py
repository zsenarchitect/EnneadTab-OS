# this code is from a GH_Python component in grasshopper to be converted to a pyRevit script

import clr
clr.AddReference('System.Core')
clr.AddReference('RhinoInside.Revit')
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI')

from System import Enum

import rhinoscriptsyntax as rs
import os
import Rhino
import RhinoInside
import Grasshopper
from Grasshopper.Kernel import GH_RuntimeMessageLevel as RML
from RhinoInside.Revit import Revit, Convert
from Autodesk.Revit import DB, UI
import Autodesk.Revit.ApplicationServices as AS

def show_warning(msg):
    ghenv.Component.AddRuntimeMessage(RML.Warning, msg)

def show_error(msg):
    ghenv.Component.AddRuntimeMessage(RML.Error, msg)

def show_remark(msg):
    ghenv.Component.AddRuntimeMessage(RML.Remark, msg)

# START TESTING AREA

def test():
    app = Revit.ActiveDBApplication
    doc = Revit.ActiveDBDocument
    manager = doc.FamilyManager
    params = manager.GetParameters()
    collector = DB.FilteredElementCollector(doc)
    elements = collector.OfClass(DB.FreeFormElement).ToElements()
    filtered_elements = []
    for element in elements:
        cat = element.Category.Name
        if cat in _subcategory_exclusion:
            continue
        else:
            filtered_elements.append(element)
            print cat
# test()

# END TESTING AREA

def assoc_elem_param_to_fam_param(family_path, built_in_param_name, family_param_name):
    # Define current application
    app = Revit.ActiveDBApplication
    
    # Open family file
    family_doc = app.OpenDocumentFile(family_path)
    
    # Establish family-specific variables
    family_manager = family_doc.FamilyManager
    family_params = family_manager.GetParameters()
    
    # Get element geometry and parameters
    collector = DB.FilteredElementCollector(family_doc)
    unfiltered_elements = collector.OfClass(DB.FreeFormElement).ToElements()
    
    filtered_elements = []
    if len(_subcategory_exclusion) == 0:
        filtered_elements = unfiltered_elements
    else:
        for element in unfiltered_elements:
            cat = element.Category.Name
            if cat in _subcategory_exclusion:
                continue
            else:
                filtered_elements.append(element)
    
    built_in_param = DB.BuiltInParameter[built_in_param_name]
    # element_param = element[0].Parameter[built_in_param]
    filtered_element_params = []
    for element in filtered_elements:
        filtered_element_params.append(element.Parameter[built_in_param])
    
    # Get shared parameter
    param_list = []
    for f in family_params:
        if f.Definition.Name == _family_param_name:
            param_list.append(f)
        else:
            continue
    family_param = param_list[0]
    
    # Associate parameter in family document
    with DB.Transaction(family_doc, "New Transaction") as t:
        
        try:
            t.Start()
            
            for i in range(len(filtered_elements)):
                family_manager.AssociateElementParameterToFamilyParameter(filtered_element_params[i], family_param)
                
                if _assign_subcat:
                    cat = family_doc.OwnerFamily.FamilyCategory
                    subcat = family_doc.Settings.Categories.NewSubcategory(cat, _subcategory_name)
                    element[i].Subcategory = subcat
            
            t.Commit()
    
        except Exception as e:
            t.RollBack()  # If there's any issue, rollback the transaction.
            show_error(str(e))  # Display the error in Grasshopper.
            print str(e)
        
        if t.HasStarted() and not t.HasEnded():
            t.RollBack()  # Ensure the transaction is rolled back if it hasn't been committed or rolled back already.
    
    # Close the family file and delete the backup copy
    family_doc.Save()
    family_doc.Close(False)
    backup_family_path = family_path[0:-4] + ".0001.rfa"
    os.remove(backup_family_path)



# List all files and subdirectories
all_files_and_dirs = os.listdir(_directory_path)

# Get files in directory
files = [f for f in all_files_and_dirs if os.path.isfile(os.path.join(_directory_path, f))]
file_paths = [os.path.join(_directory_path, f) for f in files]

# Run script
if run:
    for path in file_paths:
        assoc_elem_param_to_fam_param(path, _built_in_param_name, _family_param_name)



