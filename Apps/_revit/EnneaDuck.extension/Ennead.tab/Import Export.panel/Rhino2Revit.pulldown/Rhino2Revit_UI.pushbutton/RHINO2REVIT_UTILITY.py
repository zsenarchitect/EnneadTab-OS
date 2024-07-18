
from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import script
from pyrevit.framework import List

def find_c(category_name):
    for category in revit.doc.Settings.Categories:
        if category.Name == category_name:
            return category

def find_subc(name):
    global subCs
    for item in subCs:
        if item.Name == name:
            return item

def user_select(select_list, rhino_name = None):
    #let user select
    select_list.append("<Create New SubCategory by typing in name (double click me)>")
    simplified_name = rhino_name.split('\\')[-1].split(".")[0]
    #simplified_name = " "
    select_list.append("<Use Rhino file name as new subC name:  {}>".format(simplified_name))
    select_list.insert(0, "<Use Parent Category>")
    selected = forms.SelectFromList.show(select_list, title = "Select a subcategory from currently available list.", button_name='Select SubC',multiselect  = False)

    if not selected:
        script.exit()
    return selected


def mesh_convert(geo,cad_trans,family_cat,cad_name):#geo element

    builder = DB.TessellatedShapeBuilder()
    builder.OpenConnectedFaceSet(False)

    triangles = [geo.Triangle[x] for x in range(0, geo.NumTriangles)]
    for t in triangles:
        p1 = cad_trans.OfPoint(t.Vertex[0])
        p2 = cad_trans.OfPoint(t.Vertex[1])
        p3 = cad_trans.OfPoint(t.Vertex[2])
        tface = DB.TessellatedFace(List[DB.XYZ]([p1, p2, p3]),
                                   DB.ElementId.InvalidElementId)
        builder.AddFace(tface)

    builder.CloseConnectedFaceSet()
    builder.Target = DB.TessellatedShapeBuilderTarget.AnyGeometry
    builder.Fallback = DB.TessellatedShapeBuilderFallback.Mesh
    builder.Build()

    with revit.Transaction("Convert CAD Import to DirectShape"):
        ds = DB.DirectShape.CreateElement(
            revit.doc,
            family_cat.Id
            # DB.ElementId(DB.BuiltInCategory.OST_DataDevices)
            )
        ds.ApplicationId = 'B39107C3-A1D7-47F4-A5A1-532DDF6EDB5D'
        ds.ApplicationDataId = ''
        ds.SetShape(builder.GetBuildResult().GetGeometricalObjects())
        ds.Name = cad_name

def assign_subC(converted_els, source_file):
    parent_category = revit.doc.OwnerFamily.FamilyCategory
    global subCs
    subCs = parent_category.SubCategories

    subC_names = []
    for item in subCs:
        subC_names.append(item.Name)
    subC_names.sort()

    selected_name = user_select(subC_names, source_file)
    if "Create New" in selected_name:
        #print "will create new"
        new_subc_name = forms.ask_for_string( default = "New SubC Name", prompt = "Name the new sub-c that will be used", title = "What is it called?")

        with revit.Transaction("Convert to User Created Sub-C"):
            try:
                new_subc = revit.doc.Settings.Categories.NewSubcategory(parent_category, new_subc_name)
            except:
                #maybe there is already this names
                new_subc = find_subc(new_subc_name)

            for element in converted_els:
                element.Subcategory = new_subc

    elif "Use Rhino" in selected_name:
        #print "will take rhino name and create new"

        new_subc_name = source_file.split('\\')[-1].split(".")[0]

        with revit.Transaction("Convert to newly created Sub-C using rhino name"):
            try:
                new_subc = revit.doc.Settings.Categories.NewSubcategory(parent_category, new_subc_name)
            except:
                #maybe there is already this names
                new_subc = find_subc(new_subc_name)

            for element in converted_els:
                element.Subcategory = new_subc


    elif "Use Parent" in selected_name:
        #print "will use parent name and do nothing"
        pass

    else:
        #print "will use selected sub c"
        with revit.Transaction("Convert to Sub-C selected"):
            for element in converted_els:
                element.Subcategory = find_subc(selected_name)



if __name__ == "__main__":
    pass