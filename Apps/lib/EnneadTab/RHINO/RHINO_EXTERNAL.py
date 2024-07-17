

import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

    
class ExternalRhino:
    def __init__(self, filepath):
        if not os.path.exists(filepath):
            print ("File path not valid")
            return
        self.doc = Rhino.RhinoDoc.OpenHeadless(filepath)


    def get_external_geos_by_layer(self, layer):
        if not self.doc:
            raise "Doc is lost."
        layer_index = self.doc.Layers.FindByFullPath(layer, Rhino.RhinoMath.UnsetIntIndex)
        if layer_index == Rhino.RhinoMath.UnsetIntIndex:
            raise "Cannot find layer <{}>".format(layer)
            
        layer = self.doc.Layers[layer_index]
        return [x.Geometry for x in self.doc.Objects.FindByLayer(layer)]

