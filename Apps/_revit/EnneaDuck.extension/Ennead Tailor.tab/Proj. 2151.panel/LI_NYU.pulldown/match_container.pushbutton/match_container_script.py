#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Match Container"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from pyrevit import script

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION, OUTPUT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()
import file_getter as FG


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def match_container():
    container_file_title = "EAEC_NYU-Langone Health_Container File"
    if REVIT_APPLICATION.get_doc().Title == container_file_title:
        NOTIFICATION.messenger("Your active doc is the container file. Nothing to compare.")
        return None
    container_doc = FG.get_NYU_doc(doc_title = container_file_title)
    if not container_doc:
        return
    
    NYULI_list = [
        "2151_A_EA_NYULI_Hospital_EXT",
        "2151_A_EAEC_NYULI_Hospital_INT",
        "2151_A_EA_NYULI_Site",
        "2151_A_EA_NYULI_Parking East",
        "2151_A_EA_NYULI_Parking West",
        "2151_A_EA_NYULI_CUP_EXT"
    ]
    working_docs = [FG.get_NYU_doc(doc_title = x) for x in NYULI_list]
    working_docs = [x for x in working_docs if x is not None]
    process_system_family("Walls", container_doc, working_docs)
    process_system_family("Floors", container_doc, working_docs)
    process_system_family("Roofs", container_doc, working_docs)

    OUTPUT.display_output_on_browser()


def process_system_family(category_name, container_doc, working_docs):
    category = getattr(DB.BuiltInCategory, "OST_{}".format(category_name))

    master_types = query_system_family(category, container_doc)
    master_type_names = sorted([_type.type_name for _type in master_types])

    # this is list of list
    working_doc_types_collection = [query_system_family(category, working_doc) for working_doc in working_docs]
    
    total_types = []
    total_types.extend(master_types)
    for working_doc_types in working_doc_types_collection:
        total_types.extend(working_doc_types)
    total_type_names = sorted(list(set(_type.type_name for _type in total_types)))

    def is_in_list(_type, _list):
        return "<Exist>" if _type in _list else "---"
    data = []
    for type_name in total_type_names:
        row_data = [type_name, is_in_list(type_name, master_type_names)]
        for working_doc_types in working_doc_types_collection:
            working_doc_type_name_list = [_type.type_name for _type in working_doc_types]
            row_data.append(is_in_list(type_name, working_doc_type_name_list))
        data.append(row_data)
    
    output.print_table(
        table_data=data,
        title="{}Type Compare".format(category_name.rsplit('s', 1)[0]),
        columns=["{}Type".format(category_name.rsplit('s', 1)[0]), "In Container File"] + ["in [{}]".format(_doc.Title) for _doc in working_docs],
        formats=['', '', '']
    )


def query_system_family(ost, doc):
    
    types = DB.FilteredElementCollector(doc).OfCategory(ost).WhereElementIsElementType().ToElements()
    return [REVIT_FAMILY.RevitType(x) for x in types]
     



################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    match_container()







