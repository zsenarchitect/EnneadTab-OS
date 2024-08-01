# -*- coding: utf-8 -*-

import ENVIRONMENT, NOTIFICATION, DATA_FILE


try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
    UIDOC = __revit__.ActiveUIDocument # pyright: ignore
    DOC = UIDOC.Document
    
    import REVIT_APPLICATION
    import REVIT_SELECTION
    from pyrevit.coreutils import envvars
    
except:
    globals()["UIDOC"] = object()
    globals()["DOC"] = object()

def get_view_by_name( view_name, doc = DOC):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()
    
    for view in all_views:
        if view.Name == view_name:
            return view
    return None


def get_default_view_type(view_type, doc = DOC):

    mapper = {"3d":DB.ViewFamily.ThreeDimensional,
              "schedule":DB.ViewFamily.Schedule,
              "drafting":DB.ViewFamily.Drafting,
              "section": DB.ViewFamily.Section,
              "elevation": DB.ViewFamily.Elevation,
              "plan":DB.ViewFamily.FloorPlan}
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
    potential_types = filter(lambda x: x.ViewFamily == mapper[view_type], view_family_types)
    return potential_types[0]


def set_active_view_by_name(view_name, doc = DOC):

    view = get_view_by_name(view_name, doc)
    if view:
        # UIDOC.RequestViewChange(view)
        try:
            REVIT_APPLICATION.get_uidoc().ActiveView = view
        except Exception as e:
            NOTIFICATION.messenger(str(e))
    else:
        NOTIFICATION.messenger("<{}> does not exist...".format(view_name))




def switch_to_sync_draft_view(doc):


    view = get_view_by_name("EnneadTab Quick Sync", doc)

    if not view:
        t = DB.Transaction(doc, "Create Drafting View")
        t.Start()
        view = DB.ViewDrafting.Create(doc, get_default_view_type("drafting", doc = doc).Id)
        view.Name = "EnneadTab Quick Sync"

        DB.TextNote.Create(doc, 
                           view.Id, 
                           DB.XYZ(0, 0, 0), 
                           'Confucius Says:\n"Syncing over drafting view is quicker."\n⎛ -᷄ ᴥ -᷅ ⎞೯', 
                           REVIT_SELECTION.get_all_textnote_types(doc = doc, return_name=False)[0].Id)

        t.Commit()


    t = DB.Transaction(doc, "Sync Quicker...")
    t.Start()
    try:
        view.LookupParameter("Views_$Group").Set("Ennead")
        view.LookupParameter("Views_$Series").Set(u"Sync Monitor  ◔.̮◔✧")
    except:
        pass
    t.Commit()

    
    envvars.set_pyrevit_env_var("LAST_VIEW_BEFORE_SYNC", REVIT_APPLICATION.get_uidoc().ActiveView.Name)
    set_active_view_by_name("EnneadTab Quick Sync")

def switch_from_sync_draft_view():
    last_view_name = envvars.get_pyrevit_env_var("LAST_VIEW_BEFORE_SYNC")
    if not last_view_name:
        return

    set_active_view_by_name(last_view_name)

    for open_ui_view in REVIT_APPLICATION.get_uidoc().GetOpenUIViews():
        open_view = DOC.GetElement(open_ui_view.ViewId)
        if open_view and open_view.Name == "EnneadTab Quick Sync":
            open_ui_view.Close()




def get_view_title(view):
    return view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION].AsString()

def set_view_title(view, title):
    view.Parameter[DB.BuiltInParameter.VIEW_DESCRIPTION].Set(title)

def get_detail_number(view):
    return view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].AsString()

def set_detail_number(view, detail_number):
    view.Parameter[DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER].Set(detail_number)





"""the resiter of the server happen during startup"""
class GraphicDataItem:

    def __init__(self, location, additional_info = {}):
        self.location = location
        self.additional_info = additional_info

        
def show_in_convas_graphic(graphic_datas, doc = DOC, view = None):
    
    """note: make it 64x64
    open in MS paint and save as 16 bit color bmp
    background 0,128,128

    if view is not provided, it will show in all views
    """



    manager = DB.TemporaryGraphicsManager.GetTemporaryGraphicsManager(doc)
    
    manager.Clear()

    path = "{}\\warning_duck.bmp".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT)

    temp_data = {}
    for graphic_data_item in graphic_datas:
        location = graphic_data_item.location
        data = DB.InCanvasControlData (path, location)

        if not view:
            index = manager.AddControl(data, DB.ElementId.InvalidElementId)
        else:
            index = manager.AddControl(data, view.Id)

        temp_data[index] = {
            "location":[location.X, location.Y, location.Z], 
             "view":view.UniqueId if view else None, 
             "additional_info": graphic_data_item.additional_info
             }

    # should not use shared data record because the index is locally created persession.
    with DATA_FILE.update_data("CANVAS_TEMP_GRAPHIC_DATA_{}.sexyDuck".format(doc.Title), is_local=True) as temp_graphic_data:
        temp_graphic_data.update(temp_data)



def show_warnings_in_view(view, doc):
    # redo inmport becasue the isolated func need structure.....
    # from EnneadTab import NOTIFICATION
    # from EnneadTab.REVIT import REVIT_VIEW
    # from Autodesk.Revit import DB # pyright: ignore 


    all_warnings = doc.GetWarnings()
    all_view_element_ids = DB.FilteredElementCollector(doc, view.Id).ToElementIds()


    description_dict = {}
    for warning in all_warnings:
        for id in warning.GetFailingElements():

            description_dict[id] = warning.GetDescriptionText()
    in_view_bad_element_ids = set(description_dict.keys()).intersection(set(all_view_element_ids))

    if not in_view_bad_element_ids:
        NOTIFICATION.messenger("No warnings in this view!")
        return

    graphic_datas = []
    for element_id in in_view_bad_element_ids:
        element = doc.GetElement(element_id)
        bbox_source_element = element.get_BoundingBox(view)
        bbox_source_center = bbox_source_element.Max - bbox_source_element.Min
        description = description_dict[element_id]
        graphic_datas.append(GraphicDataItem(bbox_source_center, additional_info = {"description": description}))

        
    show_in_convas_graphic(graphic_datas, view = view)
    NOTIFICATION.messenger("Warnings marked!")
    