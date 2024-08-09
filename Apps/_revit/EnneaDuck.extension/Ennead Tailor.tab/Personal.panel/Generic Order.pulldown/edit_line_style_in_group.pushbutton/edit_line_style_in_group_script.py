#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "WORK IN PROGRESS, attempt to edit the linestyle usage that is bound to groups."
__title__ = "Modify LineStyle in Group(For A.Chi)"

# from pyrevit import forms #
from pyrevit import script #


from Autodesk.Revit import DB # pyright: ignore 
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from pyrevit.revit import ErrorSwallower
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def edit_line_style_in_group():
    bad_line_style = EnneadTab.REVIT.REVIT_SELECTION.get_linestyle(doc, linestyle_name = ".07")

    target_line_style = EnneadTab.REVIT.REVIT_SELECTION.get_linestyle(doc, linestyle_name = ".01")


    groups = EnneadTab.REVIT.REVIT_SELECTION.get_detail_groups_by_name(doc, group_name = "test")
    #print groups




    #T = DB.TransactionGroup(doc, __title__.replace("\n", " "))
    #T.Start()
    #


    wait_groups = []
    for i, group in enumerate(groups):
        if i == 0:
            editor_group_id = group.Id
            continue
        wait_groups.append(group)


    t = DB.Transaction(doc, "duptype")
    t.Start()
    if len(wait_groups) > 0:
        original_type = wait_groups[0].GroupType
        temp_type_name = original_type.LookupParameter("Type Name").AsString() + "_temp_EA3feddedfef222"
        temp_type = original_type.Duplicate(temp_type_name)
        for group in wait_groups:
            group.GroupType = temp_type

    t.Commit()


    t = DB.Transaction(doc, "change editor")
    t.Start()
    with ErrorSwallower() as swallower:
        editor_group = doc.GetElement(editor_group_id)
        group_members = [doc.GetElement(x) for x in editor_group.GetMemberIds()]
        for member in group_members:
            #sprint member.LineStyle
            if member.LineStyle.Id  == bad_line_style.Id:
                member.LineStyle = target_line_style

    t.Commit()
    #doc.Regenerate()


    t = DB.Transaction(doc, "change wait groups")
    t.Start()
    editor_group = doc.GetElement(editor_group_id)
    print(editor_group)
    if len(wait_groups) > 0:
        for group in temp_type.Groups:
            group.GroupType = editor_group.GroupType
            group_members = [doc.GetElement(x) for x in editor_group.GetMemberIds()]
            for member in group_members:
                DB.ElementTransformUtils.MoveElement(doc, member.Id, DB.XYZ(0,0,1))
                """
                need a way to move all element from group to force update
                """
    t.Commit()



    #T.Commit()

def AA_edit_line_style_in_group():
    bad_line_style = EnneadTab.REVIT.REVIT_SELECTION.get_linestyle(doc, linestyle_name = ".07")

    target_line_style = EnneadTab.REVIT.REVIT_SELECTION.get_linestyle(doc, linestyle_name = ".01")


    groups = EnneadTab.REVIT.REVIT_SELECTION.get_detail_groups_by_name(doc, group_name = "test")
    #print groups




    #T = DB.TransactionGroup(doc, __title__.replace("\n", " "))
    #T.Start()
    #with ErrorSwallower() as swallower:


    wait_groups = []
    for i, group in enumerate(groups):
        if i == 0:
            editor_group_id = group.Id
            continue
        wait_groups.append(group)


    t = DB.Transaction(doc, "duptype")
    t.Start()
    if len(wait_groups) > 0:
        original_type = wait_groups[0].GroupType
        temp_type_name = original_type.LookupParameter("Type Name").AsString() + "_temp_EAe33222"
        temp_type = original_type.Duplicate(temp_type_name)
        for group in wait_groups:
            group.GroupType = temp_type

    t.Commit()

    def fix_group(group):
        group_members = [doc.GetElement(x) for x in group.GetMemberIds()]
        for member in group_members:
            #sprint member.LineStyle
            if member.LineStyle.Id  == bad_line_style.Id:
                member.LineStyle = target_line_style
    t = DB.Transaction(doc, "change editor")
    t.Start()
    editor_group = doc.GetElement(editor_group_id)
    group_members = [doc.GetElement(x) for x in editor_group.GetMemberIds()]
    for member in group_members:
        #sprint member.LineStyle
        if member.LineStyle.Id  == bad_line_style.Id:
            member.LineStyle = target_line_style
    t.Commit()
    #doc.Regenerate()

    return
    t = DB.Transaction(doc, "change wait groups")
    t.Start()
    editor_group = doc.GetElement(editor_group_id)
    print(editor_group)
    if len(wait_groups) > 0:
        for group in temp_type.Groups:
            group.GroupType = editor_group.GroupType
    t.Commit()



    #T.Commit()
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    edit_line_style_in_group()
    
