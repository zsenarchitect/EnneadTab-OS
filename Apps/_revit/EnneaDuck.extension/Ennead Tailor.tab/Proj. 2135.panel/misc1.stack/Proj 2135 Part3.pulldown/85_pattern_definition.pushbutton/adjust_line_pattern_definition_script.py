#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Adjusting the line pattern definition to remove very similar but different definition, WIP"
__title__ = "85_adjust_line_pattern_definition"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def process_line_pattern_element(line_pattern_element):
    print("\n\n  ")
    print("#"*20)
    print(line_pattern_element.Name)
    # get line pattern segements list
    line_pattern = line_pattern_element.GetLinePattern ()
    segements= line_pattern.GetSegments()

    max_length = max(list(segements))
    if max_length < 2:
        return
    for seg in segements:
        print(seg.Type)
        length = EA_UTILITY.internal_to_mm(seg.Length)
        print(length)






    # for each segements, if the length converted to mm is larger than 10, scale it down to 3mm and keep the scale factor

    # apply same factor to the rest of segements list


    #  reset the line pattern

    #
def adjust_line_pattern_definition():
    pass


    # get all line pattern
    all_line_patterns = DB.FilteredElementCollector(doc).OfClass(DB.LinePatternElement ).ToElements()

    map(process_line_pattern_element, all_line_patterns)


    """
    t = DB.Transaction(doc, "Link into link doc view for this dummy")
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """


    """

    import selected object style from project or family
    """
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    adjust_line_pattern_definition()
