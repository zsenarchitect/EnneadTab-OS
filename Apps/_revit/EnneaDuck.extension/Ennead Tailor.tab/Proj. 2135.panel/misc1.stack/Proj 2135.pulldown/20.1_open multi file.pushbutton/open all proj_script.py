__doc__ = "Open many Bili projects together."
__title__ = "21.1_Open Many\nBili Proj"
__context__ = "zero-doc"

from pyrevit import forms, DB, revit, script
import System
import EA_UTILITY
import EnneadTab
from pyrevit.revit import ErrorSwallower


"""
class OpenCloudCallBack(DB.IOpenFromCloudCallback):
    def OnOpenConflict (self):
        return False
"""

def close_docs_by_name(names = [], close_all = False):

    def safe_close(doc):
        doc.Close(False)
        doc.Dispose()#########################


    docs = get_top_revit_docs()
    if close_all:
        map(safe_close, docs)
        return

    for doc in docs:
        if doc.Title in names:
            safe_close(doc)

def get_top_revit_docs():

    docs = app.Documents
    OUT = []
    for doc in docs:
        if doc.IsLinked or doc.IsFamilyDocument:
            continue
        OUT.append(doc)
    return OUT



def export_from_doc(doc):

    sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

    output.print_md( "##{}".format(doc.Title))
    for sheet in sheets:
        output.print_md( sheet.Name)
    print("-------------------export finish")

def open_doc_siliently(doc_name, no_workset_option = False):
    for data in GUID_list:
        if data[0] == doc_name:
            break

    cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(System.Guid(data[1]), System.Guid(data[2]) )
    #print cloud_path
    open_options = DB.OpenOptions()
    if no_workset_option:
        open_options.SetOpenWorksetsConfiguration (DB.WorksetConfiguration(DB.WorksetConfigurationOption.CloseAllWorksets ) )
    if use_audit:
        open_options.Audit = True
    new_doc = app.OpenDocumentFile(cloud_path,
                                open_options)


def open_doc_and_activate(doc_name):
    for data in GUID_list:
        if data[0] == doc_name:
            break

    cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(System.Guid(data[1]), System.Guid(data[2]) )
    print(cloud_path)
    # open_options = DB.OpenOptions()
    # new_doc = app.OpenDocumentFile(cloud_path,
    #                             open_options)
    EA_UTILITY.open_and_active_project(cloud_path)

    #output.print_md( "background open file {}".format(doc_name))


def background_action():
    open_without_workset_res = EA_UTILITY.dialogue(options = ["Yes, no worksets", "No, keep default open status"], main_text = "Open without worksets?")
    if "Yes" in open_without_workset_res:
        open_without_workset = True
    else:
        open_without_workset = False


    docs_to_process = forms.SelectFromList.show(bili_file_list,
                                            multiselect = True)
    if not docs_to_process:
        return

    docs_already_open = [x.Title for x in get_top_revit_docs()]
    docs_to_be_opened_by_API = [x for x in docs_to_process if x not in docs_already_open]
    print("docs alrady open = {}".format(docs_already_open))
    print("docs to be opened = {}".format(docs_to_be_opened_by_API))




    EA_UTILITY.set_open_hook_depressed(True)

    with ErrorSwallower() as swallower:
        for doc_name in docs_to_be_opened_by_API:
            open_doc_siliently(doc_name, no_workset_option = open_without_workset)
    print("silent mode finish")
    for doc_name in docs_to_be_opened_by_API:
        open_doc_and_activate(doc_name)


    EA_UTILITY.set_open_hook_depressed(False)
    #output.close_others(all_open_outputs = True)
    output.print_md( "tool finished")
################## main code below #####################
output = script.get_output()
output.close_others()
output.self_destruct(10)
try:
    app = revit.doc.Application
except:
    uiapp = __revit__
    app = uiapp.Application
#cloud_path = "BIM 360://2135_Bilibili Shanghai Headquarters/2135_BiliBili SH HQ_N4.rvt"
cloud_path = r"BIM 360://2135_Bilibili Shanghai Headquarters/***.rvt"

GUID_list = [
            ["2135_BiliBili SH HQ_N3", "7bb487db-c370-408e-9a97-9441ef91c51c", "9652bd4b-03b2-4016-8af3-2742efa27968"],
            ["2135_BiliBili SH HQ_N4_OLD", "7bb487db-c370-408e-9a97-9441ef91c51c", "ca4336c2-ea68-4d16-97a5-32c09a7c607b"],
            ["2135_BiliBili SH HQ_N4", "7bb487db-c370-408e-9a97-9441ef91c51c", "4f84f7b1-07a4-4f36-992b-62e9f69c3453"],
            ["2135_BiliBili SH HQ_N5", "7bb487db-c370-408e-9a97-9441ef91c51c", "bc6dc5d7-8833-4564-aa74-c64dc14f50a1"],
            ["2135_BiliBili SH HQ_N6", "7bb487db-c370-408e-9a97-9441ef91c51c", "50ce9b1b-6ecf-4a7b-aec1-8f0af5acfe06"],
            ["2135_BiliBili SH HQ_Site", "7bb487db-c370-408e-9a97-9441ef91c51c", "8e18fa0b-26ec-4ddd-99d1-799953f5e2b3"],
            ["2135_BiliBili SH HQ_Plot Connection", "7bb487db-c370-408e-9a97-9441ef91c51c", "cc92a09d-f24c-43b7-92c7-d3b30ab62b68"],
            ["2135_BiliBili SH HQ_N3_Special Geometry", "7bb487db-c370-408e-9a97-9441ef91c51c", "cb647c33-3cf4-4275-b570-0ce24aa44607"],
            ["2135_BiliBili SH HQ_Structure_N3", "7bb487db-c370-408e-9a97-9441ef91c51c", "236d579c-c3f0-4497-abae-c6c4919265b2"],
            ["2135_BiliBili SH HQ_Structure_N5", "7bb487db-c370-408e-9a97-9441ef91c51c", "ad8ad658-5015-494a-9d84-8afe477be192"],
            ["2135_BiliBili SH HQ_Structure_N6", "7bb487db-c370-408e-9a97-9441ef91c51c", "39399a76-989b-4d3e-8805-54359cf7d184"]
            ]


bili_file_list = ["2135_BiliBili SH HQ_N3",
                "2135_BiliBili SH HQ_N4_OLD",
                "2135_BiliBili SH HQ_N4",
                "2135_BiliBili SH HQ_N5",
                "2135_BiliBili SH HQ_N6",
                "2135_BiliBili SH HQ_Site",
                "2135_BiliBili SH HQ_Plot Connection",
                "2135_BiliBili SH HQ_N3_Special Geometry",
                "2135_BiliBili SH HQ_Structure_N3",
                "2135_BiliBili SH HQ_Structure_N5",
                "2135_BiliBili SH HQ_Structure_N6"
                ]

"""
docs = get_top_revit_docs()
for doc in docs:
    print(doc.Title)
"""
#close_docs_by_name(close_all = True)
#script.exit()

use_audit = EA_UTILITY.dialogue(main_text = "open with audit?", options = ["yes", "no audit"])

background_action()
