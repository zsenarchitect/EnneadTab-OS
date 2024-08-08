__doc__ = "Get the rooms that does not have associate level matching building id, then try to recreate this room in the coorect associate level. This is a common problem in early SD/DD where rooms are created in similar height levels and the information locked to it."
__title__ = "3.3_recreate room on correct level"

from pyrevit import script #
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import Creation
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def match_property(para_name, source, target):
    try:
        target.LookupParameter(para_name).Set(source.LookupParameter(para_name).AsString())
    except:
        target.LookupParameter(para_name).Set(source.LookupParameter(para_name).AsDouble())

def get_tag_on_room(room):
    t = DB.Transaction(doc,"local")
    t.Start()
    ids = doc.Delete(room.Id)
    t.RollBack()
    temp = []
    for id in ids:
        el = doc.GetElement(id)
        # print el.GetType()
        if "RoomTag" in str(el.GetType()):
            temp.append(el)
    if len(temp) != 0:
        return temp[0]
    return False



"""
    all_tags = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Room == room, all_tags)[0]
    try:
        return filter(lambda x: x.Room == room, all_tags)[0]
    except:
        return False
"""

class TransactionFinalizer(DB.ITransactionFinalizer):
    def OnCommitted(self, doc, string):
        return
    def OnRolledBack(self, doc, string):
        return


def process_room(room):
    global cur_value
    cur_value += 1
    output.update_progress(cur_value, max_value)
    output.print_md("#{} remaining".format( max_value - cur_value))


    # # print "---"
    # curent_level_name = doc.GetElement( room.LevelId).Name
    # # print curent_level_name


    # print current_tag



    """
    options = t.GetFailureHandlingOptions ()
    # options.SetTransactionFinalizer(TransactionFinalizer(doc, "fix room"))
    options.SetTransactionFinalizer(TransactionFinalizer())
    options.SetDelayedMiniWarnings(True)
    options.SetForcedModalHandling(False)
    t.SetFailureHandlingOptions (options)
    """


    target_level = get_matching_level(room)
    room.LookupParameter("Spatial Element Note").Set(target_level.Name)

    location = room.Location.Point
    insert_location = DB.UV(location.X, location.Y)
    new_room = doc.Create.NewRoom(target_level, insert_location)
    para_names = ["Name","Department", "MC_$Translate", "MC_$BuildingID"]
    for para_name in para_names:
        match_property(para_name, room, new_room)
    new_room.LookupParameter("Limit Offset").Set(room.LookupParameter("Unbounded Height").AsDouble())

    tag_info = dict[room.Id]
    doc.Delete(room.Id)
    new_room.LookupParameter("Spatial Element Note").Set("new born")


    # current_tag = PPPP_get_tag_on_room(room)
    if tag_info != None:
        tag_insert_location = tag_info[0]
        tag_view = tag_info[1]
        new_tag = doc.Create.NewRoomTag(DB.LinkElementId(new_room.Id), tag_insert_location, tag_view.Id)
        print("tag added")

    # print target_level.Name

def get_matching_level(room):



    def test_level(x):
        guested_level_name = room.LookupParameter("MC_$BuildingID").AsString() + " - " + room.Level.Name.split(" - ")[1]
        # print guested_level_name
        return x.Name == guested_level_name




    all_levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).WhereElementIsNotElementType().ToElements()

    try:
        return filter(test_level, all_levels)[0]
    except IndexError:
        guested_level_name = room.LookupParameter("MC_$BuildingID").AsString() + " - " + room.Level.Name.split(" - ")[1]
        print("cannot find {}".format(guested_level_name))
        return room.Level

def check_associated_level(element):


    level_name = doc.GetElement( element.LevelId).Name

    bldg_id = element.LookupParameter("MC_$BuildingID").AsString()

    if bldg_id not in level_name :
        return True
    return False
################## main code below #####################
output = script.get_output()
output.close_others()

# get bad rooms
all_rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
bad_rooms = filter(check_associated_level, all_rooms)
# bad_rooms = bad_rooms[0:10]


dict = {}
T = DB.TransactionGroup(doc, "find tag")
T.Start()
count = len(bad_rooms)
for room in bad_rooms:
    print(count)
    count -= 1
    # print room.Id
    tag = get_tag_on_room(room)
    if not tag:
        dict[room.Id] = None
        continue
    location = tag.Location.Point
    tag_insert_location = DB.UV(location.X, location.Y)
    # tag_type = current_tag.RoomTagType.Id
    tag_view = tag.View
    dict[room.Id] = [tag_insert_location, tag_view]
T.RollBack()

for key in dict.keys():
    print(dict[key])
# script.exit()

print("start")
cur_value, max_value = 0, len(bad_rooms)
#PROCESS EACH VIEW
t = DB.Transaction(doc, "fix room")
t.Start()
map(process_room, bad_rooms)
t.Commit()

print("{} room recreated".format(max_value))

EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()
