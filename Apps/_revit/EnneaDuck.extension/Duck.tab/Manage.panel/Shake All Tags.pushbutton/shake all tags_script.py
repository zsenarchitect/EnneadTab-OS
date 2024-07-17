#pylint: disable=missing-docstring,import-error,invalid-name,unused-argument
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

from EnneadTab import ERROR_HANDLE

__doc__ = 'Sometimes the tag will not update after updating the component info. This can be resolved by shifting the tags up and down to force them to update.\nThis tool moved all tags on the selected sheets back-and-forth by a tiny amount to force Revit to regenerate the tag and update the display. This makes sure the tags are all reading something.'
__title__ = "Shake\nAll Tags"

output = script.get_output()


def get_viewsId_from_sheet(sheet):
    views = []
    for view_id in sheet.GetAllViewports():
        #views.append(revit.doc.GetElement(view_id))
        views.append(view_id)
    return views

def get_views_from_sheet(sheet):
    views = []
    for view_id in sheet.GetAllViewports():
        views.append(revit.doc.GetElement(view_id))
        #views.append(view_id)
    return views

def shake_tags(view):
    #print view ,view.Id, view.ViewId #this line is used to debug
    independent_tags = \
        DB.FilteredElementCollector(revit.doc, view.ViewId)\
          .OfClass(DB.IndependentTag)\
          .WhereElementIsNotElementType()\
          .ToElements()#use view.ViewId not view.id for filterelementcollector argument

    spatial_el_tags = \
        DB.FilteredElementCollector(revit.doc, view.ViewId)\
          .OfClass(DB.SpatialElementTag)\
          .WhereElementIsNotElementType()\
          .ToElements()

    tags = []
    tags.extend(independent_tags)
    tags.extend(spatial_el_tags)
    print('Shaking {0} Tags in view: {1}'
          .format(str(len(tags)),view.Parameter[DB.BuiltInParameter.VIEW_NAME].AsString()))

    #revit.active_view = revit.doc.GetElement(view.ViewId)


    #print revit.doc.GetElement(view.ViewId)
    for tag in tags:
        pin_condition = tag.Pinned


        with revit.Transaction('#1'):
            tag.Pinned = False
            old_text = tag.TagText

            #print revit.doc.GetElement(view.ViewId).ViewDirection
            #print revit.doc.GetElement(view.ViewId).UpDirection

            #tag.Location.Move(revit.doc.GetElement(view.ViewId).ViewDirection)
            try:
                tag.Location.Move(revit.doc.GetElement(view.ViewId).UpDirection)
                tag.Location.Move(DB.XYZ(0.1,0.1,0.1))
                tag.LeaderEnd += revit.doc.GetElement(view.ViewId).UpDirection
            except Exception as e:
                print (e)
            revit.doc.Regenerate()
        with revit.Transaction("#2"):
            try:
                tag.Location.Move(-1*revit.doc.GetElement(view.ViewId).UpDirection)
                tag.Location.Move(DB.XYZ(-0.1,-0.1,-0.1))
                tag.LeaderEnd -= revit.doc.GetElement(view.ViewId).UpDirection
                tag.TagHeadPosition.Add(DB.XYZ.Zero)
            except Exception as e:
                print (e)

            if tag.TagText != old_text:
                print("Tag content refreshed as {}".format(tag.TagText))
        with revit.Transaction("#3"):
            if pin_condition:
                tag.Pinned = True
        """
        with revit.Transaction('#1'):
            tag.Location.Move(DB.XYZ(10, 10, 10))
        #print(str(tag.Id)+ " moved out")
        with revit.Transaction('#2'):
            tag.Location.Move(DB.XYZ(-10, -10, -10))
        """
        #print(str(tag.Id)+ " moved back")
        
@ERROR_HANDLE.try_catch_error
def main():
    #selection = revit.get_selection()
    sel_sheets = forms.select_sheets(title='Select Sheets That Have The Tags You Want To ~~Shake~~')

    if sel_sheets:
        #selection.set_to(sel_sheets)
        target_views = []
        for sheet in sel_sheets:
            target_views.extend(get_views_from_sheet(sheet))
    else:
        script.exit()

    #print(target_views) # this line is used to debug

    print('Shaking Tags in {} views'.format(len(target_views)))
    with revit.TransactionGroup('Shake Tags'):
        for idx, view in enumerate(target_views):
            shake_tags(view)
            output.update_progress(idx+1, len(target_views))

    print('All Tags where shaken...')






##############################################################
if __name__ == '__main__':
    main()