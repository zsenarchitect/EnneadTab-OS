#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "A drafter that allow you to take advantage of Rhino fast editing power. You can operate however you want for crvs and surfaces in Rhino, and transfer those content to Revit detail lines and filled regions with matching linestyle and filled region type.\n\nSome Rhino command to consider:\n+Trim\n+Split\n+Fillet\n+CurveBoolean\n+EditControlPoints\n+Surface trim/split.\n\nIt also support nurbs crv or srf with nurbs edge, and it support AreaBoundaryLine and RoomSeperationLine drafting."
__title__ = "Rhino Drafter"
__youtube__ = r"https://youtu.be/dYeVpdXsMYM"
__tip__ = True

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException



from pyrevit.revit import ErrorSwallower
from pyrevit import script, forms


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_EXPORT, REVIT_FORMS, REVIT_UNIT, REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import EXE, DATA_FILE, DATA_CONVERSION, NOTIFICATION, IMAGE, SOUND, TIME, ERROR_HANDLE, FOLDER


import traceback

import os
import math
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True


def is_elevation_view():
    return doc.ActiveView.ViewDirection.DotProduct(DB.XYZ(0,0,1)) == 0



def convert_unit(x):
    global RHINO_UNIT
    #print RHINO_UNIT
    # why there are two versions....Becasue one system(left) comes from older manual maping, one system(right) comes from newer mapping based on DB.ExportUnit Enum. 
    if RHINO_UNIT == "Millimeters" or  RHINO_UNIT == "Millimeter":
        return REVIT_UNIT.mm_to_internal(float(x))

    if RHINO_UNIT == "Feet" or RHINO_UNIT == "Foot":
        return float(x)

    if RHINO_UNIT == "Inches" or RHINO_UNIT == "Inch":
        return float(x) /12


def get_doc_create():
    if doc.IsFamilyDocument:
        #EA_UTILITY.print_note("it is family doc")
        doc_create = doc.FamilyCreate
    else:
        #EA_UTILITY.print_note("it is project doc")
        doc_create = doc.Create

    return doc_create


def group_contents(new_elements):
    new_elements = filter(lambda x: x is not None, new_elements)
    if len(new_elements) == 0:
        return

    new_element_ids = [x.Id for x in new_elements]
    t = DB.Transaction(doc, "grouping content")
    t.Start()
    doc_create = get_doc_create()
    try:
        with ErrorSwallower() as swallower:
            group = doc_create.NewGroup(DATA_CONVERSION.list_to_system_list(new_element_ids))

            group.GroupType.Name = "EA_Rhino_Drafting_Transfer_({}_{})".format(doc.ActiveView.Name,
                                                                                TIME.get_formatted_current_time())
    except:
        NOTIFICATION.messenger("Cannot make the group of the new draft element but they are still there.")
    t.Commit()


def process_layer_data(layer, contents):
    """contents[id] = {type: line, construct_info:(pt0, pt1)}"""



    if "Curves" in layer:
        linestyle_name = layer.replace("OUT::Curves::", "")
        abstract_crvs = [get_abstract_crv_from_crv(crv_obj_info) for crv_obj_info in contents ]

        doc_create = get_doc_create()
        if linestyle_name in ["<Room Separation>","<Area Boundary>"] :
            level_id = doc.ActiveView.GenLevel.Id
            sketch_plane = DB.SketchPlane.Create(doc, level_id)

            move_vec = DB.XYZ(0,0,sketch_plane.GetPlane().Origin.Z)
            transform = DB.Transform.CreateTranslation(move_vec)
            abstract_crvs = [x.CreateTransformed (transform) for x in abstract_crvs if x is not None]




            #print abstract_crvs
            #print crv_arr
            if "<Area Boundary>" == linestyle_name:

                return [doc_create.NewAreaBoundaryLine  (sketch_plane, crv, doc.ActiveView) for crv in abstract_crvs]

            else:
                crv_arr = DB.CurveArray()
                for abstract_crv in abstract_crvs:
                    crv_arr.Append(abstract_crv)

                sp_lines_arr = doc_create.NewRoomBoundaryLines (sketch_plane, crv_arr, doc.ActiveView)
                #print list(rm_sp_lines_arr)
                return  list(sp_lines_arr)

                #model_crvs = [DB.ElementTransformUtils.MoveElement (doc, x.Id, move_vec) for x in model_crvs]


        else:
            try:
                detail_crvs = [doc_create.NewDetailCurve(doc.ActiveView, abstract_crv) for abstract_crv in abstract_crvs if abstract_crv]
            except Exception as e:
                NOTIFICATION.messenger(main_text = "Error in creating detail crvs:\n{}".format(e))
                return []
            for detail_crv in detail_crvs:
                detail_crv.LineStyle = REVIT_SELECTION.get_linestyle(doc, linestyle_name)
            return detail_crvs


    if "FilledRegion" in layer:
        filled_region_name = layer.replace("OUT::FilledRegion::", "")
        return [create_filled_region_from_srf(filled_region_name, srf_obj_info) for srf_obj_info in contents ]

def get_abstract_crv_from_crv(obj_info):
    #print construct_info
    type, geo_data = obj_info["type"], obj_info["construct_info"]

    if type == "line":
        return create_abstract_line(geo_data)

    if type == "arc":
        return create_abstract_arc(geo_data)

    if type == "circle":
        return create_abstract_circle(geo_data)

    if type == "nurbs_crv":
        return create_abstract_nurbs(geo_data)


def create_abstract_line(geo_data):
    
    pt0, pt1 = geo_data[0], geo_data[1]
    x0, y0, z0 = pt0
    x1, y1, z1 = pt1

    x0, y0, z0, x1, y1, z1 = [convert_unit(x) for x in [x0, y0, z0, x1, y1, z1]]

    for x in [x0, y0, z0, x1, y1, z1]:
        if x is None:
            raise "Find None value in data returned.\n{}".format([x0, y0, z0, x1, y1, z1])



    if is_elevation_view():
        #assume current view is a section/elevation view
        #x value from data is the distance it travel from origion in view right direction
        # y value from data is the Z in real space
        #z value is alwasy 0
        pt0 = doc.ActiveView.RightDirection * x0 + DB.XYZ(0,0,y0)
        pt1 = doc.ActiveView.RightDirection * x1 + DB.XYZ(0,0,y1)

    else:
        #assume current view is a plan view
        #x, y value from data is the distance it travel from origion in view right and up direction
        #z value is alwasy 0
        pt0 = doc.ActiveView.RightDirection * x0 + doc.ActiveView.UpDirection * y0
        pt1 = doc.ActiveView.RightDirection * x1 + doc.ActiveView.UpDirection * y1
    #print pt0, pt1
    try:
        line = DB.Line.CreateBound(pt0, pt1)
    except Exception as e:
        print ("Cannot create line becasue: " + str(e))
        line = None
    #print line
    return line

def create_abstract_arc(geo_data):


    pt0, pt1, pt2 = geo_data[0], geo_data[1], geo_data[2]
    x0, y0, z0 = pt0
    x1, y1, z1 = pt1
    x2, y2, z2 = pt2

    x0, y0, z0, x1, y1, z1, x2, y2, z2 = [convert_unit(x) for x in [x0, y0, z0, x1, y1, z1, x2, y2, z2]]


    if is_elevation_view():
        pt0 = doc.ActiveView.RightDirection * x0 + DB.XYZ(0,0,y0)
        pt1 = doc.ActiveView.RightDirection * x1 + DB.XYZ(0,0,y1)
        pt2 = doc.ActiveView.RightDirection * x2 + DB.XYZ(0,0,y2)

    else:
        pt0 = doc.ActiveView.RightDirection * x0 + doc.ActiveView.UpDirection * y0
        pt1 = doc.ActiveView.RightDirection * x1 + doc.ActiveView.UpDirection * y1
        pt2 = doc.ActiveView.RightDirection * x2 + doc.ActiveView.UpDirection * y2
    #print pt0, pt1
    try:
        arc = DB.Arc.Create(pt0, pt2, pt1)#start, end, midpt
    except Exception as e:
        print ("Cannot create arc becasue: " + str(e))
        arc = None
    #print arc
    return arc

def create_abstract_circle(geo_data):


    pt0, r = geo_data[0], geo_data[1]
    #print geo_data
    x0, y0, z0 = pt0


    x0, y0, z0, r = [convert_unit(x) for x in [x0, y0, z0, r]]




    if is_elevation_view():

        pt0 = doc.ActiveView.RightDirection * x0 + DB.XYZ(0,0,y0)


    else:
        pt0 = doc.ActiveView.RightDirection * x0 + doc.ActiveView.UpDirection * y0


    plane = DB.Plane.CreateByOriginAndBasis (pt0, doc.ActiveView.RightDirection, doc.ActiveView.UpDirection)
    try:
        circle = DB.Arc.Create(plane, r, startAngle = 0, endAngle = 2 * math.pi)# make circle
    except Exception as e:
        print ("Cannot create circle becasue: " + str(e))
        circle = None
    #print arc
    return circle

#print geo_data
def convert_pt(pt):
    x0, y0, z0 = pt[0], pt[1], pt[2]
    x0, y0, z0 = [convert_unit(x) for x in [x0, y0, z0]]
    pt0 = doc.ActiveView.RightDirection * x0 + doc.ActiveView.UpDirection * y0
    return pt0
    """
    if is_elevation_view():
        # pt0 = doc.ActiveView.RightDirection * x0 + DB.XYZ(0,0,y0)
    else:
        pt0 = doc.ActiveView.RightDirection * x0 + doc.ActiveView.UpDirection * y0
    """

    #return DB.XYZ(pt0.X, pt0.Y, pt0.Z)


def create_abstract_nurbs(geo_data):





    pts = [convert_pt(pt) for pt in geo_data]

    #pts = [DB.XYZ(convert_unit(pt[0]),convert_unit(pt[1]),convert_unit(pt[2])) for pt in geo_data]
    #print pts

    """
    ipts = System.Collections.Generic.List[DB.XYZ]()
    iweights = System.Collections.Generic.List[System.Double]()
    for pt in pts:
    	ipts.Add(pt)
    	iweights.Add(2)
    """


    # print pts
    pt_count = len(pts)
    # print pt_count
    pts = DATA_CONVERSION.list_to_system_list(pts, type = "XYZ", use_IList = False)

    weights = [1.0] * pt_count
    # print weights
    weights = DATA_CONVERSION.list_to_system_list(weights, type = "Double", use_IList = False)
    #print weights



    # print pts
    # print weights
    try:
        nurbs = DB.NurbSpline.CreateCurve(pts, weights)# make nurbs
    except Exception as e:
        print ("Cannot create nurbs becasue: " + str(e))
        nurbs = None
    #print arc
    return nurbs


def create_filled_region_from_srf(filled_region_name, obj_info):
    srf_infoes = obj_info["construct_info"]
    DB_crv_loops = []
    for srf_info in srf_infoes:
        crv_loop = []
        for crv_obj_info in srf_info:
            #print crv_obj_info
            abstract_crv = get_abstract_crv_from_crv(crv_obj_info)
            crv_loop.append(abstract_crv)

        DB_crv_loop = DB.CurveLoop.Create(list(crv_loop))
        DB_crv_loops.append(DB_crv_loop)


    crv_loops = DATA_CONVERSION.list_to_system_list(DB_crv_loops, type = "CurveLoop", use_IList = False)
    filled_region_type = REVIT_SELECTION.get_filledregion_type(doc, filled_region_name)
    if not filled_region_type:
        NOTIFICATION.messenger("Cannot find the type of filled region in your project: {}\nI will use a default type instead.".format(filled_region_name),)
        filled_region_type = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).FirstElement()
    filled_region = DB.FilledRegion.Create(doc,
                                            filled_region_type.Id,
                                            doc.ActiveView.Id,
                                            crv_loops)
    return filled_region

@ERROR_HANDLE.try_catch_error()
def transfer_in_draft(rhino_unit, is_grouping):

    # global RHINO_UNIT
    # RHINO_UNIT = rhino_unit




    # get dump data
    file_path = FOLDER.get_filepath_in_special_folder_in_EA_setting("Local Copy Dump", "EA_DRAFTING_TRANSFER.json")
    datas = DATA_FILE.read_json_as_dict(file_path)
    if not datas:
        NOTIFICATION.messenger ("There is no data saved. Have you exported from the Rhino?")
        return




    # map: for each data, create line, or arc detail line
    t = DB.Transaction(doc, "transfering rhino drafting")
    t.Start()

    new_elements = []
    for layer, contents in datas.items():
        #print data
        new_elements.extend(process_layer_data(layer, contents))

    t.Commit()

    # group new coming with time stamp
    if is_grouping:
        group_contents(new_elements)




    NOTIFICATION.toast(main_text = "Draft content created!")
    
   
    SOUND.play_sound("sound_effect_popup_msg1.wav")


# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(*self.kwargs)
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"



# A simple WPF form used to call the ExternalEvent
class RhinoDraft_UI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):

        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.simple_event_handler = SimpleEventHandler(transfer_in_draft)

        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.simple_event_handler)
        #print "preaction done"
        #print self.simple_event_handler
        #print self.simple_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'rhino_draft_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)
        self.subtitle.Text = "A helper window that transfer draft content between Rhino and Revit. You might do any combination of lines, polylines, arcs and freeform nurbs for detail lines, area boundary lines, room seperation lines and edges of filled regions."

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.set_image_source(self.rhino_button_icon_1, "drafting.png")
        self.set_image_source(self.rhino_button_icon_2, "drafting.png")
        self.combobox_dwg_setting.ItemsSource = self.get_dwg_settings()
        self.combobox_dwg_setting.SelectedItem = self.combobox_dwg_setting.ItemsSource[0]

        self.Show()



    @ERROR_HANDLE.try_catch_error()
    def get_dwg_settings(self, setting_name = None):
        existing_dwg_settings = DB.FilteredElementCollector(doc).OfClass(DB.ExportDWGSettings).WhereElementIsNotElementType().ToElements()

        if len(existing_dwg_settings) == 0:
            return ["No available dwg setting..."]

        if not setting_name:
            return [x.Name for x in existing_dwg_settings]
        else:
            for x in existing_dwg_settings:
                if x.Name == setting_name:
                    return x


    @ERROR_HANDLE.try_catch_error()
    def export_view_click(self, sender, args):
        if str(doc.ActiveView.ViewType) not in ["Detail", 
                                                "Section", 
                                                "AreaPlan", 
                                                "Elevation", 
                                                "FloorPlan", 
                                                "CeilingPlan", 
                                                "DraftingView"]:
            self.debug_textbox.Text = "Cannot do it in view type " + str(doc.ActiveView.ViewType)
            NOTIFICATION.messenger(main_text = "Cannot export in view type " + str(doc.ActiveView.ViewType))
            return


        self.debug_textbox.Text = ""
        crop_region_shape_manager = doc.ActiveView.GetCropRegionShapeManager ()
        if crop_region_shape_manager.Split :
            REVIT_FORMS.notification(main_text = "The view appears to have view break.", sub_text = "You can still draft in Rhino, but be aware that Rhino will not understand Revit view break in dwg, so when importing back, the draft might see partial shift.", self_destruct = 10)



        if self.combobox_dwg_setting.SelectedItem == "No available dwg setting...":
            NOTIFICATION.messenger(main_text = "No valid dwg setting selected.\nCannot export without a valid dwg setting.")
            return



        if self.checkbox_open_new_rhino.IsChecked:
            self.open_template_rhino(doc)


        #dwg_setting = self.get_dwg_settings(self.combobox_dwg_setting.SelectedItem)
        #print dwg_setting
        #DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, dwg_setting.Name)

        file_name = "EA_TRANSFER_DRAFT_BACKGROUND"
        view = doc.ActiveView
        output_folder = FOLDER.get_EA_local_dump_folder()
        REVIT_EXPORT.export_dwg(view, file_name, output_folder, self.combobox_dwg_setting.SelectedItem)

        self.update_global_unit()


        self.save_export_setting()

    def update_global_unit(self):
        DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, self.combobox_dwg_setting.SelectedItem)
        if not DWG_option:
            return
        export_unit = DWG_option.TargetUnit
        """
        Default
        Inch	
        Foot	
        Millimeter	
        Centimeter	
        Meter
        """
        global RHINO_UNIT
        RHINO_UNIT = str(export_unit)
        #print RHINO_UNIT

    @property
    def revit_unit(self):
        try:
            revit_unit = doc.GetUnits().GetFormatOptions (DB.UnitType.UT_Length ).DisplayUnits
            revit_unit =  str(revit_unit).replace("DUT_", "").lower()
            #print revit_unit
        except:

            revit_unit = doc.GetUnits().GetFormatOptions (REVIT_UNIT.lookup_unit_spec_id("length") ).GetUnitTypeId().TypeId
            revit_unit = str(revit_unit).split("-")[0].split("unit:")[1]
            #print revit_unit
        """
        possible revit unit
        feet_fractional_inches
        feetFractionalInches
        feet
        inches
        millimeters
        """

        """
        possible rhin ounit
        feet, feet & inches
        inches, feet & inches
        feet
        inches
        millimeters
        """
        if "feet_fractional_inches" == revit_unit or "feetFractionalInches" == revit_unit:
            revit_unit = "feet, feet & inches"

        return revit_unit

    @property
    def final_file(self):
        # open template
        #rhino_template_folder = r"{}\AppData\Roaming\McNeel\Rhinoceros\7.0\Localization\en-US\Template Files".format(os.environ["USERPROFILE"])



        import os
        rhino_template_folder = "{}\Rhino Template Files".format(os.path.dirname(os.path.abspath(__file__)))

        # note:
        # Use "Draft Transfer" from EnneadTab for Rhino to continue working.

        for template in FOLDER.get_filenames_in_folder(rhino_template_folder):
            #print template
            if self.revit_unit in template.lower():
                break


        self.template_file_path = rhino_template_folder + "\\" + template

        #FOLDER.copy_file_to_folder(file_path, FOLDER.get_EA_local_dump_folder())
        file_path = FOLDER.get_EA_local_dump_folder() + "\\" + template
        final_file = file_path.replace(".3dm", "_{}.3dm".format(doc.ActiveView.Name
                                                                .replace("/","-")))


        return final_file

    def open_template_rhino(self, doc):
        final_file = self.final_file
        try:
            FOLDER.copy_file(self.template_file_path, final_file)
        except:
            NOTIFICATION.messenger(main_text = "Cannot start current file, there might be illegal character\nfor window filename from your view name.")
            NOTIFICATION.duck_pop(main_text = "..Or your previous export for rhino of same view is not closed.")
            return
        
        EXE.open_file_in_default_application(final_file)
        NOTIFICATION.toast(main_text = "New empty Rhino is starting...")

    def save_export_setting(self):
        line_style_names = REVIT_SELECTION.get_all_linestyles(doc)
        filled_region_type_names = REVIT_SELECTION.get_all_filledregion_types(doc)
        OUT = dict()
        OUT["line_styles"] = line_style_names
        OUT["filled_region_type_names"] = filled_region_type_names
        OUT["revit_unit"] = self.revit_unit
        OUT["final_file"] = self.final_file
        file = FOLDER.get_EA_dump_folder_file("EA_TRANSFER_DRAFT_SETTING.json")
        DATA_FILE.set_data(OUT, file)


    @ERROR_HANDLE.try_catch_error()
    def transfer_in_click(self, sender, args):


        if self.revit_unit == "millimeters":
            rhino_unit = "Millimeters"
        elif self.revit_unit in ["feet, feet & inches", "feet"]:
            rhino_unit = "Feet"
        elif self.revit_unit in ["inches, feet & inches", "inches"]:
            rhino_unit = "Inches"
        else:
            NOTIFICATION.toast(main_text = " bad unit, talk to SZ")
            return


        self.update_global_unit()

        is_grouping = self.checkbox_is_grouping.IsChecked
        self.simple_event_handler.kwargs = rhino_unit, is_grouping
        self.ext_event.Raise()
        res = self.simple_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    def handleclick(self, sender, args):
        print ("surface clicked")

    def close_click(self, sender, args):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


    def play_demo_click(self, sender, args):

        os.startfile(__youtube__)
        


@ERROR_HANDLE.try_catch_error()
def main():

    modeless_form = RhinoDraft_UI()



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    
