#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Update WWR chart"

# from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


FIN_ELEMENT_KEYWORD = "ExtraProtrusion"
GENERIC_PROTRUSION_KEYWORD = "Protrusion"
GLASS_ELEMENT_KEYWORD = "Glass"

def is_good_region(region):
    owner_view = doc.GetElement(region.OwnerViewId)
    if owner_view.Name == "WWR Legand":
        return False
    
    type_comments = get_type_comments(region)
    if not type_comments:
        return False
    return type_comments.startswith("WWR")
    
       
@EnneadTab.ERROR_HANDLE.try_catch_error()
def update_WWR_region():
    # all_regions = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_FilledRegion).WhereElementIsNotElementType().ToElements()
    
    all_regions = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegion).WhereElementIsNotElementType().ToElements()
    good_regions = filter(is_good_region, all_regions)
    
    
    data={}
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    for region in good_regions:
        area = region.LookupParameter("Area").AsDouble()
        region.LookupParameter("FilledRegionArea").Set(area)
        
        if region.GroupId.IntegerValue != -1:
            group = doc.GetElement(region.GroupId)
            region.LookupParameter("DesignOptionName").Set(group.Name)
            
            # just prepare the group names list, not getting area sum of the group
            if group.Name not in data:
                data[group.Name] = 0
        else:
            
            print ("Are you putting this filled region type outside a option group?")
            # region.LookupParameter("DesignOptionName").Set("Solo")
    
    
    
    all_group_types = DB.FilteredElementCollector(doc).OfClass(DB.GroupType).ToElements()
    for group_type in all_group_types:
        group_name = group_type.LookupParameter("Type Name").AsString()
        if not group_name in data:
            continue
        
        sample_group = list(group_type.Groups)[0]
        for id in sample_group.GetMemberIds ():
            member = doc.GetElement(id)
            try:
                area = member.LookupParameter("Area").AsDouble()
                
                # do this after try get area so other cate will not bee here
                description = get_type_description(member)
                if FIN_ELEMENT_KEYWORD in description:
                    continue
                if GENERIC_PROTRUSION_KEYWORD in description:
                    continue
                data[group_name] += area
            except:
                # print ("skip {}".format(member))
                pass
        
      
            
    for region in good_regions:
        group_name = region.LookupParameter("DesignOptionName").AsString()
        percentage = region.LookupParameter("Area").AsDouble()/data[group_name]
        
        status = "ok"
        type_comments = get_type_description(region)
        if GLASS_ELEMENT_KEYWORD in type_comments:
            if percentage > 0.4:
                status = "bad"
                
        if FIN_ELEMENT_KEYWORD in get_type_description(region):
            if percentage > 0.1:
                status = "bad"
        region.LookupParameter("FillRegionStatus").Set(status)
        
        
        percentage = "{}%".format(100*round(percentage, 3))
        region.LookupParameter("DesignOptionAreaPercentageAsText").Set(percentage)
    t.Commit()
 
 
    EnneadTab.NOTIFICATION.messenger(main_text="WWR data updated")
   
    
    
def get_type_comments(region):
    region_type = doc.GetElement( region.GetTypeId())
    type_comments = region_type.LookupParameter("Type Comments").AsString()
    return type_comments

def get_type_description(region):
    region_type = doc.GetElement( region.GetTypeId())
    type_description = region_type.LookupParameter("Description").AsString()
    return type_description
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    update_WWR_region()
    




