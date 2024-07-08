
try:
    from Autodesk.Revit import DB # pyright: ignore
    REF_CLASS = DB.IFamilyLoadOptions
    import clr # pyright: ignore
    DOC = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    REF_CLASS = object # this is to trick that class can be used

    
import NOTIFICATION
import FOLDER 
import REVIT_SELECTION



class EnneadTabFamilyLoadingOption(REF_CLASS):
    def __init__(self, is_shared_using_family = True):
        self.is_shared_using_family = is_shared_using_family
        pass


    def OnFamilyFound(self, familyInUse, overwriteParameterValues):

        # true means use project value
        overwriteParameterValues = True

        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        overwriteParameterValues = True
        
        if self.is_shared_using_family:
            source = DB.FamilySource.Family
        else:
            source = DB.FamilySource.Project
        return True


def load_family(family_doc, project_doc):
    try:
        family_doc.LoadFamily.Overloads[DB.Document, DB.IFamilyLoadOptions](project_doc, EnneadTabFamilyLoadingOption())
    except Exception as e:
        print (e)
        family_doc.LoadFamily(project_doc, EnneadTabFamilyLoadingOption())
    
    
def load_family_by_path(family_path, project_doc=None, ):
    project_doc = project_doc or DOC
    
    fam_ref = clr.StrongBox[DB.Family](None)
    family_path = FOLDER.copy_file_to_local_dump_folder(family_path, file_name=family_path.rsplit("\\", 1)[1].replace("_content",""))
    project_doc.LoadFamily(family_path, EnneadTabFamilyLoadingOption(), fam_ref)
    
    return fam_ref
    
  

def is_family_exist(family_name, doc=None):
    doc = doc or DOC
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    for family in all_families:
        if family.Name == family_name:
            return True
    return False

def get_family_by_name(family_name, 
                       doc=None, 
                       load_path_if_not_exist=None):
    doc = doc or DOC
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    families = filter(lambda x: x.Name == family_name, all_families)
    
    if len(families) == 0:
        print ("Cannot find this family")
        if load_path_if_not_exist:
            print ("Loading from [{}]".format(load_path_if_not_exist))
            return load_family_by_path(load_path_if_not_exist, project_doc=doc)
        else:
            return None
        
    return families[0]


def get_all_types_by_family_name(family_name, doc=None):
    doc = doc or DOC
    family = get_family_by_name(family_name, doc=doc)
    if family is None:
        return None
    return [doc.GetElement(x) for x in family.GetFamilySymbolIds()]

def get_family_type_by_name(family_name, type_name, doc=None, create_if_not_exist=False):
    doc = doc or DOC
    family = get_family_by_name(family_name, doc=doc)
    if family is None:
        return None
    types = [doc.GetElement(x) for x in family.GetFamilySymbolIds()]

    for type in types:
        if type.LookupParameter("Type Name").AsString() == type_name:
            return type
    else:
        if create_if_not_exist:
            return type.Duplicate(type_name)
        else:
            return None

def get_family_instances_by_family_name_and_type_name(family_name, type_name, doc=None, editable_only = False):
    doc = doc or DOC
    family_type = get_family_type_by_name(family_name, type_name, doc=doc)
    if not family_type:
        NOTIFICATION.messenger("Cannot find any type")
        return

    res = [el for el in DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WhereElementIsNotElementType().ToElements() if el.Symbol.Id == family_type.Id]

    if res and editable_only:
        res = REVIT_SELECTION.filter_elements_changable(res)

    return res