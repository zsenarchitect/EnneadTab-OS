#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
this is getting a little out of hand

should consider refactor the script. There is big potentials"""


__doc__ = """Manager your curtain wall locations by converting walls in current plan to abstract line.
You can then modify/confirm the location of CW wall in that diagram and update the actual CW wall with this tool.

Left Click: Process current view
Right Click: Process selected views


You also have the option to include EOS lines in the diagrams, as long as the floor type name contain "struc".
You can use working-view-manager to export those Abstract wall diagram views to jpgs and can review those quicker."""
__title__ = "CurtainWall\nLocation Manager"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_FORMS, REVIT_SELECTION, REVIT_APPLICATION, REVIT_VIEW
from EnneadTab import DATA_FILE, NOTIFICATION, ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


@ERROR_HANDLE.try_catch_error()
def abstract_wall(current_only):
    solution = Solution()
    if not solution.res:
        return
    
    if current_only:
        solution.run(doc.ActiveView)
    else:
        if solution.res == solution.opts[1][0]:
            REVIT_FORMS.dialogue(main_text="If want to update wall based on diagram, this is only allowed in single view, not multiple view.",
                                                 sub_text="Use left click instead.")
            return
        views = forms.select_views(title="Select views to convert to abstract wall", 
                                    multiple=True,
                                    filterfunc=lambda v: v.ViewType in [DB.ViewType.FloorPlan, DB.ViewType.CeilingPlan])
        if not views:
            return
        for i, view in enumerate(views):
            print (i+1, " of ", len(views))
            uidoc.ActiveView = view
            solution.run(view)
        
class Solution:
    
    def __init__(self):
        self.data_file_name = "ABSTRACT_WALL_{}.json".format(doc.Title)
        self.data = DATA_FILE.read_json_as_dict_in_shared_dump_folder(self.data_file_name, create_if_not_exist=True)
        self.prefix = "EnneadTab Abstract Wall_"
        self.opts = [["Wall-->Diagram", "Generate abstract walls to review and update"],
                ["Diagram-->Wall", "Use abstract walls to update original wall locations. This will also delete other diagram lines of the same CW wall."]]
        self.res, self.is_eos_added = REVIT_FORMS.dialogue(options = self.opts, 
                                                                 main_text = "Pick your action!",
                                                                 verification_check_box_text = "Add EOS(Edge of Slab)?  [Note: the edited EOS lines cannot update floor boundary], this only help you to check where they are.")
        if not self.res:
            return
        
    def run(self, starting_view):
        # confirm current active view is a plan view or RCP, cancel and warn if not
        if starting_view.ViewType not in [DB.ViewType.FloorPlan, DB.ViewType.CeilingPlan]:
            NOTIFICATION.messenger(main_text="Current active view is not a plan view or RCP, abort.")
            return
        
        



       
        if self.res == self.opts[0][0]:
            self.wall2line()
        else:
            self.line2wall()
        
        
    def line2wall(self):
        active_view = doc.ActiveView

        

        source_view = self.prepare_view_line2wall()
        if not source_view:
            return
        
        detail_line = DB.FilteredElementCollector(doc, active_view.Id).OfCategory(DB.BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()
        self.removable_keys_in_dict = []
        self.deletable_detail_lines = []
        
        t = DB.Transaction(doc, "Abstract wall draft")
        t.Start()
        map(self.process_line2wall, detail_line)
        
        
        for detail_line in list(set(self.deletable_detail_lines)):
            try:
                doc.Delete(detail_line.Id)
            except:
                pass
        doc.Delete(active_view.Id)
        t.Commit()
        
        for key in list(set(self.removable_keys_in_dict)):
            del self.data[key]
            
        DATA_FILE.set_data_in_shared_dump_folder(self.data, self.data_file_name)
    
    
    
    
    def wall2line(self):
        
        active_view = doc.ActiveView

        
        # get all walls in current view
        all_walls = DB.FilteredElementCollector(doc, active_view.Id).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
        all_walls = [wall for wall in all_walls if hasattr(wall, "WallType") and wall.WallType.Kind == DB.WallKind.Curtain]

        all_floors = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
        # for floor in all_floors:
        #     print floor.FloorType.LookupParameter("Type Name").AsString()
        all_floors = [floor for floor in all_floors if hasattr(floor, "FloorType") and "struc" in floor.FloorType.LookupParameter("Type Name").AsString().lower()]

 
        
        if len(all_walls)==0:
            NOTIFICATION.messenger(main_text = "No curtain walls found in current view, abort.")
            return

        working_view = self.prepare_view_wall2line()
        if not working_view:
            return
        
        
        
        # for each wall, get the line/arc geometry, create new detailline in the new duplicated view
            # save the pairing data: new view uniqueId, wall uniqueId, new line uniqueId
            # set linestyle
        self.picked_linestyle =  REVIT_SELECTION.get_linestyle(doc, "EnneadTab_FOG", creation_data_if_not_exsit={"color": (0,128,255)})
        # self.picked_linestyle = REVIT_SELECTION.pick_linestyle(doc, 
        #                                                                        return_style=True,
        #                                                                        title="Pick a line style for the [AbstractWalls]")
        if not self.picked_linestyle:
            return


        t = DB.Transaction(doc, "Abstract wall draft")
        t.Start()
        map(self.process_wall2line, all_walls)
        if self.is_eos_added:
            self.floor2line(all_floors)
        t.Commit()
            
        
        #  store the data in L drive? in project custoe schema?
        DATA_FILE.set_data_in_shared_dump_folder(self.data, self.data_file_name)
        
        
        NOTIFICATION.messenger(main_text = "You can start checking/updating the abstract walls in\n[{}].".format(working_view.Name))
        
        
        pass


    def floor2line(self, all_floors):
        
        
  
        
        if len(all_floors)==0:
            NOTIFICATION.messenger(main_text = "No floor with type name containning 'struc' found in current view, skip EOS creation.")
            return
        self.picked_eos_linestyle =  REVIT_SELECTION.get_linestyle(doc, "EnneadTab_EOS", creation_data_if_not_exsit={"color": (255,0,0)})
        # self.picked_eos_linestyle = REVIT_SELECTION.pick_linestyle(doc, 
        #                                                                        return_style=True,
        #                                                                        title="Pick a line style for the [EdgeOfSlab]")
        if not self.picked_eos_linestyle:
            return

        map(self.process_floor2line, all_floors)

    def process_line2wall(self, detail_line):
        original_id = self.data.get(detail_line.UniqueId, None)
        if not original_id:
            return
        
        self.removable_keys_in_dict.append(detail_line.UniqueId)
        
        
        original_element = doc.GetElement(original_id)
        if hasattr(original_element, "WallType"):
            original_element.Location.Curve = detail_line.Location.Curve
        elif hasattr(original_element, "FloorType"):
            pass
            # original_element = detail_line.Location.Curve



        # should also remove any detailine related to this floor or wall but not in current view
        for detail_line_unique_id in self.data:
            if self.data[detail_line_unique_id] != original_id:
                # this key is not pointing to the same floor
                continue

            # should remove the key from dict regardless the detail line still exist or not
            self.removable_keys_in_dict.append(detail_line_unique_id)

            
            retreived_detail_line = doc.GetElement(detail_line_unique_id)
            if retreived_detail_line is None:
                continue
            if retreived_detail_line.OwnerViewId.IntegerValue  == doc.ActiveView.Id.IntegerValue :
                continue
                
            self.deletable_detail_lines.append(doc.GetElement(detail_line_unique_id))
        
        return

        intersection_pt = original_wall.Location.Curve.Project(detail_line.Location.Curve.GetEndPoint(0)).XYZPoint
        move_vector =  detail_line.Location.Curve.GetEndPoint(0) - intersection_pt
        
        original_wall.Location.Move(move_vector)
        

    def update_detail_lines_of_same_original_element(self, element_unique_id):
        # to-do: make this a statdard processure for both geo2line and line2geo
        pass
    
    def update_detail_lines_of_same_detail_line(self, detail_line_id):
        # to-do: make this a statdard processure for both geo2line and line2geo
        pass
    
    def process_wall2line(self, wall):
        curve =  wall.Location.Curve
        
        # get all the detail line related to this wall based on data, if the detailine still exist, update detail line, otherwise create
        # this is not efficient becasue same detail line will be updated multiple time when running by different view. Should do this at begingin and prepare things_updated list
        found_in_views = []
        for detail_line_unique_id in self.data:
            original_wall_id = self.data[detail_line_unique_id]
            if wall.UniqueId != original_wall_id:
                # this key is not pointing to the same wall
                continue
            retreived_detail_line = doc.GetElement(detail_line_unique_id)
            if retreived_detail_line:
                found_in_views.append(doc.GetElement(retreived_detail_line.OwnerViewId))
                retreived_detail_line.Location.Curve = curve
                


        if doc.ActiveView not in found_in_views:

            detail_line = doc.Create.NewDetailCurve (doc.ActiveView, curve)
            detail_line.LineStyle = self.picked_linestyle
            # key = detail line, value = source wall
            self.data[detail_line.UniqueId] = wall.UniqueId

    def process_floor2line(self, floor):
        self.process_floor2line_action_classic(floor)
        return
        if not hasattr(floor, "SketchId"):
            self.process_floor2line_action_classic(floor)
        else:
            pass
            floor_sketch = doc.GetElement(floor.SketchId)
            sketch_profile = floor_sketch.Profile
            for crv_array in sketch_profile:
                for crv in crv_array:
                    try:
                        detail_line = doc.Create.NewDetailCurve (doc.ActiveView, crv)
                    except:
                        # might failed if the floor have been edit in shape to become un-flat
                        continue
                    detail_line.LineStyle = self.picked_eos_linestyle
                    # key = detail line, value = source floor
                    self.data[detail_line.UniqueId] = floor.UniqueId
        



    def process_floor2line_action_classic(self, floor):
        opt = DB.Options()
        opt.IncludeNonVisibleObjects = True
        opt.ComputeReferences = True
        floor_geo = floor.get_Geometry(opt)
        geo_objs = floor_geo.GetEnumerator()
        for geo_obj in geo_objs:
            if "Solid" in str(geo_obj.GetType()):
                break

        def get_top_face(solid):
            faces = solid.Faces
            for face in faces.GetEnumerator():
                face_normal = face.ComputeNormal(DB.UV())
                if face_normal.DotProduct(DB.XYZ(0,0,1)) - 1 < 0.001:
                    return face
        top_face = get_top_face(geo_obj)
        
        curveloops =  top_face.GetEdgesAsCurveLoops ()
        for curveloop in curveloops:
            # A curve loop iterator object that can be used to iterate through key-value pairs in the collection.
            crv_iterator = curveloop.GetCurveLoopIterator ()

            while crv_iterator.MoveNext ():
            
                sketch_curve = crv_iterator.Current
                # print (sketch_curve)
                try:
                    detail_line = doc.Create.NewDetailCurve (doc.ActiveView, sketch_curve)
                except:
                    # might failed if the floor have been edit in shape to become un-flat
                    continue
                detail_line.LineStyle = self.picked_eos_linestyle
                # key = detail line, value = source floor
                self.data[detail_line.UniqueId] = floor.UniqueId

                # to-do: use temp tranation to find the 
                # self.data[detail_line.UniqueId] = sketch_curve.UniqueId

    
    def prepare_view_line2wall(self):
        
        if self.prefix not in doc.ActiveView.Name:
            NOTIFICATION.messenger(main_text="Current active view is not a abstract wall view, cannot find its source view..")
            return None
        desired_source_view_name = doc.ActiveView.Name.replace(self.prefix, "")
        source_view = REVIT_VIEW.get_view_by_name(desired_source_view_name)
        if not source_view:
            NOTIFICATION.messenger(main_text="The source view of this diagram view cannot be found...")
            return None
        
        uidoc.ActiveView = source_view
        return source_view

    def prepare_view_wall2line(self):
        # duplicate current view, keep only those categorys visible:
        # -lines
        # -dimension
        # -grid
        
        
        if self.prefix in doc.ActiveView.Name:
            NOTIFICATION.messenger(main_text="Current active view is already a diagram view, abort.")
            
            return None
        
        
        
        t = DB.Transaction(doc, "Prepare new view")
        t.Start()
        desired_view_name = self.prefix + doc.ActiveView.Name
        working_view = REVIT_VIEW.get_view_by_name(desired_view_name)
        
        
        if not working_view:
            working_view_id = doc.ActiveView.Duplicate(DB.ViewDuplicateOption.Duplicate)
            working_view = doc.GetElement(working_view_id)
            working_view.Name = desired_view_name
            working_view.ViewTemplateId = DB.ElementId.InvalidElementId
            
            
            para = working_view.LookupParameter("Views_$Group")
            if para:
                para.Set("Abstract Wall Locations")
            para = working_view.LookupParameter("Views_$Series")
            if para:
                current_value = doc.ActiveView.LookupParameter("Views_$Series").AsString()
                # adding str() here to force type as string, not elementID, which might be the case when geting empty
                para.Set(str(current_value))
            
            
            kept_cate_names = ["Dimensions", "Grids", "Lines", "Detail Items"]
            for cate in doc.Settings.Categories:
                if not working_view.CanCategoryBeHidden (cate.Id):
                    continue
                if cate.Name in kept_cate_names:
                    working_view.SetCategoryHidden(cate.Id, False)
                else:
                    working_view.SetCategoryHidden(cate.Id, True)
                    
                if cate.Name == "Lines":
                    for subC in cate.SubCategories:
                        if not working_view.CanCategoryBeHidden (subC.Id):
                            continue
                        if subC.Name.startswith("<"):
                            working_view.SetCategoryHidden(subC.Id, True)
            
        
        t.Commit()
        uidoc.ActiveView = working_view
        
        return working_view
################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    if __shiftclick__:
        abstract_wall(current_only=False)
    else:
        abstract_wall(current_only=True)
    


