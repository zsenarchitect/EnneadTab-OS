
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
if ENVIRONMENT.is_Grasshopper_environment():
    import Rhino # pyright: ignore
    import Grasshopper # pyright: ignore
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

def set_doc_to_rhinodoc():
    sc.doc = Rhino.RhinoDoc.ActiveDoc

def set_doc_to_ghdoc():
    sc.doc = Grasshopper.Instances.ActiveCanvas.Document


class AccessRhinoDoc():
    """Simplifies switching backa dn forth between Rhino and Grasshopper documents. 
    by setting to RhinoDoc.ActiveDoc and ghdoc before and after the context.
    Automatically rolls back if exception is raised.

    >>> with AccessRhinoDoc():
    >>>     wall.DoSomething()

    """
    def __init__(self):
        pass

    def __enter__(self):
        set_doc_to_rhinodoc()
        return self

    def __exit__(self, exception, exception_value, traceback):
        set_doc_to_ghdoc()


"""
it turns out you can load grasshopper compnent to rhino doc method.

https://developer.rhino3d.com/guides/rhinopython/ghpython-call-components/#node-in-code-from-rhinopython

import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import scriptcontext
 
points = rs.GetPoints(True, True)
if points:
    curves = ghcomp.Voronoi(points)   <----------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for curve in curves:
        scriptcontext.doc.Objects.AddCurve(curve)
    for point in points:
        scriptcontext.doc.Objects.AddPoint(point)
    scriptcontext.doc.Views.Redraw()

"""