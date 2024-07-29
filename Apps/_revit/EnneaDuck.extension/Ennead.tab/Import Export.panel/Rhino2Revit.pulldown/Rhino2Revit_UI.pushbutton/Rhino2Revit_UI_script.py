#!/usr/bin/python
# -*- coding: utf-8 -*-


__doc__ = "A window that allow you to convert .3dm file and .dwg files into native revit family elements.\n\nAllo subCategory assigning per file, you may also add new SubCateogry on the run or simply use the source file name as the subcategory.\n\nSupport all major curve convertion except nurbs curve when part of the control points are not on same CPlane.\n\nSee instruction in the window for more details and features. This tool works best with the EnneadTab for Rhino tool's Rhino2Revit exporter window."
__title__ = "Rhino2Revit"
__tip__ = ["You can get crvs from Rhino into revit family as well, all you need to do to export as dwg in rhino side, and import as dwg in revit family side.\nSee EnneadTab for Rhino LayerPackagre for details",
           __doc__]

from pyrevit import forms
from pyrevit import script
from pyrevit.revit import ErrorSwallower
# from pyrevit import revit #

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import DATA_FILE, NOTIFICATION, IMAGE, ERROR_HANDLE, FOLDER, TIME, LOG

from Autodesk.Revit import DB # pyright: ignore  
import clr
import os
import System
import time
import traceback

# this is needed only becasue when parsing tips from python files, a relative import will fail to find moudle
script_folder = os.path.dirname(__file__)
import sys
sys.path.append(script_folder)
import RHINO2REVIT_UTILITY


# from Autodesk.Revit import UI # pyright: ignore
doc = REVIT_APPLICATION.get_doc()

# parent_category = doc.OwnerFamily.FamilyCategory
# print parent_category.Name


def is_family_adaptive():
    t = DB.Transaction(doc, "qwe")
    t.Start()
    try:
        doc.FamilyCreate.NewReferencePoint(DB.XYZ(0, 0, 0))
        t.RollBack()
        return True
    except:
        t.RollBack()
        return False
    # return hasattr(doc.FamilyCreate, "NewReferencePoint")
# print is_family_adaptive()


class DataGridObj(object):
    def __init__(self, file_path, OST_list, selected_name=None):
        self.file_path = file_path
        self.display_name = FOLDER.get_file_name_from_path(file_path)
        self.display_name_naked = self.display_name.split(".")[0]
        self.extension = FOLDER.get_file_extension_from_path(
            file_path).lower()
        self.OST_list = OST_list
        if selected_name:
            self.selected_OST_name = selected_name
        else:
            self.selected_OST_name = OST_list[0]


class Rhino2Revit_UI(forms.WPFWindow):
    def __init__(self):
        xaml_file_name = 'Rhino2Revit_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)


        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.button_convert.Visibility = System.Windows.Visibility.Collapsed
        self.Height = 800

        self.is_adaptive_family = is_family_adaptive()
        # self.Show()

    def is_pass_convert_precheck(self):
        # print "############################"
        for item in self.data_grid.ItemsSource:
            if "Waiting" in item.selected_OST_name:
                self.button_convert.BorderBrush = System.Windows.Media.Brushes.Black
                self.button_convert.BorderThickness = System.Windows.Thickness(
                    1)
                # NOTIFICATION.messenger(main_text = "Not all object style is assigned")
                self.button_convert.Content = "ObjectStyle Test Not Passed"
                # self.button_convert.Width = 300
                self.button_convert.IsEnabled = False
                return False

        self.button_convert.BorderBrush = System.Windows.Media.Brushes.GreenYellow
        self.button_convert.BorderThickness = System.Windows.Thickness(2)
        self.button_convert.Content = "Convert To Revit"
        self.button_convert.IsEnabled = True
        self.button_convert.Visibility = System.Windows.Visibility.Visible

        return True

    @ERROR_HANDLE.try_catch_error()
    def convert_clicked(self, sender, args):
        if not self.is_pass_convert_precheck():
            return

        t = DB.Transaction(doc, "Convert GEO to native Revit")
        t.Start()
        tool_start_time = time.time()
        detail_list = ""
        for item in self.data_grid.ItemsSource:
            start_time = time.time()
            detail_list += "\t{}\n".format(item.display_name)

            if "Use Source File Name" in item.selected_OST_name:
                try:
                    parent_category = doc.OwnerFamily.FamilyCategory
                    new_subc = doc.Settings.Categories.NewSubcategory(
                        parent_category, item.display_name_naked)
                except Exception as e:
                    # print (e)
                    pass
                finally:
                    item.selected_OST_name = item.display_name_naked

            if item.extension == ".3dm":
                self.free_form_convert(item)
            if item.extension == '.dwg':
                self.DWG_convert(item)

            time_span = time.time() - start_time
            NOTIFICATION.messenger("{} import finished!!\nImport used {}".format(item.display_name, TIME.get_readable_time(time_span)))
        t.Commit()
        tool_time_span = time.time() - tool_start_time
        REVIT_FORMS.notification(main_text="Rhino2Revit Finished.",
                                sub_text="Files processeds:\n{}\nTotal time:\n{}".format(detail_list, TIME.get_readable_time(tool_time_span)))
        self.Close()

    def free_form_convert(self, data_item):

        bad_geo_found = False

        converted_els = []
        geos = DB.ShapeImporter().Convert(doc, data_item.file_path)
        for geo in geos:
            try:
                converted_els.append(DB.FreeFormElement.Create(doc, geo))
            except Exception as e:
                print("-----Cannot import this part of file, skipping: {}".format(geo))
                print(e)
                print("-----")
                bad_geo_found = True

        assign_subC(converted_els, subC=get_subC_by_name(
            data_item.selected_OST_name))

    def DWG_convert(self, data_item):

        exisiting_cads = DB.FilteredElementCollector(
            doc).OfClass(DB.ImportInstance).ToElements()
        exisiting_import_OSTs = get_current_import_object_styles()

        options = DB.DWGImportOptions()
        cad_import_id = clr.StrongBox[DB.ElementId]()
        with ErrorSwallower() as swallower:
            doc.Import(data_item.file_path, options,
                       doc.ActiveView, cad_import_id)

        current_cad_imports = DB.FilteredElementCollector(
            doc).OfClass(DB.ImportInstance).ToElements()
        cad_import = None
        for cad_import in current_cad_imports:
            if cad_import not in exisiting_cads:
                break

        # in rare condition there is no cad import at this step, need investigation..
        if not cad_import:
            print("No CAD good import found in the family document.<{}>".format(data_item.display_name))
            return

        cad_trans = cad_import.GetTransform()
        cad_type = cad_import.Document.GetElement(cad_import.GetTypeId())
        # cad_name = revit.query.get_name(cad_type)

        family_cat = doc.OwnerFamily.FamilyCategory

        geo_elem = cad_import.get_Geometry(DB.Options())
        geo_elements = []
        for geo in geo_elem:
            if isinstance(geo, DB.GeometryInstance):
                geo_elements.extend([x for x in geo.GetSymbolGeometry()])
                """ideas
                get layer from geo.GraphicsStyleId attribute
                """

            """ideas
            if isinstance(geo, DB.TextNote):
            """

        solids = []
        model_lines = []
        for gel in geo_elements:

            if isinstance(gel, DB.Solid):
                solids.append(gel)
            elif isinstance(gel, DB.Mesh):
                print("found mesh, trying to convert: {}".format(gel))
                RHINO2REVIT_UTILITY.mesh_convert(
                    gel, cad_trans, family_cat, data_item.display_name_naked)

            elif isinstance(gel, DB.Line):
                model_lines.append(self.create_model_crv(gel))
            elif isinstance(gel, DB.Arc):
                if gel.IsBound:
                    model_lines.append(self.create_model_crv(
                        gel, additional_pt=gel.Evaluate(0.5, True)))
                else:
                    model_lines.append(self.create_model_circle(gel))
            elif isinstance(gel, DB.PolyLine):
                # print "poly line!!!!!!!!!!!!!!!!!!!"
                vertices = gel.GetCoordinates()
                for i in range(len(vertices)-1):
                    pt0 = vertices[i]
                    pt1 = vertices[i + 1]
                    try:
                        line = DB.Line.CreateBound(pt0, pt1)
                        # print line
                        model_lines.append(self.create_model_crv(line))
                    # if vertices[0].DistanceTo(vertices[-1]) < 0.00001:
                    except Exception as e:
                        print("Cannot do it here becasue {}".format(e))

            elif isinstance(gel, DB.NurbSpline):
                model_lines.append(self.create_model_spline(gel))
            else:
                print("Other geo found: {}, will ignore...".format(gel))

        # create freeform from solids
        converted_els = []
        # Convert CAD Import to FreeFrom/DirectShape"
        for solid in solids:
            converted_els.append(DB.FreeFormElement.Create(doc, solid))

        cad_import.Pinned = False
        doc.Delete(cad_import.Id)

        assign_subC_to_crvs(model_lines, subC=get_graphic_style_by_name(
            data_item.selected_OST_name))
        assign_subC(converted_els, subC=get_subC_by_name(
            data_item.selected_OST_name))

        try:
            clean_import_object_style(existing_OSTs=exisiting_import_OSTs)
        except Exception as e:
            print("fail to clean up imported category SubC becasue " + str(e))

    @ERROR_HANDLE.try_catch_error()
    def add_OST_clicked(self, sender, args):
        parent_category = doc.OwnerFamily.FamilyCategory
        new_subc_name = forms.ask_for_unique_string(reserved_values=get_all_subC_names(),
                                                    default="New SubC Name",
                                                    prompt="Name the new sub-c that will be used",
                                                    title="What is it called? Give it a unique SubC name.")

        t = DB.Transaction(doc, "Convert to User Created Sub-C")
        t.Start()
        try:
            new_subc = doc.Settings.Categories.NewSubcategory(
                parent_category, new_subc_name)
        except:
            pass
        t.Commit()

        if not self.data_grid.ItemsSource:
            return
        self.update_drop_down_selection_source()

        # print ":%%%%%%%%%"
        # print raw_subC_names
        self.data_grid.ItemsSource = [DataGridObj(
            x.file_path, self.object_style_combos.ItemsSource, selected_name=x.selected_OST_name) for x in self.data_grid.ItemsSource]

    def update_drop_down_selection_source(self):
        raw_subC_names = ["- Waiting Assignment -"] + \
            get_all_subC_names() + ["<Use Source File Name as SubC>"]
        self.object_style_combos.ItemsSource = raw_subC_names

    @ERROR_HANDLE.try_catch_error()
    def open_details_describtion(self, sender, args):
        REVIT_FORMS.notification(main_text="<.3dm Files>\nPros:\n\tStable, feel more similar to native Revit elements.\n\tIndividual control on Boolean, Subc, Visibility, Dimension Control\nCons:\n\tRequire Higer Standard of Cleaness in model.\n\tCannot handle curves.\n\n<.DWG Files>\nPros:\n\tMore tolerance on imperfection in models\n\tCan deal with lines, arcs and circle. Can also deal with Nurbs if all control points on same CPlane.\nCons:\n\tNo individual control for multiple elements, each import from same source file is glued.\n\tIntroduce Import SubC (which can be fixed automatically)",
                                                 sub_text="With the exception of curve elements, .3dm is always prefered format, if it fails to convert, try some fix source model as far as you can. You can see the help from the output window.\nUse .dwg as your last resort.",
                                                 window_title="EnneadTab",
                                                 button_name="Close",
                                                 self_destruct=0,
                                                 window_width=1200,
                                                 window_height=800)
        import trouble_shooting
        trouble_shooting.show_instruction(output)

    @ERROR_HANDLE.try_catch_error()
    def open_youtube(self, sender, args):
        script.open_url(r"https://youtu.be/gb2rG6ZteP8")

    @ERROR_HANDLE.try_catch_error()
    def pick_files(self, sender, args):
        # print "pick files"
        recent_output_folder = os.path.join(os.path.expanduser("~"), "Desktop")
            
            
        files = forms.pick_file(files_filter='Rhino and AutoCAD (*.3dm; *.dwg)|*.3dm; *.dwg|'
                                'Rhino (*.3dm)|*.3dm|'
                                'AutoCAD|*.dwg',
                                init_dir = recent_output_folder,
                                multi_file=True,
                                title="Pick your files, Rhino and/or CAD")
        # print files
        if not files:
            NOTIFICATION.messenger("There are no files selected.")
            return

        # make this to ost list
        self.update_drop_down_selection_source()
        # self.object_style_combos_template.ItemsSource = raw_subC_names
        self.data_grid.ItemsSource = [DataGridObj(
            x, self.object_style_combos.ItemsSource) for x in files]
        self.data_grid.Visibility = System.Windows.Visibility.Visible

        self.Height = 800

        self.button_test_assignment.Visibility = System.Windows.Visibility.Visible
        self.button_force_filename_OST.Visibility = System.Windows.Visibility.Visible

    def data_grid_value_changed(self, sender, args):
        self.is_pass_convert_precheck()

    @ERROR_HANDLE.try_catch_error()
    def test_assignment_clicked(self, sender, args):
        self.is_pass_convert_precheck()

    @ERROR_HANDLE.try_catch_error()
    def force_file_name_OST_clicked(self, sender, args):
        for item in self.data_grid.ItemsSource:
            if item.selected_OST_name == self.object_style_combos.ItemsSource[0]:
                item.selected_OST_name = self.object_style_combos.ItemsSource[-1]
        self.data_grid.ItemsSource = [DataGridObj(
            x.file_path, self.object_style_combos.ItemsSource, selected_name=x.selected_OST_name) for x in self.data_grid.ItemsSource]

    def handleclick(self, sender, args):
        print("surface clicked")

    def close_click(self, sender, args):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        # print "mouse down"
        sender.DragMove()

    def create_model_crv(self, geo_crv, additional_pt=None):

        try:
            pt0 = geo_crv.GetEndPoint(0)
            pt1 = geo_crv.GetEndPoint(1)
            if not additional_pt:
                pt2 = pt0 + DB.XYZ(0, 0, 1)
                pt2_alt = pt0 + DB.XYZ(1, 0, 0)
            else:
                pt2 = additional_pt

            parent_category = doc.OwnerFamily.FamilyCategory
            if parent_category.Name == "Mass" or self.is_adaptive_family:
                pt_arry = DB.ReferencePointArray()
                for pt in [pt0, pt1]:
                    pt_arry.Append(doc.FamilyCreate.NewReferencePoint(pt))

                model_crv = doc.FamilyCreate.NewCurveByPoints(pt_arry)
            else:
                try:
                    geo_plane = DB.Plane.CreateByThreePoints(pt0, pt1, pt2)
                except:
                    geo_plane = DB.Plane.CreateByThreePoints(pt0, pt1, pt2_alt)
                sketch_plane = DB.SketchPlane.Create(doc, geo_plane)
                model_crv = doc.FamilyCreate.NewModelCurve(
                    geo_crv, sketch_plane)
            # print model_crv
            return model_crv
        except Exception as e:
            print("\n\nCannot convert crv object {} becasue {}".format(
                geo_crv, traceback.format_exc()))

    def create_model_circle(self, geo_crv):
        try:
            pt0 = geo_crv.Center
            # r = geo_crv.Radius
            normal = geo_crv.Normal

            geo_plane = DB.Plane.CreateByNormalAndOrigin(normal, pt0)
            sketch_plane = DB.SketchPlane.Create(doc, geo_plane)
            model_crv = doc.FamilyCreate.NewModelCurve(geo_crv, sketch_plane)
            # print model_crv
            return model_crv
        except Exception as e:
            print("Cannot convert crv object {} becasue {}".format(
                geo_crv, traceback.format_exc()))

    def create_model_spline(self, geo_crv):
        try:
            control_pts = list(geo_crv.CtrlPoints)
            pt0 = control_pts[0]
            pt1 = control_pts[-1]
            pt2 = control_pts[1]

            geo_plane = DB.Plane.CreateByThreePoints(pt0, pt1, pt2)
            sketch_plane = DB.SketchPlane.Create(doc, geo_plane)
            model_crv = doc.FamilyCreate.NewModelCurve(geo_crv, sketch_plane)
            # print model_crv
            return model_crv
        except Exception as e:
            # print "Cannot convert crv object {} becasue {}".format(geo_crv, traceback.format_exc())
            print("###############")
            print("Cannot convert spline object {} becasue {}".format(geo_crv, e))
            print("###############")
            REVIT_FORMS.notification(main_text="There are geometry that Revit didn't accept becasue {}".format(e),
                                                     sub_text="Revit spline has to live in a plane. The plane can be angled, but a plane nonetheless.\n\nIf you need spatial free curve, consider make the curve a surface ribbon in Rhino and bring in here in Revit. You can then use the edge of this surface to do sweep and then keep the ribbon category hidden in template.", self_destruct=30)
            """
            refptarr = DB.ReferencePointArray()

            #use for loop to create a series of points
            for pt in control_pts:
                refPt = doc.FamilyCreate.NewReferencePoint(pt)
                refptarr.Append(refPt)

            model_crv = doc.FamilyCreate.NewCurveByPoints(refptarr)
            return model_crv
            """


def get_all_subC_names():
    parent_category = doc.OwnerFamily.FamilyCategory
    subCs = parent_category.SubCategories

    # <hidden line> might cause error
    subC_names = [
        x.Name for x in parent_category.SubCategories if "<" not in x.Name]
    subC_names.sort()
    return subC_names


def get_subC_by_name(name):
    parent_category = doc.OwnerFamily.FamilyCategory
    subCs = parent_category.SubCategories
    for subC in subCs:
        if subC.Name == name:
            return subC


def get_graphic_style_by_name(name):

    all_graphic_styles = DB.FilteredElementCollector(
        doc).OfClass(DB.GraphicsStyle).ToElements()
    for style in all_graphic_styles:

        if style.GraphicsStyleCategory.Name == name:
            # print style.GraphicsStyleCategory.Name
            return style
        """
        if not style.GraphicsStyleCategory.Id == doc.OwnerFamily.FamilyCategory.Id:
            continue
        if not style.GraphicsStyleType == DB.GraphicsStyleType.Projection :
            continue
        print("$$$$$$$$$$$$$$")
        print(style.GraphicsStyleType)
        for subC in style.GraphicsStyleCategory.SubCategories:
            print(subC.Name)
            if subC.Name == name:

                return subC
        """


def assign_subC(converted_els, subC):
    for element in converted_els:
        element.Subcategory = subC


def assign_subC_to_crvs(converted_els, subC):
    if not subC:
        return
    for element in converted_els:
        if not element:
            continue
        try:
            element.Subcategory = subC
        except Exception as e:
            print("\ncannot assign SubC becasue {}".format(e))
            # print subC
            print(subC.Name)


def get_current_import_object_styles():
    categories = doc.Settings.Categories
    import_OSTs = filter(lambda x: "Imports in Families" in x.Name, categories)
    if len(import_OSTs) == 0:
        return
    import_OSTs = list(import_OSTs[0].SubCategories)
    return import_OSTs


def clean_import_object_style(existing_OSTs):
    import_OSTs = get_current_import_object_styles()

    for import_OST in import_OSTs:
        if import_OST not in existing_OSTs:
            # print "--deleting imported DWG SubC: " + import_OST.Name
            doc.Delete(import_OST.Id)
    # print "\n\nCleaning finish."


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    if not doc.IsFamilyDocument:
        NOTIFICATION.messenger("Must be in a family environment, for effective subCategory")
        REVIT_FORMS.notification(main_text="Must be in a family environment for subCategory to be useful.",
                                                 sub_text="DirectShape is never a good solution, so don't do it in project environment.",
                                                 window_title="EnneadTab",
                                                 button_name="Close",
                                                 self_destruct=5,
                                                 window_width=500,
                                                 window_height=500)
        return
    Rhino2Revit_UI().show_dialog()



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
