__doc__ = "Batch apply keyplan instance parameter to many sheets."
__title__ = "06_fix keyplan"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()

def reset_titleblock(tb):
    global para_names
    global opts
    with revit.Transaction("fix keyplan"):
        for para_name in opts:
            #print para_name
            tb.LookupParameter(para_name).Set(0)


def fix_titleblock(tb):
    global para_names
    global sheet_num_collection
    #print "*"*20
    sheet_number = tb.LookupParameter("Sheet Number").AsString()
    #print sheet_number
    if sheet_number in sheet_num_collection:
        try:
            reset_titleblock(tb)
            with revit.Transaction("fix keyplan"):
                for para_name in para_names:
                    tb.LookupParameter(para_name).Set(1)
        except:
            print("skip {}:{}".format(sheet_number, tb.LookupParameter("Sheet Name").AsString()))





titleblocks = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType().ToElements()
sheets = forms.select_sheets()
sheet_num_collection = [sheet.LookupParameter("Sheet Number").AsString() for sheet in sheets]
opts = ["show_N3",
        "show_N3P",
        "show_N4",
        "show_N5A",
        "show_N5B",
        "show_N5C",
        "show_Bilistage",
        "show_N6A1",
        "show_N6A2",
        "show_N6B",
        "show_N6C",
        "show_N6D",
        "show_N6E",
        "show_N6F1",
        "show_N6F2",
        "show_N6G",
        "show_N6H",
        "show_N6J",
        "show_N6K",
        "show_N4 Plaza",
        "show_N5AB Plaza",
        "show_N5BC Plaza",
        "show_N6AB Plaza",
        "show_N6C Plaza",
        "show_N6E Plaza",
        ]
para_names = forms.SelectFromList.show(opts,\
                                        multiselect=True,\
                                        button_name='Select bldg name')
with revit.TransactionGroup("fix keyplan"):
    map(fix_titleblock,titleblocks)
