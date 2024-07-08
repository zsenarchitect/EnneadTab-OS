
__title__ = "MatchTextureMappingInBlock"
__doc__ = "Pick a source block, then apply the texture mapping of this block to other blocks selected."

import rhinoscriptsyntax as rs
import scriptcontext as sc

from EnneadTab import LOG, ERROR_HANDLE

class Solution:
    def __init__(self):
        pass
    
    def process_block(self, block_name):
        objects = rs.BlockObjects(block_name)
        for obj in objects:
            layer = rs.ObjectLayer(obj)
            for source_obj in self.source_objects:
                if rs.ObjectLayer(source_obj) == layer:
                    
                    break
                
            # transform = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
            # print sc.doc.Objects.FindId (source_obj)
            mapping = sc.doc.Objects.FindId (source_obj).GetTextureMapping(1)
            if mapping is None:
                continue
            # print mapping
            sc.doc.Objects.FindId (obj).SetTextureMapping(1, mapping)
            
    def match_block_map(self):
        
        source_block = rs.GetObject("Select source block", rs.filter.instance)
        if not source_block:
            return
        target_blocks = rs.GetObjects("Select target blocks", rs.filter.instance)
        if not target_blocks:
            return
        
        
        rs.EnableRedraw(False)
        
        self.source_objects = rs.BlockObjects(rs.BlockInstanceName(source_block))
        
        unique_target_blocks = list(set([rs.BlockInstanceName(b) for b in target_blocks]))
        map(self.process_block, unique_target_blocks)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def match_texture_mapping_in_block():
    Solution().match_block_map()

if __name__ == "__main__":
    match_texture_mapping_in_block()