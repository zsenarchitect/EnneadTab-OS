#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Recreate a filled region using the same shape as the floor."
__title__ = "40_Floor to Filled region"
__youtube__ = "https://youtu.be/ieGPe-3ACw4"
import time
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument
from pyrevit.framework import List



def OLD_sort_crv(crvs):#work only with single loop-like, if double loop then it ewill fail
    current_crv = crvs[0]
    end_pt = current_crv.GetEndPoint(1)
    sorted_crv = [current_crv]
    i = 0#safety count
    while len(sorted_crv) < len(crvs):
    #for i, crv in enumerate(crvs):

        for other_crv in crvs:
            if current_crv == other_crv:#skip itself
                #print "self"
                continue
            elif end_pt.IsAlmostEqualTo( other_crv.GetEndPoint(0) ):#this is the next curve
                #print "found"
                sorted_crv.append(other_crv)
                current_crv = other_crv
                end_pt = current_crv.GetEndPoint(1)
                #print sorted_crv
                break
            else:#not the next crv
                #print "not this one"
                pass

        i += 1
        if i > 500:
            break
    return sorted_crv


def create_filled_region_from_floor(floor, filled_region_type, view_id):
    """
    make temp copy and reset copy shape, main prolblem is the copy does not know the other hole cut
    """


    def get_curveloop_method1():
        slab_editor = floor.SlabShapeEditor
        creases = slab_editor.SlabShapeCreases
        # print creases
        crvs = []
        for crease in creases:
            # print crease
            if crease.CreaseType == DB.SlabShapeCreaseType.Boundary:
                # print "add boundary"
                crvs.append(crease.Curve)

        crvs = sort_crv(crvs)
        curveloop = DB.CurveLoop.Create(EA_UTILITY.list_to_system_list(crvs, type = "Curve"))
        # return EA_UTILITY.list_to_system_list([crvs], type = "CurveLoop")
        return List[DB.CurveLoop]([curveloop]) #feed filled region as List objectr

    def get_curveloop_method2():
        def get_top_face(solid):
            faces = solid.Faces
            for face in faces.GetEnumerator():
                # print str(face.GetType())
                face_normal = face.ComputeNormal(DB.UV())
                # print face_normal
                if face_normal.DotProduct(DB.XYZ(0,0,1)) - 1 < 0.001:
                    # print "top face = {}".format(face)
                    return face
            pass


        t = DB.Transaction(doc, "copy floor and reset shape")
        t.Start()
        copy_floor_id = DB.ElementTransformUtils.CopyElement (doc, floor.Id, DB.XYZ(0,0,-100))[0]
        copy_floor = doc.GetElement(copy_floor_id)
        slab_editor = copy_floor.SlabShapeEditor
        slab_editor.ResetSlabShape()
        t.Commit()

        opt = DB.Options()
        opt.IncludeNonVisibleObjects = True
        opt.ComputeReferences = True
        floor_geo = copy_floor.get_Geometry(opt)
        geo_objs = floor_geo.GetEnumerator()
        for geo_obj in geo_objs:
            # print geo_obj
            if "Solid" in str(geo_obj.GetType()):
                break
        top_face = get_top_face(geo_obj)

        t = DB.Transaction(doc, "delete copy floor")
        t.Start()
        doc.Delete(copy_floor.Id)
        t.Commit()

        curveloop = top_face.GetEdgesAsCurveLoops ()
        return curveloop


    # curveloop = get_curveloop_method1()
    curveloop = get_curveloop_method2()
    # print curveloop
    t = DB.Transaction(doc, "make new filled region")
    t.Start()

    new_filled_region = DB.FilledRegion.Create(doc,
                                                filled_region_type.Id,
                                                view_id,
                                                curveloop)

    new_filled_region.SetLineStyleId (get_invisible_style().Id)

    setting = DB.OverrideGraphicSettings ()
    setting.SetSurfaceForegroundPatternVisible (False)
    setting.SetSurfaceBackgroundPatternVisible (False)
    view = doc.GetElement(view_id)
    view.SetElementOverrides (floor.Id, setting)

    t.Commit()
    global new_filled_region_data
    new_filled_region_data.append([floor, new_filled_region, view_id])
    # append_new_link(floor, new_filled_region, view_id)
    return

def try_create_filled_region_from_floor(floor, filled_region_type, view_id):



    def get_curveloop_method1():
        slab_editor = floor.SlabShapeEditor
        creases = slab_editor.SlabShapeCreases
        # print creases
        crvs = []
        for crease in creases:
            # print crease
            if crease.CreaseType == DB.SlabShapeCreaseType.Boundary:
                # print "add boundary"
                crvs.append(crease.Curve)

        crvs = sort_crv(crvs)
        curveloop = DB.CurveLoop.Create(EA_UTILITY.list_to_system_list(crvs, type = "Curve"))
        # return EA_UTILITY.list_to_system_list([crvs], type = "CurveLoop")
        return List[DB.CurveLoop]([curveloop]) #feed filled region as List objectr

    def get_curveloop_method2():
        def get_top_face(solid):
            faces = solid.Faces
            for face in faces.GetEnumerator():
                # print str(face.GetType())
                face_normal = face.ComputeNormal(DB.UV())
                # print face_normal
                if face_normal.DotProduct(DB.XYZ(0,0,1)) - 1 < 0.001:
                    # print "top face = {}".format(face)
                    return face
            pass


        t = DB.Transaction(doc, "temp reset shape")
        t.Start()

        slab_editor = floor.SlabShapeEditor
        slab_editor.ResetSlabShape()


        opt = DB.Options()
        opt.IncludeNonVisibleObjects = False
        opt.ComputeReferences = False
        floor_geo = floor.get_Geometry(opt)
        geo_objs = floor_geo.GetEnumerator()
        for geo_obj in geo_objs:
            # print geo_obj
            if "Solid" in str(geo_obj.GetType()):
                break
        top_face = get_top_face(geo_obj)




        curveloop = top_face.GetEdgesAsCurveLoops ()
        t.RollBack()
        print(curveloop)
        return curveloop


    # curveloop = get_curveloop_method1()
    curveloop = get_curveloop_method2()
    # print curveloop
    t = DB.Transaction(doc, "make new filled region")
    t.Start()

    new_filled_region = DB.FilledRegion.Create(doc,
                                                filled_region_type.Id,
                                                view_id,
                                                curveloop)

    new_filled_region.SetLineStyleId (get_invisible_style().Id)
    t.Commit()
    global new_filled_region_data
    new_filled_region_data.append([floor, new_filled_region, view_id])
    # append_new_link(floor, new_filled_region, view_id)
    return

def get_element_link_file():
    file = r"I:\2135\0_BIM\10_BIM Management\Filled Region_Floor Links\Filled Region_Floor_Link_{}.txt".format(doc.Title.split("HQ_")[1])
    return file

def OLD_append_new_link(floor, filled_region, view_id):
    filepath = get_element_link_file()

    data = "{}|{}|{}|{}".format(floor.UniqueId,
                                filled_region.UniqueId,
                                doc.GetElement(filled_region.GetTypeId()).UniqueId,
                                doc.GetElement(view_id).UniqueId)
    with open(filepath, "a") as f:
        f.write(data)
        f.write("\n")
    time.sleep(0.1)

def write_new_data(new_filled_region_data):
    filepath = get_element_link_file()

    with open(filepath, "a") as f:
        for data in new_filled_region_data:
            floor, filled_region, view_id = data
            line = "{}|{}|{}|{}".format(floor.UniqueId,
                                        filled_region.UniqueId,
                                        doc.GetElement(filled_region.GetTypeId()).UniqueId,
                                        doc.GetElement(view_id).UniqueId)
            f.write(line)
            f.write("\n")

    pass

def update_existing_filled_regions():
    tg = DB.TransactionGroup(doc, "update filled regions by record")
    tg.Start()
    if len(uidoc.Selection.GetElementIds ()) != 0:
        EA_UTILITY.dialogue(main_text = "No preslection needed to update.", sub_text = "Selection will be ignored.")

    file_path = get_element_link_file()
    datas = EA_UTILITY.read_txt_as_list(file_path)


    # make empty file becasue i will regenerate all-------> too dangerous to empty list directly maybe memberize the content and once no error in final step to remove front end
    # EA_UTILITY.save_list_to_txt([], get_element_link_file())


    """
    note:  one floor can have multiple filled region..

    case 1:     floor yes, filled region yes ---> delete filled region, regenerate filled region in original view---->no user wanring
    case 2:     floor no, filled region yes ---> delete filled region, do not regenerate ---> tell user it will delete filled region in which view
    case 3:     floor yes, filled region no ---> regenerate filled region ---> tell user it will re-make filled region in original view
    case 4:     floor no, filled region no ---> do nothing ----> tell user both are gone

    conclusion:
    # delete filled region no matter what
    # generate filled region as long as there is floor, use recorded view
    """
    for data in datas:
        floor_id, filled_region_id, filled_region_type_id,  view_id = data.split("|")

        floor = doc.GetElement(floor_id)
        filled_region = doc.GetElement(filled_region_id)
        filled_region_type = doc.GetElement(filled_region_type_id)
        view = doc.GetElement(view_id)
        exist_floor = floor is not None
        exist_filled_region = filled_region is not None

        try:
            t = DB.Transaction(doc, "delete old filled region")
            t.Start()
            doc.Delete(filled_region.Id)

        except Exception as e:
            EA_UTILITY.print_note(e)
        finally:
            t.Commit()


        if exist_floor and exist_filled_region:
            EA_UTILITY.print_note( "floor and filled region both exist, will just regenerate filled_region")
            create_filled_region_from_floor(floor, filled_region_type, view.Id)

        elif not exist_floor and exist_filled_region:
            print("Floor '{}' is no longer in the file. Associated filled region will be removed".format(floor_id))

        elif exist_floor and not exist_filled_region:
            print("Filled Region '{}' is no longer in the file, but source floor exist, will regenerate.".format(filled_region_id))
            create_filled_region_from_floor(floor, filled_region_type, view.Id)

        elif not exist_floor and not exist_filled_region:
            print("Both floor and associateed filled region is gone.")

        else:
            print("Things go wrong")

    write_new_data(new_filled_region_data)
    current_datas = EA_UTILITY.read_txt_as_list(file_path)
    # EA_UTILITY.print_note( current_datas)
    # EA_UTILITY.print_note( current_datas[len(datas):])
    new_data = list(set(current_datas) - set(datas))
    EA_UTILITY.save_list_to_txt(new_data, file_path, end_with_new_line = True)
    tg.Commit()


def make_new_filled_regions():
    # get floor in selection, check is_floor
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]
    for item in selection:
        if item.GetType() != DB.Floor:
            EA_UTILITY.dialogue(main_text = "Only accepting floors in selection.")
            script.exit()
    floors = selection



    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{}".format(self.LookupParameter('Type Name').AsString())
    filled_region_types = list(DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).WhereElementIsElementType().ToElements())
    filled_region_types.sort(key = lambda x: x.LookupParameter('Type Name').AsString())

    filled_region_type = forms.SelectFromList.show([MyOption(x) for x in filled_region_types],
                                                    title = "Pick the filled region type to use.")





    tg = DB.TransactionGroup(doc, "Make filled region from floor")
    tg.Start()
    """
    for floor in floors:

        try:
            create_filled_region_from_floor(floor)
        except Exception as e:
            print("Skip filled region creation on one floor element")
            print (e)
    """
    map(lambda x: create_filled_region_from_floor(x, filled_region_type, doc.ActiveView.Id), floors)
    write_new_data(new_filled_region_data)
    tg.Commit()

def get_invisible_style():
    graphic_styles = DB.FilteredElementCollector(doc).OfClass(DB.GraphicsStyle ).ToElements()
    for style in graphic_styles:
        if "Invisible" in style.Name:
            return style



################## main code below #####################
output = script.get_output()
output.close_others()
new_filled_region_data = []
# tool 1 create: if not created, floor will make a filled region and link the stable ID between,
# tool 2 update: for all floor in file, find the linked filled region, update them
res = EA_UTILITY.dialogue(main_text = "I want to [...] filled regions", options = [["create", "based on selected floor"], ["update previously generated","will try to update all filled region generated by this tool.(beta)"]])


"""
------------add third functyion to remove selecvted filled region from list
"""
if res == "create":
    make_new_filled_regions()
else:
    update_existing_filled_regions()


#ideas:
"""
IDEAS
    - wall to room seperation line or area boubnary line
    - copy material defination, object style definiation, object style material assignment, template defination across open docs or from link
    - net bound for complex curtain panel inside
    -rename family/type in multiple open doc
    -report dim that is not whole number

    - deep purge sub family




    - what is my view direvtion vector, what is this line vector
    - override graphic for all user keynote as blue color,

    - ceiling family alway use ceiling line but switch head up and down becasue usally you dim to the ceiling dash

    - annotater family add lines for eng and CN as interger to control the left align location

    - RENAME GROUP BY CURRENT VIEW---- group usage report

    - flusing , bolt, fire stoper, plate, hanger, angle, tubes

    - MATCH SLAB BOUDARY PINK LINES

    - INUSLATED BACK PAN , OPTION TO USE CL AND SIDE Line
    - TUBE OPTION TO US CL AND EDGE



    - add section, elevation, to temp vision tool

    - extract CAD lines by layer and assign to object style

    - ANNOTATION MODE -- ONLY ABLE TO SELECT 2D ELEMENTS

    - GUI recent used family type, drag and drop

    - IF FAMILY NAME = TYPE NAME, THAT IS NOT GOOD, RENAME THE TYPE NAME TO "DD"

    - PERMITION TO DELEETE ELEMENT

    - mark element as non-editable, soyou dont accidentally go inside a family_doc


    - detauil item object style:
        insulation, water proof, profil extieor, interior, cut but not important, center, slab cut, see but not important....

    - proejct line style
        $$ predefined profile, ceiling, waterproffing, slab_cut, column cut, CL line, ceiling

    - label unused legend and schedule

    - CHANGE  $LINE STYLE TO INVISIBLE(USFUL FOR FILLED REGION)
    AND CHANGE ALL INVISUABELT O T$$ea LINE SO YOU CAN CHECK THE BOUDNARY

    - SHORT LIST LOCAL OVERRIDE



bip = BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS
provider = ParameterValueProvider(ElementId(bip))
evaluator = FilterStringEquals();
rule = FilterStringRule(provider, evaluator, "aaa", False);
filter = ElementParameterFilter(rule);
walls = FilteredElementCollector(doc).OfClass(Wall).WherePasses(filter).ToElements()

t = DB.Transaction(doc , "action")
t.Start()
#do work
t.Commit()

__all__ = ('pick_element', 'pick_element_by_category',
           'pick_elements', 'pick_elements_by_category',
           'get_picked_elements', 'get_picked_elements_by_category',
           'pick_edge', 'pick_edges',
           'pick_face', 'pick_faces',
           'pick_linked', 'pick_linkeds',
           'pick_elementpoint', 'pick_elementpoints',
           'pick_point', 'pick_rectangle', 'get_selection_category_set',
           'get_selection')

doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = revit.doc
uidoc = revit.uidoc




global

########note to self to research
#GUI window?
#how did select from para window show extra icon  instance/type by list?
#try to search from directory the name used for revit tab manager?


fake delete Transaction
    with revit.DryTransaction("Search for linked elements"):
        linked_elements_list = revit.doc.Delete(selection.first.Id)

from playsound import playsound
playsound('/path/to/a/sound/file/you/want/to/play.mp3')

FREQUENTLY_SELECTED_CATEGORIES = [
    DB.BuiltInCategory.OST_Areas,
    DB.BuiltInCategory.OST_AreaTags,
    DB.BuiltInCategory.OST_AreaSchemeLines,
    DB.BuiltInCategory.OST_Columns,
    DB.BuiltInCategory.OST_StructuralColumns,
    DB.BuiltInCategory.OST_Dimensions,
    DB.BuiltInCategory.OST_Doors,
    DB.BuiltInCategory.OST_Floors,
    DB.BuiltInCategory.OST_StructuralFraming,
    DB.BuiltInCategory.OST_Furniture,
    DB.BuiltInCategory.OST_Grids,
    DB.BuiltInCategory.OST_Rooms,
    DB.BuiltInCategory.OST_RoomTags,
    DB.BuiltInCategory.OST_CurtainWallPanels,
    DB.BuiltInCategory.OST_Walls,
    DB.BuiltInCategory.OST_Windows,
    DB.BuiltInCategory.OST_Ceilings,
    DB.BuiltInCategory.OST_SectionBox,
    DB.BuiltInCategory.OST_ElevationMarks,
    DB.BuiltInCategory.OST_Parking,
    DB.BuiltInCategory.OST_GenericModel
    OST_Sheets
    OST_TextNotes
    OST_GenericLines
    OST_Lines
]


remove duplicate from list:
list({x for x in list_raw})

filter(function, sequence)
Parameters:
function: function that tests if each element of a
sequence true or not.
sequence: sequence which needs to be filtered, it can
be sets, lists, tuples, or containers of any iterators.
Returns:
returns an iterator that is already filtered.



from datetime import date
print(date.today())


keynotes = DB.FilteredElementCollector(revit.doc,revit.active_view.Id)\
              .OfCategory(DB.BuiltInCategory.OST_KeynoteTags)\
              .WhereElementIsNotElementType()\
              .ToElements()

WhereElementIsElementType()
#to get element type name
type.LookupParameter("Type Name").AsString()


# ICollections format: System.Collections.Generic.List[DB.date type]([list data])
    shapes = [shapes list]
    shape_collection = System.Collections.Generic.List[DB.ElementId]([x.Id for x in shapes])
    revit.active_view.IsolateElementsTemporary(shape_collection)


##Rhino - Rhino3dmIO

Rhino3dmIO is a subset of RhinoCommon and it gives you access to openNurbs, allowing you to, amongst other things, read and write 3dm files.
>>> from rpw.extras.rhino import Rhino as rc
>>> pt1 = rc.Geometry.Point3d(0,0,0)
>>> pt2 = rc.Geometry.Point3d(10,10,0)
>>> line1 = rc.Geometry.Line(pt1, pt2)
>>> line1.Length
14.142135623730951
>>>
>>> pt1 = rc.Geometry.Point3d(10,0,0)
>>> pt2 = rc.Geometry.Point3d(0,10,0)
>>> line2 = rc.Geometry.Line(pt1, pt2)
>>>
>>> rc.Geometry.Intersect.Intersection.LineLine(line1, line2)
(True, 0.5, 0.5)
>>>
>>> file3dm = f = rc.FileIO.File3dm()
>>> file3md_options = rc.FileIO.File3dmWriteOptions()
>>> file3dm.Objects.AddLine(line1)
>>> filepath = 'c:/folder/test.3dm'
>>> file3dm.Write(filepath, file3md_options)


forms.WPFWindow(xaml_source, literal_string=False, handle_esc=True, set_owner=True)
>>> from pyrevit import forms
>>> layout = '<Window ' \
>>>          'xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" ' \
>>>          'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" ' \
>>>          'ShowInTaskbar="False" ResizeMode="NoResize" ' \
>>>          'WindowStartupLocation="CenterScreen" ' \
>>>          'HorizontalContentAlignment="Center">' \
>>>          '</Window>'
>>> w = forms.WPFWindow(layout, literal_string=True)
>>> w.show()


>>> with ErrorSwallower() as swallower:
>>>     for fam in families:
>>>         revit.doc.EditFamily(fam)
>>>         if swallower.get_swallowed():
>>>             logger.warn("Warnings swallowed")

forms.alert(msg, title=None, sub_msg=None, expanded=None, footer='', ok=True, cancel=False, yes=False, no=False, retry=False, warn_icon=True, options=None, exitscript=False)
forms.ask_for_color(default=None)
forms.ask_for_one_item(items, default=None, prompt=None, title=None, **kwargs)
forms.ask_for_string(default=None, prompt=None, title=None, **kwargs)
forms.select_family_parameters(family_doc, title='Select Parameters', button_name='Select', multiple=True, filterfunc=None, include_instance=True, include_type=True, include_builtin=True, include_labeled=True)
forms.select_image(images, title='Select Image', button_name='Select')
forms.select_parameters(src_element, title='Select Parameters', button_name='Select', multiple=True, filterfunc=None, include_instance=True, include_type=True, exclude_readonly=True)
forms.select_swatch(title='Select Color Swatch', button_name='Select')
forms.select_views(title='Select Views', button_name='Select', width=500, multiple=True, filterfunc=None, doc=None, use_selection=False)
forms.select_viewtemplates(title='Select View Templates', button_name='Select', width=500, multiple=True, filterfunc=None, doc=None)
forms.toast(message, title='pyRevit', appid='pyRevit', icon=None, click=None, actions=None)

output = pyrevit.output.get_output()
output.print_image(r'C:\image.gif')
print(script.get_script_path())
print(script.get_bundle_files())
print(script.get_bundle_file('triangle.png'))
output.set_width(1500)
output.set_height(900)
output.center()
output.close_others()
#output.open_url("http://dict.cn/")
output.show()
output.print_md(str)----->    https://www.markdownguide.org/basic-syntax/
        bold ====   **text**
        italic ====   *text*
        bold and italic ======   ***text***
        heading =======   ## text   (# biggest, ##### smallest)





no_sheet_views.sort(key = lambda x: x.ViewType, reverse = True)




with forms.WarningBar(title='Pick title corner point'):
    ref_pt = revit.pick_point()




sel_sheets = forms.select_sheets(title='Select Sheets That contain views that you want to do temperory template')



res = forms.alert(options = ["mark title corners at sheets", "remove existing marks from sheets."], msg = "I want to [.....]")

if "remove" in res:
    option = False
elif "mark" in res:
    option = True
else:
    script.exit()



forms.alert(msg = '{0} FILES RENAMED.'.format(sheetcount), sub_msg = fail_text)





from pyrevit import forms
items = ['item1', 'item2', 'item3']
res = forms.SelectFromList.show(context = items, button_name='Select Item')
if res == 'item1':
    do_stuff()
~~~~~
ops = [viewsheet1, viewsheet2, viewsheet3]
res = forms.SelectFromList.show(ops,
                                multiselect=False,
                                name_attr='Name',
                                button_name='Select Sheet')
if res.Id == viewsheet1.Id:
    do_stuff()
~~~
forms.SelectFromList.show(
        {'All': '1 2 3 4 5 6 7 8 9 0'.split(),
         'Odd': '1 3 5 7 9'.split(),
         'Even': '2 4 6 8 0'.split()},
        title='MultiGroup List',
        group_selector_title='Select Integer Range:',
        multiselect=True
    )
~~~
ops = {'Sheet Set A': [viewsheet1, viewsheet2, viewsheet3],
       'Sheet Set B': [viewsheet4, viewsheet5, viewsheet6]}
res = forms.SelectFromList.show(ops,
                                multiselect=True,
                                name_attr='Name',
                                group_selector_title='Sheet Sets',
                                button_name='Select Sheets')
if res.Id == viewsheet1.Id:
    do_stuff()
~~~
from pyrevit import forms

class MyOption(forms.TemplateListItem):
    @property
    def name(self):
        return "Option: {}".format(self.item)

ops = [MyOption('op1'), MyOption('op2', checked=True), MyOption('op3')]
res = forms.SelectFromList.show(ops,
                                multiselect=True,
                                button_name='Select Item')
~~~

selected_views = forms.SelectFromList.show(no_sheet_views,
                                multiselect=True,
                                name_attr='Name',
                                title = "Those views are not on sheet",
                                button_name= "Mark them with 'NoSheet-' prefix",
                                filterfunc=lambda x: x.ViewType not in [DB.ViewType.Legend, DB.ViewType.Schedule])




DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()

.OfCategory(DB.BuiltInCategory.OST_Massing)





with revit.Transaction("Mark NoSheet Views"):
    for view in selected_views:
        new_name = "NoSheet-" + view.Name
        view.Parameter[DB.BuiltInParameter.VIEW_NAME].Set(new_name)





def final_print_table():
	table_data = []
	for item in view_item_collection:
		if item.view_name in view_item_collection_selected:
			#temp_list = [item.critical_level_text, item.view_name, item.line_count]
			temp_list = [ item.critical_level_text, item.view_name, item.line_count, output.linkify(item.id, title = "Go To View")]
			table_data.append(temp_list)
    output.print_table(table_data=table_data,title="Bad Views by Line Count ",columns=[ "Critical Level", "View Name", "Line Count", "View Link"],formats=['', '{}', '{} Lines', '{}'])



output.freeze()
output.unfreeze()
output.self_destruct()
output.set_title()
output.update_progress(cur_value, max_value)
output.add_style('body { color: blue; }')





with forms.ProgressBar(title = "Checking Families, Hold On...({value} of {max_value})", step = pb_step, cancellable = True) as pb:
# initiate the class collection.
	for family in all_families:

		family_item_collection.append(family_item(family))



		global_counter += 1
		if global_counter > limit:
			break

		if pb.cancelled:
			script.exit()
		pb.update_progress(global_counter, limit)


>>> for count, value in enumerate(values):
...     print(count, value)


selection = revit.get_selection()

if len(selection) > 1:
    forms.alert("Please select 1 tags only.")
    script.exit()

if "Tags" not in selection[0].Category.Name:
    forms.alert("This is not a tag.")
    script.exit()


ref_tag = revit.doc.GetElement(get_ref_tag_id())

"""
