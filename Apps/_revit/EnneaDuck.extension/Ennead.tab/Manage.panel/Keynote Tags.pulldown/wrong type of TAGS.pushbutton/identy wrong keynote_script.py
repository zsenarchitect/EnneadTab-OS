__doc__ = """You should avoid using user keynotes, but if someone already did in the project, you can find them here.

Also, element keynote and material keynote should be used by it repsected types. 
If there is mismatch, this tool will attempt to find them. The rule as as such, if there is 'material' mentioned in the type name or family name, and the tag is pointing to a element key data, it will warn you. 
The same go for the element keynote types.

User keynote, since no one should really use it, will be highlighted as blue."""
__title__ = "Identify Wrong Type\nOf KeynoteTAG"
__tip__ = True
from pyrevit import DB, revit, script


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, LOG
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

def is_owned(element):
    eh = revit.query.get_history(element)
    print(eh.owner)
    if len(eh.owner) == 0:
        return False
    elif eh.owner == revit.doc.Application.Username:
        return False
    else:
        print("{} Owned by {}".format(element.Id, eh.owner))
        return True


def override_2D_element(element,is_user_tag = False,is_wrong_tag_type = False, reset = False):
    view = revit.doc.GetElement(element.OwnerViewId)
    if reset:
        OG_setting = DB.OverrideGraphicSettings()
        view.SetElementOverrides(element.Id, OG_setting)
        return

    if is_wrong_tag_type:
        if element.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "Material":
            print("find wrong type, Element tag family tagging Material keynote.")
            color = DB.Color(255,0,255)

        if element.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "Element":
            print("find wrong type, Material tag family tagging Element keynote.")
            color = DB.Color(255,128,0)
        else:
            color = DB.Color(255,0,0)
    if is_user_tag:
        print("find user tag!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        color = DB.Color(0,0,215)

    #print color
    OG_setting = DB.OverrideGraphicSettings()
    OG_setting.SetProjectionLineColor(color)
    #print OG_setting.ProjectionLineColor
    view.SetElementOverrides(element.Id, OG_setting)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():

    key_note_tags = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_KeynoteTags).WhereElementIsNotElementType().ToElements()

    output.freeze()

    view_id_collection = set()
    with revit.Transaction("Identify keynote tag"):
        for tag in key_note_tags:
            """
            #tag.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString() == "User"
            print("*"*20)
            print(tag, tag.Name,tag.Parameter[DB.BuiltInParameter.SYMBOL_NAME_PARAM].AsElementId())
            print(tag.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString())
            print("###")
            #print tag.Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)#.AsString()
            for para in tag.Parameters:
                print(para.Definition.Name)
            """


            """

            maybe consider, if type name has not keyword, then search for family name?
            """
            key_source = tag.Parameter[DB.BuiltInParameter.KEY_SOURCE_PARAM].AsString()
            type_name = tag.Name.lower()
            #print tag
            if hasattr(tag, "Symbol"):
                family_name = tag.Symbol.FamilyName.lower()
            else:
                family_name = doc.GetElement(tag.GetTypeId()).get_Parameter(DB.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString().lower()
            search_pool = [type_name, family_name]

            def is_string_in_pool(string, list):
                for x in list:
                    if string in x:
                        return True
                return False

            if is_string_in_pool("material", search_pool) and "Material" == key_source:
                override_2D_element(tag,reset = True)
                continue
            if "Element" == key_source:
                if is_string_in_pool("wall", search_pool) or is_string_in_pool("system", search_pool):
                    override_2D_element(tag,reset = True)
                    continue
            print("\n\n   ")
            print("*"*20)

            print(revit.doc.GetElement(tag.OwnerViewId).Name)
            view_id_collection.add(tag.OwnerViewId)
            eh = revit.query.get_history(tag)
            print("Created by:{}".format(eh.creator))
            print(output.linkify(tag.Id, title = "go to tag" ))
            if hasattr(tag, "TagText") and tag.TagText != "":
                print("Display Content = {}".format(tag.TagText))
            if is_owned(tag):
                print("skip element owned by other.")
                continue
            if key_source == "User":
                override_2D_element(tag,is_user_tag = True, is_wrong_tag_type = False)
            else:
                override_2D_element(tag,is_user_tag = False, is_wrong_tag_type = True)

    output.unfreeze()
    if len(view_id_collection) >= 1:
        print("\n\n\n\n  ")
        print("#"*20)
        print("check below views")
        for view_id in list(view_id_collection):
            print(output.linkify(view_id, title = "{}".format(revit.doc.GetElement(view_id).Name)))

        print("#Rule for tag name checking.\nCheck 'Type Name' and 'Fmaily Name', if contain keyword 'material', then check for material keynote.\nif contain keyword 'wall' or 'system', then check for element keynote.")


        print("\n\nBlue = User Keynote, should avoid as much as you can.\nPink = Element Tag taging Material key\nOrange = Material Key tagging Element key.")
    else:
        print("No wrong keynote tag found.")

################## main code below #####################
if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    main()