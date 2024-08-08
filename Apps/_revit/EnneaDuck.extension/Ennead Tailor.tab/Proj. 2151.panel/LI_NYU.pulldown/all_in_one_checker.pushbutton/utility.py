
from EnneadTab import ENVIRONMENT_CONSTANTS
from EnneadTab.REVIT import REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore

# from constants import CALCULATOR_FAMILY_NAME


def get_all_calculator_types(doc):
    all_symbol_types = DB.FilteredElementCollector(doc)\
                        .OfCategory(DB.BuiltInCategory.OST_GenericAnnotation)\
                        .WhereElementIsElementType()\
                        .ToElements()
    return filter(lambda x: x.FamilyName == CALCULATOR_FAMILY_NAME, all_symbol_types)


def get_all_calculators(doc):
    all_anno_symbols = DB.FilteredElementCollector(doc)\
                        .OfCategory(DB.BuiltInCategory.OST_GenericAnnotation)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
    return filter(lambda x: x.Symbol.FamilyName == CALCULATOR_FAMILY_NAME, all_anno_symbols)


def get_calculator_type_by_type_name(doc, type_name):
    types = filter(lambda x: x.LookupParameter("Type Name").AsString() == type_name, 
                   get_all_calculator_types(doc))
    if len(types) == 0:
        return None
    return types[0]


def get_calculators_by_type_name(doc, type_name):
    family_type = get_calculator_type_by_type_name(doc, type_name)
    if not family_type:
        return []

    return filter(lambda x: x.Symbol.Id == family_type.Id, get_all_calculators(doc))


def get_family(doc):
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    families = filter(lambda x: x.Name == CALCULATOR_FAMILY_NAME, all_families)
    
    if len(families) == 0:
        print ("Cannot find this family, loading family from L drive.")
        # if it does not exist, load it from L drive and get_family again
        sample_family_path = "{}\\ENNEAD.extension\\Ennead Library.tab\\Contents.panel\\2D Contents.pulldown\\HealthCare Data Calculator.content\\EnneadTab AreaData Calculator_content.rfa".format(ENVIRONMENT_CONSTANTS.PUBLISH_BETA_FOLDER_FOR_REVIT)
        REVIT_FAMILY.load_family_by_path(sample_family_path)
        
        return get_family(doc)
    
    
    return families[0]

