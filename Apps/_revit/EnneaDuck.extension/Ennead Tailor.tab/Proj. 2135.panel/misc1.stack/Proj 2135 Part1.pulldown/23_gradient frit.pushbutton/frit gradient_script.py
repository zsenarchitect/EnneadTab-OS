__doc__ = "Apply grediant frit pattern to the ADP family instance."
__title__ = "23_frit gradient"

from pyrevit import script, revit #
from Autodesk.Revit import DB # pyright: ignore 
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
"""
from Autodesk.Revit import UI # pyright: ignore
uiapp = UI.UIApplicationapp
uidoc = UI.UIDocument
#optional
host_app = pyrevit._HostApplication
app = host_app.app
uiapp = host_app.uiapp
uidoc = host_app.uidoc



uidoc = __revit__.ActiveUIDocument
"""
"""
from pyrevit import HOST_APP
doc = HOST_APP.doc
uidoc = HOST_APP.uidoc
"""

def process_frit(dot):

    intersection_result = crv.Project(dot.Location.Point)
    #print "***"
    dist = EA_UTILITY.internal_to_mm(intersection_result.Distance)
    if dist > threshold:
        scale = 1.0
    else:
        #print "&&&&&&&&&&&&&&"
        t = threshold
        a = (1 - min_scale)/(t**2)
        b = min_scale
        x = dist
        scale = max(min_scale, a * (x**2) + b)
        #print scale

    ###consider standardise the scale to 0.2,0.4,0.6,0.8,0.9,1.0
    ##use number rounding

    new_edge = EA_UTILITY.mm_to_internal(max_edge * scale)
    #print max_edge * scale

    dot.LookupParameter("edge").Set(new_edge)
    dot.LookupParameter("Comments").Set("edge = " + str(max_edge * scale))
    dot.LookupParameter("Mark").Set("dist = " + str(dist))



################## main code below #####################
output = script.get_output()
output.close_others()
threshold = 2000 # cut off distance in mm
min_scale = 0.2 #  dont make frit smaller than this scale
max_edge = 50 # the default edge size if the frit scale is 1

guides = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ReferenceLines).WhereElementIsNotElementType().ToElements()

guide = filter(lambda x: x.Subcategory.Name == "frit guide line", guides)[0]
#print guide
#print guide.Subcategory.Name

crv = guide.GeometryCurve


generic_models = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
frits = filter(lambda x: x.Symbol.Family.Name == "frit item", generic_models)
#print frits
#script.exit()

with revit.Transaction("gradient"):
    output.freeze()
    map(process_frit, frits)
    output.unfreeze()
