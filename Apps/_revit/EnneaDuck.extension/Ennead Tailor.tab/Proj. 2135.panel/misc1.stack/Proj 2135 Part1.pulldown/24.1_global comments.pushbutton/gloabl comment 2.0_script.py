__doc__ = "For office markup elements( internal textnotes, sketch dims, etc), the tool goes thru the entire file and find them on each view, then it either hide and show them based on your choice."
__title__ = "24.1_Show/Hide Markups and Office layout 2.0"

from pyrevit import forms, script #
from Autodesk.Revit import DB # pyright: ignore 
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
import System
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()


def get_all_markup_contents(category_name):
    def is_markup_content(x):
        type = x.GetType()
        if "TextNote" in str(type):
            type_name = x.TextNoteType.LookupParameter("Type Name").AsString()
        elif "Dimension" in str(type):
            type_name = x.DimensionType.LookupParameter("Type Name").AsString()

        elif str(type) in ["Autodesk.Revit.DB.DetailArc",
                            "Autodesk.Revit.DB.DetailLine",
                            "Autodesk.Revit.DB.DetailEllipse" ,
                            "Autodesk.Revit.DB.ModelLine",
                            "Autodesk.Revit.DB.ModelArc",
                            "Autodesk.Revit.DB.ModelEllipse",
                            "Autodesk.Revit.DB.DetailNurbSpline",
                            "Autodesk.Revit.DB.CurveElement" ,
                            "Autodesk.Revit.DB.ModelHermiteSpline"]:
            type_name = x.LineStyle.Name
        elif "RevisionCloud" in str(type):
            return True
        else:
            print(type)
            type_name = "bad"

        if "markup" in type_name.lower():
            return True
        return False


    bic = DB.BuiltInCategory.Parse(DB.BuiltInCategory,category_name)
    all_elements = DB.FilteredElementCollector(doc).OfCategory(bic).WhereElementIsNotElementType().ToElements()


    return filter(is_markup_content, all_elements)



def get_all_office_layout_textnotes():
    all_textnotes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: "Office Layout" in x.TextNoteType.LookupParameter("Type Name").AsString(), all_textnotes)

def get_all_office_layout_tags():
    all_room_tags = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_RoomTags).WhereElementIsNotElementType().ToElements()
    #print all_room_tags
    #print all_room_tags[0].Id
    all_room_tags = filter(lambda x: hasattr(x, "RoomTagType"), all_room_tags)
    return filter(lambda x: "Office Layout" in x.RoomTagType.LookupParameter("Type Name").AsString(), all_room_tags)


def get_content_by_view(list, view_id):
    return [x for x in list if x.OwnerViewId == view_id]



def process_view(view_id, collection):
    view = doc.GetElement(view_id)

    if view.IsTemplate:
        print("---checkinging on template: {}".format(view.Name))
    else:
        print("---checkinging on view: {}".format(view.Name))

    if "Save to Central" in view.Name:
        return


    elements_in_view = get_content_by_view(collection, view_id)

    action_list = [item.Id for item in elements_in_view if item.IsHidden(view) != try_hidding_all]

    #new control to unhide any manual hide.
    if not try_hidding_all:
        action_list.extend(item.Id for item in get_every_office_layout_elements() if item.IsHidden(view))


    action_list = System.Collections.Generic.List[DB.ElementId](action_list)
    if len(action_list) == 0:
        print("nothing to do here.")
        print("\n\n")
        return
    else:
        print("found {} related items".format(len(action_list)))
        if EA_UTILITY.is_owned(view):
            print("\n\n")
            return
        print("\n\n")

    if try_hidding_all:
        view.HideElements(action_list)
    else:
        view.UnhideElements(action_list)


def process_collection(collection, is_owned_view_only = True):
    view_ids = {x.OwnerViewId for x in collection}
    if not is_owned_view_only:
        all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
        all_templates = get_all_templates()
        #print all_templates
        def is_view_using_valid_template(view):
            view_template = doc.GetElement(view.ViewTemplateId)
            if view_template is None:
                return False
            if view_template.Name not in [x.Name for x in all_templates]:
                return False
            return True

        all_views = filter(is_view_using_valid_template, all_views)

        view_ids = {x.Id for x in all_views}

        """
        for ww in range(100):
            print("---")
            print(all_views[ww].Name)
            print(all_views[ww].ViewTemplateId)
            if doc.GetElement(all_views[ww].ViewTemplateId) != None:
                print(doc.GetElement(all_views[ww].ViewTemplateId).Name)
        """
        # print view_ids
    view_ids = sorted(list(view_ids), key = lambda x: doc.GetElement(x).Name)
    #map(lambda x: process_view(x, collection), view_ids)
    for i,x in enumerate(view_ids):
        print("#{}/{}".format(i + 1, len(view_ids)))
        process_view(x, collection)


    print("\n\n##finish processing views.")




def get_every_office_layout_elements():
    """this is trying to unhide elements that have been hide manually, becasue view filter cannot handle local treatment.

    """
    raw_collection = []
    categories = [DB.BuiltInCategory.OST_Walls,
                    DB.BuiltInCategory.OST_Furniture,
                    DB.BuiltInCategory.OST_Doors,
                    DB.BuiltInCategory.OST_PlumbingFixtures]
    for cate in categories:
        raw_collection.extend(list(DB.FilteredElementCollector(doc).OfCategory(cate).WhereElementIsNotElementType().ToElements()))

    def is_type_comments_office_layout(x):
        type_comment = ""
        if hasattr(x, "WallType"):
            type_comment = x.WallType.LookupParameter("Type Comments").AsString()
        if hasattr(x, "Symbol"):
            type_comment = x.Symbol.LookupParameter("Type Comments").AsString()
        if type_comment == "Office Layout":
            return True
        return False

    office_layout_collection = filter(is_type_comments_office_layout, raw_collection)

    all_walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    office_layout_wall_by_comment = filter(lambda x: x.LookupParameter("Comments").AsString() == "Office Layout", all_walls)
    for wall in office_layout_wall_by_comment:
        if wall not in office_layout_collection:
            office_layout_collection.append(wall)

    return office_layout_collection


def get_all_templates():
    views = DB.FilteredElementCollector(doc).OfClass(DB.View)
    return [v for v in views if v.IsTemplate and v.Name in template_checklist]



def get_template_checklist():
    with open(template_checklist_filepath) as f:
        lines = f.readlines()
    return map(lambda x: x.replace("\n",""), lines)



def get_office_layout_filter_id():
    #get the id of the office layout filter
    view_filters = DB.FilteredElementCollector(doc).OfClass(DB.FilterElement).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Name == "Office Layout Content", view_filters)[0].Id

def get_meeting_room_filter_id():
    #get the id of the office layout filter
    view_filters = DB.FilteredElementCollector(doc).OfClass(DB.FilterElement).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Name == "Room_Office Meeting Rooms", view_filters)[0].Id

def process_office_layout_template(template):

    try:
        template.SetFilterVisibility(filter_office_layout_id, not(try_hidding_all))
        template.SetFilterOverrides (filter_meeting_room_id, meeting_room_override_setting)
    except Exception as e:
        print("skip {} becasue:{}".format(template.Name, e))


def save_template_to_file():
    views = DB.FilteredElementCollector(doc).OfClass(DB.View)
    templates = [v.Name for v in views if v.IsTemplate]

    templates.sort()
    # print templates
    import EA_UTILITY
    import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
    EA_UTILITY.save_list_to_txt(templates, template_checklist_filepath)
################## main code below #####################
output = script.get_output()
output.close_others()


template_checklist_filepaths = [r"I:\2135\0_BIM\10_BIM Management\Office Layout Template Checklist_N3.txt",
                                r"I:\2135\0_BIM\10_BIM Management\Office Layout Template Checklist_N4.txt",
                                r"I:\2135\0_BIM\10_BIM Management\Office Layout Template Checklist_N5.txt",
                                r"I:\2135\0_BIM\10_BIM Management\Office Layout Template Checklist_N6.txt"]

for template_checklist_filepath in template_checklist_filepaths:
    if doc.Title.split("HQ_")[1] in template_checklist_filepath:
        break




#ask if want to show, hide
hidding_options = ["hide", ["show","2022-06-16 updates: It takes a lot longer than 'hide' option because it is also trying to unhide any manually hide elements"], "know where is the template checklist saved", "save all templates names to override checklist file"]
res = EA_UTILITY.dialogue(main_text = "for all markup or office layout content, i want to [...]", options = hidding_options)
if res == hidding_options[0]:
    try_hidding_all = True
elif res == hidding_options[1][0]:
    try_hidding_all = False
elif res == hidding_options[2]:
    path_display = ""
    for item in template_checklist_filepaths:
        path_display += "\n{}".format(item)
    forms.alert("Go to this text file to modify the view template name checklist that you want to participate the office layout filter on/off.\n\n{}".format(path_display))
    script.exit()
elif res == hidding_options[3]:
    save_template_to_file()
    script.exit()
else:
    script.exit()


markup_annos = []
markup_clouds = []
all_templates = []
office_layout_anno_collection = []
cate_options = ["Markup Dim, Markup Textnote, Markup Line", "Revision Cloud", "Office Layout Filter and office room tag and office textnotes"]
cate_selection = forms.SelectFromList.show(cate_options,
                                            multiselect = True,
                                            button_name = "Go!",
                                            title = "what is considered as markup?")

#get markup content
output.freeze()
all_markup_texts = get_all_markup_contents("OST_TextNotes")
all_markup_dims = get_all_markup_contents("OST_Dimensions")
all_markup_lines = get_all_markup_contents("OST_Lines")
all_clouds = get_all_markup_contents("OST_RevisionClouds")
#print all_clouds
output.unfreeze()


if cate_options[0] in cate_selection:
    markup_annos = all_markup_texts + all_markup_dims + all_markup_lines
if cate_options[1] in cate_selection:
    markup_clouds = all_clouds
if cate_options[2] in cate_selection:
    template_checklist = get_template_checklist()
    all_templates = get_all_templates()
    filter_office_layout_id = get_office_layout_filter_id()
    filter_meeting_room_id = get_meeting_room_filter_id()
    meeting_room_override_setting = DB.OverrideGraphicSettings()
    if try_hidding_all:
        meeting_room_override_setting.SetSurfaceForegroundPatternColor(DB.Color(208, 238, 255))

    office_layout_anno_collection = []
    office_layout_anno_collection.extend( get_all_office_layout_textnotes() )
    office_layout_anno_collection.extend( get_all_office_layout_tags() )



##process contetn in this list for the view
t = DB.Transaction(doc, "{} markup content".format(res))
t.Start()

will_sync_and_close = False
markup_collection = markup_annos + markup_clouds
process_collection(markup_collection)


map(process_office_layout_template, all_templates)
search_local_hide = False
if not try_hidding_all:
    search_res = EA_UTILITY.dialogue(main_text = "Search local hide? This will make unhide process much longer becasue it need to search thru every view.\nOtherwise it will just search thru templates.", options = ["Yes, search each views", "No, just search templates"])
    search_local_hide = True if "Yes" in search_res else False

    if search_local_hide:
        will_sync_and_close_res = EA_UTILITY.dialogue(main_text = "Sync and Close after done?", options = ["Yes", "No"])
        if will_sync_and_close_res == "Yes":
            will_sync_and_close = True






process_collection(office_layout_anno_collection, is_owned_view_only = not search_local_hide)

t.Commit()

if not will_sync_and_close:
    forms.alert("{} action finished.\n{} markup element involved (except sample graphic in the start view).\n{} office layout annotation involved.\n{} view template changed.".format(res, len(markup_collection),len(office_layout_anno_collection), len(all_templates)))


try:
    if will_sync_and_close:
        EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()
except:
    pass
