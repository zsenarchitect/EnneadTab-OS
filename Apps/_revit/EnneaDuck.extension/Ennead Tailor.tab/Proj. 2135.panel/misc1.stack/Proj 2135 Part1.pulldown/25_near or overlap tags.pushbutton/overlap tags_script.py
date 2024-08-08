__doc__ = "Remove area tag or room tags that is visually very close on same view."
__title__ = "25_remove near or overlapped area or room tags"

# from pyrevit import forms, revit, script #
from Autodesk.Revit import DB # pyright: ignore 
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from pyrevit import revit, script, forms
# from Autodesk.Revit import Creation

doc = __revit__.ActiveUIDocument.Document # pyright: ignore
# uidoc = __revit__.ActiveUIDocument

# from Autodesk.Revit import UI # pyright: ignore
# uiapp = UI.UIApplicationapp
# uidoc = UI.UIDocument
# optional
# host_app = pyrevit._HostApplication
# app = host_app.app
# uiapp = host_app.uiapp
# uidoc = host_app.uidoc

def get_all_tags(view, is_area_tag = False, is_room_tag = False):
    if view.IsTemplate:
        return []

    if is_area_tag:
        return DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_AreaTags).WhereElementIsNotElementType().ToElements()
    if is_room_tag:
        return DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsNotElementType().ToElements()



def old_get_all_room_tags(view):
    if view.IsTemplate:
        return []
    return DB.FilteredElementCollector(doc, view.Id).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsNotElementType().ToElements()

def fix_tag_in_view(view):
    if len(get_all_tags(view, is_area_tag = True)) + len(get_all_tags(view, is_room_tag = True)) == 0:
        return

    output.print_md( "## Cleanning on view: [{}]".format(view.Name))
    def delete_tag_closer_than_distance(tag, use_room, use_area):
        delete_happened = False

        try:
            location = tag.TagHeadPosition
        except Exception as e:
            print("*"*20)
            print (e)
            print(tag)
            print(tag.Id)
            print(view.Name)
            return delete_happened

        for other_tag in get_all_tags(view, is_room_tag = use_room, is_area_tag = use_area):

            if tag.Id == other_tag.Id:
                continue
            if use_room:
                if tag.Room.Id != other_tag.Room.Id:
                    continue
            if use_area:
                if tag.Area.Id != other_tag.Area.Id:
                    continue


            other_location = other_tag.TagHeadPosition
            #
            # other_location_projected = DB.XYZ(other_location.X,
            #                                     other_location.Y,
            #                                     location.Z)
            # dist = location.DistanceTo(other_location_projected)
            # print dist


            # print location.Z
            # print other_location.Z
            vector = DB.XYZ(other_location.X - location.X, \
                                other_location.Y - location.Y, \
                                other_location.Z - location.Z)
            view_x = view.RightDirection
            view_y = view.UpDirection
            project_x = vector.DotProduct(view_x)
            proejct_y = vector.DotProduct(view_y)
            #projected_vector = project_x.Add(project_y)
            #dist = projected_vector.GetLength()
            dist = (project_x **2 + proejct_y**2)**0.5
            # print dist
            #
            # print tolerance

            if dist > tolerance:
                continue

            doc.Delete(other_tag.Id)
            print("---")
            print("delete tag too close( only if tagging same element), distance {} is smaller than tolerance {}".format(dist, tolerance))
            delete_happened = True

            break


        return delete_happened  #delete happedn so loop need to restart


    def process_category(use_room = False, use_area = False):
        safety = 0
        status_reset = True
        while True:
            # print status_reset
            if status_reset == False or safety > 100:
                break

            safety += 1
            # print safety
            status_reset = False
            tags = get_all_tags(view, is_room_tag = use_room, is_area_tag = use_area)
            # print tags
            for tag in tags:
                if not tag:
                    continue
                status_reset = status_reset or delete_tag_closer_than_distance(tag, use_room, use_area)
                if status_reset:
                    break



    tolerance = 50 #in mm unit
    # print view.Scale
    tolerance *= view.Scale
    tolerance = EA_UTILITY.mm_to_internal(tolerance)

    process_category(use_room = True)
    # print "fine"
    process_category(use_area = True)
    # print "ok"


    pass

################## main code below #####################
output = script.get_output()
output.close_others()

selection = revit.get_selection()
#GET SELECTED VIEWS
views = selection
#GET SELECTED VIEWS
#views = selection
#views = [doc.ActiveView]
# if len(views) == 0:
views = forms.select_views(use_selection = True)
# views = [doc.ActiveView]

from pyrevit import forms
res = forms.alert("sync and close docs after finish?", options = ["Yes..","Nope.."])
close_others_afterward = True if res == "Yes.." else False


#define tag
# tag_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_AreaTagType).ToElements()
# tag_type = filter(lambda x: x.FamilyName == "Discount Ratio Tag", tag_types)[0]

#PROCESS EACH VIEW
t = DB.Transaction(doc, "fix overlap tags")
t.Start()
map(fix_tag_in_view, views)
t.Commit()

if close_others_afterward:
    EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close(close_others = close_others_afterward)
