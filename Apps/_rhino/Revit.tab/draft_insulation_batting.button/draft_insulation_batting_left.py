
__title__ = "DraftInsulationBatting"
__doc__ = "Given base crvs and thickness, it makes a 2D insulation batting graphic that can be any shape. "
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab import DATA_FILE, ENVIRONMENT



class InsulationDrafter:
    def main(self):
        ref_crvs = rs.GetObjects("Select reference crvs", rs.filter.curve)
        if not ref_crvs:
            return
        
        insulation_width = DATA_FILE.get_sticky("insulation_width", 2)
        insulation_width = rs.PropertyListBox(items = ["Insulation Width(file unit)"], values = [insulation_width], message = "Enter insulation data", title = "Curved Insulation Maker")[0]
        if not insulation_width: return
        insulation_width = float(insulation_width)
        DATA_FILE.set_sticky("insulation_width", insulation_width)
        print (insulation_width)

        
        rs.EnableRedraw(False)
        sample_file = "{}\\Insulation Batting Sample.3dm".format(os.path.dirname(__file__))
        rs.Command("_-import \"{}\" -enter -enter".format(sample_file))
        sample_bat = rs.LastCreatedObjects()[0]

  
        current_half_width = rs.BoundingBox(sample_bat)[2][1]
        print (current_half_width)
        scale_factor = insulation_width / (2*current_half_width)
        print (scale_factor)
        sample_bat = rs.ScaleObject(sample_bat, [0,0,0], [scale_factor, scale_factor, scale_factor])
        
        self.sample_data = {}
        self.sample_data["bat_crv"] = sample_bat
        self.sample_data["bat_half_width"] = rs.BoundingBox(sample_bat)[2][1]
        self.sample_data["bat_length"] = rs.BoundingBox(sample_bat)[2][0]

        map(self.process_crv, ref_crvs)
        rs.DeleteObject(self.sample_data["bat_crv"])

    def process_crv(self,crv):
        length = rs.CurveLength(crv)
        
        
        
        collection = [rs.CopyObject(self.sample_data["bat_crv"])]
        right_end = self.sample_data["bat_length"]
        

        while right_end + self.sample_data["bat_length"] < length:
            
            flipped_copy = rs.MirrorObject(collection[-1], [right_end,0,0], [right_end,1,0], True)
            collection.append(flipped_copy)
            right_end += self.sample_data["bat_length"]
            
        
        guide_crv = rs.AddLine([0,0,0], [right_end,0,0])
        
        
        morph = Rhino.Geometry.Morphs.FlowSpaceMorph(sc.doc.Objects.Find(guide_crv).Geometry,
                                                     sc.doc.Objects.Find(crv).Geometry,
                                                     False)
        
        abstract_crvs = [sc.doc.Objects.Find(x).Geometry for x in collection]
        map(morph.Morph,abstract_crvs)
        res = [sc.doc.Objects.AddCurve(x) for x in abstract_crvs]
        rs.AddObjectsToGroup(res, rs.AddGroup())
        rs.DeleteObjects(collection + [guide_crv])

 



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def draft_insulation_batting():
    InsulationDrafter().main()




if __name__ == "__main__":
    draft_insulation_batting()