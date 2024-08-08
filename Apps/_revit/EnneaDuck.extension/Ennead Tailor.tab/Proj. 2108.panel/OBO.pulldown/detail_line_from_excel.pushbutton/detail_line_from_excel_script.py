#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Generate detail line from the Excel survey pt data. Best used for property line geneation."
__title__ = "Detail Line By Excel"
__tip__ = True

from pyrevit import forms #
from pyrevit import script #


from EnneadTab import ERROR_HANDLE, EXCEL, NOTIFICATION, DATA_CONVERSION, TIME
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_GEOMETRY, REVIT_UNIT
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error()
def detail_line_from_excel():
    excel = forms.pick_excel_file()
    if not excel:
        return
    if excel.endswith(".xlsx"):
        NOTIFICATION.messenger("Please save your excel as .xls for max compatiablity")
        return

    lines = EXCEL.read_data_from_excel(excel)

    # for line in lines:
    #     print(line)
    
    pts = [DB.XYZ(REVIT_UNIT.m_to_internal(float(line[1][2:])), 
                  REVIT_UNIT.m_to_internal(float(line[2][2:])), 
                  0) 
           for line in lines]

    t = DB.Transaction(doc, __title__)
    t.Start()
    print (pts[:2])
    pts = [REVIT_GEOMETRY.transform_survey_pt_to_internal_pt(doc, pt) for pt in pts]
    print (pts[:2])


    # pts.append(pts[0]) # the excel alloready make a seconda record of pt for the loop

    detail_line_ids = []
    for i in range(len(pts)-1):
        # print (pts[i].DistanceTo (pts[i+1]))
        if pts[i].DistanceTo (pts[i+1]) < 0.0001:
            print ("Weird data, too close")
            continue
        # print ("Making")
        line = DB.Line.CreateBound(pts[i], pts[i+1])
        detail_line_ids.append(doc.Create.NewDetailCurve(doc.ActiveView, line).Id)

    group = doc.Create.NewGroup(DATA_CONVERSION.list_to_system_list(detail_line_ids))

    group.GroupType.Name = "EA_PropertyLineMaker_({}_{})".format(doc.ActiveView.Name,
                                                                        TIME.get_formatted_current_time())
    t.Commit()



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    detail_line_from_excel()
    







