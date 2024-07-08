
__title__ = "SectionCrowd"
__doc__ = "Populate people interactively in TOP view by providing two points."

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System # pyright: ignore
import sys
import random
import os
import traceback
from EnneadTab import DATA_FILE
from EnneadTab import NOTIFICATION, LOG, ERROR_HANDLE

BASIC_BLOCK_NAMES = []
for block_file in os.listdir(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\bin\Dummy Blocks\EA_People_Elevation_Dummy"):
    if block_file.endswith(".3dm"):
        dummy_block_name = block_file.split(".")[0]
        BASIC_BLOCK_NAMES.append(dummy_block_name)
        
        
class GetPointUI(Rhino.Input.Custom.GetPoint):
    def __init__(self, other_point, spacing):
        self.other_point = other_point
        self.spacing = spacing
        if not other_point:
            self.title = "EnneadTab Sectional Crowd: First Point"
        else:
            self.title = "EnneadTab Sectional Crowd: Second Point"
        self.dummy_block_name = BASIC_BLOCK_NAMES[0]
    
    
    def show_text_with_pointer(self, e, text, size):
        is_middle_justified = False
        color = rs.CreateColor([87, 85, 83])
        
        
        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)
        #self.pointer_2d = Rhino.Geometry.Point2d(self.pointer_2d[0], self.pointer_2d[0] + size - 5)
        self.pointer_2d += Rhino.Geometry.Vector2d(0, size )
        
        
        
    def OnDynamicDraw(self, e):

        position_X_offset = 20
        position_Y_offset = 40
        bounds = e.Viewport.Bounds
        self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)


        mouse_pt = e.CurrentPoint

        if self.other_point:
            try:
                line = Rhino.Geometry.Line(self.other_point, mouse_pt)
                e.Display.DrawLine   (line, System.Drawing.Color.White, 3)
                


                self.transform_list = self.get_transforms_on_crv(line, spacing = self.spacing)
                
         
                block_definition = sc.doc.InstanceDefinitions.Find(BASIC_BLOCK_NAMES[0])
                map(lambda transform: e.Display.DrawInstanceDefinition(block_definition, transform), self.transform_list)
            except:
                print (traceback.format_exc())
                self.transform_list = []

        else:
            self.transform_list = []


        
        self.show_text_with_pointer(e,
                                    text = self.title,
                                    size = 30)

        if self.other_point:
            e.Display.DrawDot  (self.other_point, "Start Pt")
            e.Display.DrawDot  (mouse_pt, "End Pt")
        else:
            e.Display.DrawDot  (mouse_pt, "Start Pt")



    def get_transforms_on_crv(self, base_crv, spacing):
        
        insert_pt, ref_pt = [0,0,0], [500 , 0, 0]
        temp_block = rs.InsertBlock(self.dummy_block_name, insert_pt)
        directional_ref = [0,1,0]
        block_reference = [insert_pt, ref_pt, directional_ref]



        collection = []
        #print crv_segs
        base_crv = base_crv.ToNurbsCurve ()
        count_target = base_crv.GetLength() / spacing
        domain = base_crv.Domain
        count = 0
        while count < count_target:
            t = domain[0] + (domain[1] - domain[0]) * random.random()
            tangent = base_crv.TangentAt(t)
            side_vector = rs.VectorRotate(tangent, 90, [0,0,1])
            
            point = base_crv.PointAt(t)
            directional_ref_temp = point + side_vector
            target_reference = [point, point + tangent, directional_ref_temp]
            
            
            temp_placed_block = rs.OrientObject( temp_block, block_reference, target_reference, flags = 1 )
            collection.append(rs.BlockInstanceXform(temp_placed_block))
            rs.DeleteObject(temp_placed_block)
            count += 1
    


        rs.DeleteObject(temp_block)
        return collection


def get_pt(other_pt, spacing):
   
    
    ui = GetPointUI(other_pt, spacing)
    if other_pt:
        ui.SetCommandPrompt("Getting Ending Pt")
        ui.SetBasePoint(other_pt, True)
        ui.DrawLineFromPoint(other_pt, True)
    else:
        ui.SetCommandPrompt("Geting Starting Pt")
    ui.ConstrainToConstructionPlane(False)
    ui.Get()
    if ui.CommandResult() != Rhino.Commands.Result.Success:
        return None, None, None
    return ui.Point(), ui.transform_list, ui.dummy_block_name


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def section_crowd():


    people_density = DATA_FILE.get_sticky_longterm("DUMMY_PEOPLE_DENSITY", 800)
    res = rs.PropertyListBox(items = ["Social Distance(file unit)"],
                            values = [ people_density],
                            message = "Enter section draft crowd setting",
                            title = "Section People CrowdMaker")
    if not res:
        return
    people_density = res[0]
    people_density = float(people_density)
    DATA_FILE.set_sticky_longterm("DUMMY_PEOPLE_DENSITY", people_density)
    
    for dummy_block_name in BASIC_BLOCK_NAMES:
        
        insert_ref_block(dummy_block_name)

    start_pt, _, _ = get_pt(None,None)
    if not start_pt:
        NOTIFICATION.messenger(main_text = "Did not pick starting point. Cancelled")
        return
    end_pt, transform_list, dummy_block_name = get_pt(start_pt, people_density)
    
    print (start_pt)
    print (end_pt)
    rs.EnableRedraw(False)
    collection = []
    for transform in transform_list:
        block_name = random.choice(BASIC_BLOCK_NAMES)
        block = rs.InsertBlock2(block_name, transform)
        rs.MoveObject(block, [0,0,random.random()])
        
        collection.append(block)
        
    rs.AddObjectsToGroup(collection, rs.AddGroup())


def insert_ref_block( dummy_block_name):
    if rs.IsBlock(dummy_block_name):
        # EnneadTab.NOTIFICATION.messenger(main_text = "Block Already Exists")
        
        return
    
    NOTIFICATION.messenger(main_text = "Block Importing")
    external_block_filepath = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\bin\Dummy Blocks\EA_People_Elevation_Dummy\{}.3dm".format(dummy_block_name)

    dummyInitialObjects = [Rhino.Geometry.Point(Rhino.Geometry.Plane.WorldXY.Origin)]
    dummyInitialAttributes = [Rhino.DocObjects.ObjectAttributes()]
    indexOfAddedBlock = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Add(dummy_block_name,
                                                                        "",
                                                                        Rhino.Geometry.Plane.WorldXY.Origin,
                                                                        dummyInitialObjects ,
                                                                        dummyInitialAttributes)


    # if is_ref_block_method:
    #     block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Linked

    # else:
    block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.LinkedAndEmbedded


    modified = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.ModifySourceArchive(indexOfAddedBlock,
                                                                                Rhino.FileIO.FileReference.CreateFromFullPath(external_block_filepath),
                                                                                block_method,
                                                                                True)# bool for quite mode, no error msg shown
    obj = Rhino.RhinoDoc.ActiveDoc.Objects.AddInstanceObject(indexOfAddedBlock,Rhino.Geometry.Transform.Identity)

    return





if __name__ == "__main__":
    section_crowd()