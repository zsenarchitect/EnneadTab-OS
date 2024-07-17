#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Now that you have finished drafting in Rhino, you can bring them in \
to Revit as detail lines.\n\nIf there are line style note found, you will be asked\
 to find a match.\n\nThis prototype works best in metric mm."
__title__ = "Transfer From Rhino Drafting"
__youtube__ = "https://youtu.be/UGRFjFWCVqU"
from pyrevit import forms #
from pyrevit import script #
from pyrevit.revit import ErrorSwallower
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore

import re

def get_doc_create(doc):
    if doc.IsFamilyDocument:
        #EA_UTILITY.print_note("it is family doc")
        doc_create = doc.FamilyCreate
    else:
        #EA_UTILITY.print_note("it is project doc")
        doc_create = doc.Create

    return doc_create



def convert_raw_data(data):
    #"['working line style', 'line', ((-211650.0, 17420.0, 0.0), (-211650.0, 16040.0, 0.0))]"
    #"['FilledRegion::AAA', 'srf', [['line', ((-0.1, 0.1, 0.0), (-0.1, 0.1, 0.0))], ['line', ((-0.1, 0.1, 0.0), (-0.1, -0.1, 0.0))], ['line', ((-0.1, -0.1, 0.0), (-0.1, -0.1, 0.0))], ['line', ((-0.1, -0.1, 0.0), (-0.1, 0.1, 0.0))]]]""
    #print data
    if "srf" not in data:
        pattern = r"\['(.+)', '(.+)', (.+)\]"
        searched_txt = re.search(pattern, data)
        layer, type, geo_data = searched_txt.group(1), searched_txt.group(2), searched_txt.group(3)
        return (layer, type, geo_data)

    pattern = r"\['(.+)', 'srf', (.+)\]"
    searched_txt = re.search(pattern, data)
    layer, type, geo_data = searched_txt.group(1), "srf", searched_txt.group(2)
    return (layer, type, geo_data)



def process_data(doc, data, DICT_ost_mapping):
    #print "\n\n----new data"

    layer, type, geo_data = data
    # print layer
    # print type
    # print geo_data

    OST_style = DICT_ost_mapping[layer]

    # deal with srf first
    if type == "srf":
        filled_region = create_filled_region(doc, geo_data, OST_style)
        #print filled_region
        return filled_region



    #deal with lines
    detail_crv = None
    if type == "line":
        detail_crv = create_detail_line(doc, geo_data)


    if type == "arc":
        detail_crv = create_detail_arc(doc, geo_data)

    if detail_crv is not None:
        doc_create = get_doc_create(doc)
        detail_crv = doc_create.NewDetailCurve(doc.ActiveView, detail_crv)
        try:
            detail_crv.LineStyle = OST_style
        except Exception as e:
            print (e)
            print (layer, type, geo_data)
            print (DICT_ost_mapping.items())

    return detail_crv


def create_filled_region(doc, geo_data, filled_region_type):
    geo_data = eval(geo_data)
    #print geo_data
    crv_datas = geo_data
    crv_loop = DB.CurveLoop()
    crv_loop = []
    for crv_data in crv_datas:
        #print "$$$$$$$$$$$"
        #print crv_data
        type, geo_data = crv_data
        #print type
        goe_data = str(geo_data)
        #print geo_data
        local_crv = None
        if type == "line":
            local_crv = create_detail_line(doc, geo_data)

        if type == "arc":
            local_crv = create_detail_arc(doc, geo_data)
        #crv_loop.Append(local_crv)
        crv_loop.append(local_crv)
    crv_loop = [DB.CurveLoop.Create(list(crv_loop))]
    crv_loop = EA_UTILITY.list_to_system_list(crv_loop, type = "CurveLoop", use_IList = False)
    filled_region = DB.FilledRegion.Create(doc,
                                            filled_region_type.Id,
                                            doc.ActiveView.Id,
                                            crv_loop)
    return filled_region

def convert_unit(x):
    global rhino_unit

    if rhino_unit == 0:
        return EA_UTILITY.mm_to_internal(float(x))

    if rhino_unit == 1:
        return float(x)     

def create_detail_line(doc, geo_data):

    pattern = r"\(\((.+), (.+), (.+)\), \((.+), (.+), (.+)\)\)"
    searched_txt = re.search(pattern, str(geo_data))
    x0, y0, z0 = searched_txt.group(1), searched_txt.group(2), searched_txt.group(3)
    x1, y1, z1 = searched_txt.group(4), searched_txt.group(5), searched_txt.group(6)

    #print x0, y0, z0, x1, y1, z1
    x0, y0, z0, x1, y1, z1 = [convert_unit(x) for x in [x0, y0, z0, x1, y1, z1]]
    #print x0, y0, z0, x1, y1, z1


    if doc.ActiveView.ViewDirection.CrossProduct(DB.XYZ(0,0,1)) == 0:
        #assume current view is a section/elevation view
        #x value from data is the distance it travel from origion in view right direction
        # y value from data is the Z in real space
        #z value is alwasy 0
        pt0 = doc.ActiveView.RightDirection * x0 + DB.XYZ(0,0,y0)
        pt1 = doc.ActiveView.RightDirection * x1 + DB.XYZ(0,0,y1)
        #print pt0, pt1
        line = DB.Line.CreateBound(pt0, pt1)
        #print line
        return line
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


def create_detail_arc(doc, geo_data):

    pattern = r"\(\((.+), (.+), (.+)\), \((.+), (.+), (.+)\), \((.+), (.+), (.+)\)\)"
    searched_txt = re.search(pattern, str(geo_data))
    x0, y0, z0 = searched_txt.group(1), searched_txt.group(2), searched_txt.group(3)
    x1, y1, z1 = searched_txt.group(4), searched_txt.group(5), searched_txt.group(6)
    x2, y2, z2 = searched_txt.group(7), searched_txt.group(8), searched_txt.group(9)

    #print x0, y0, z0, x1, y1, z1

    x0, y0, z0, x1, y1, z1, x2, y2, z2 = [convert_unit(x) for x in [x0, y0, z0, x1, y1, z1, x2, y2, z2]]




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


def transfer_rhino_drafting(doc):
    """
    IMPORTANT!
    !!!!cross platform drafter

    export revit view as two dwgs(model dwg, 2D element dwg). In rhino load two. Start drafting in OUT layer. Allow only lines and arc. and hatches and block made of current detail item on page. Sublayer of OUT is all the availbley line type. A live conduit show cuurent count by OST and non-revit element count

    Export OUT content and regenerate in revit element by element, group final with time stamp.
    has a mapping form that takes USER new layer to revit line style

    ideas: check force import dwg but with lines this time. polyline-->polyline, lines(touching)--->polyline, llines(solo)---Line, hatch ---> straight invisible, surface----> shape


    Ideas:
    Revit reading dwg is hard.
    Maybe it is better to explode polylines in rhino and record line data(pt0,pt1, layer), or arc data. Then directly create revit detail line in view and group.
    Similarly can use surface in rhino to extract boundary line, and fill region type.

    The tricky part is to be able to return rhino edit again from revit to update.  But practically it might not be important.
    """
    global rhino_unit
    rhino_unit = EnneadTab.REVIT.REVIT_UNIT.pick_incoming_file_unit(main_text = "What is the file unit of the drafting Rhino file?")

    # get dump data
    file_path = EA_UTILITY.get_filepath_in_special_folder_in_EA_setting("Local Copy Dump", "EA_DRAFTING_TRANSFER.txt")
    raw_datas = EA_UTILITY.read_txt_as_list(file_path)


    datas = [convert_raw_data(x) for x in raw_datas]
    unique_layers = list(set([x[0] for x in datas]))
    DICT_ost_mapping = dict()

    def map_line_OST(layer):
        OST_style = EA_UTILITY.get_linestyle(doc, layer)
        if OST_style is None:
            EA_UTILITY.dialogue(main_text = "Rhino Layer [{}] does not have a matching linestyle in revit, please rename in Rhino and reexport, or pick a linestyle now to map.".format(layer))

            opts = EA_UTILITY.get_all_linestyles(doc)
            res = forms.SelectFromList.show(opts,
                                            multiselect = False,
                                            title = "Original Rhino layer name: {}.".format(layer),
                                            button_name = "Pick a linestyle to map into".format(layer))
            if res is not None:
                OST_style = EA_UTILITY.get_linestyle(doc, res)
            else:
                temp_name = EA_UTILITY.get_all_linestyles(doc)[0]
                OST_style = EA_UTILITY.get_linestyle(doc, temp_name)
        return OST_style
        #print "something wrong"
        #print OST_style
        #print "end"
        #return None


    def map_detailitem_OST(layer):
        OST_style = EA_UTILITY.get_subc(doc, layer, in_cate = "Detail Items")
        if OST_style is None:
            EA_UTILITY.dialogue(main_text = "Rhino Layer [{}] does not have a matching detail items subC in revit, please rename in Rhino and reexport, or pick a subC now to map.".format(layer))

            opts = EA_UTILITY.get_all_subcs(doc, in_cate = "Detail Items")
            opts = [x.Name for x in opts]
            res = forms.SelectFromList.show(opts,
                                            multiselect = False,
                                            title = "Original Rhino layer name: {}.".format(layer),
                                            button_name = "Pick a subC to map into".format(layer))
            if res is not None:
                OST_style = EA_UTILITY.get_subc(doc, res, in_cate = "Detail Items")
            else:

                OST_style = EA_UTILITY.get_all_subcs(doc, in_cate = "Detail Items")[0]
        return OST_style

    def map_fill_region_type(raw_name):
        type_name = raw_name.split("::")[-1]
        types = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).ToElements()
        for type in types:
            if type.LookupParameter ("Type Name").AsString()== type_name:
                return type
        EA_UTILITY.dialogue(main_text = "Rhino Layer [{}] does not have a matching FilledRegion type in revit, please rename in Rhino and reexport, or pick a type now to map.".format(type_name))

        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "{}".format(self.item.LookupParameter ("Type Name").AsString())
        res = forms.SelectFromList.show([MyOption(x) for x in types],
                                        multiselect = False,
                                        title = "Original Rhino layer name: {}.".format(type_name),
                                        button_name = "Pick a region type to map into")

        if res is not None:
            return res
        else:
            return types[0]






    for layer in unique_layers:

        #deal with srf first
        if "FilledRegion" in layer:
            DICT_ost_mapping[layer] = map_fill_region_type(layer)
            #print DICT_ost_mapping[layer]
            continue

        #then deal with lines
        if doc.IsFamilyDocument:
            OST_style = map_detailitem_OST(layer)
        else:
            #EA_UTILITY.print_note("using line mode")
            OST_style = map_line_OST(layer)
        DICT_ost_mapping[layer] = OST_style
    #print data

    # map layer name to line style OST if cannot find, ask user


    # map: for each data, create line, or arc detail line
    t = DB.Transaction(doc, "transfering rhino drafting")
    t.Start()

    new_elements = []
    for data in datas:
        #print data
        new_elements.append(process_data(doc, data, DICT_ost_mapping))

    t.Commit()

    # group new coming with time stamp
    new_elements = filter(lambda x: x is not None, new_elements)
    new_element_ids = [x.Id for x in new_elements]
    group_contents(doc, new_element_ids)




    EA_UTILITY.show_toast(title = "Draft content created!")
    import ENNEAD_LOG
    ENNEAD_LOG.use_enneadtab(coin_change = 30, tool_used = "Rhino2Revit_Rhino Draft Import", show_toast = True)




def group_contents(doc, new_element_ids):
    t = DB.Transaction(doc, "grouping content")
    t.Start()
    doc_create = get_doc_create(doc)
    with ErrorSwallower() as swallower:
        group = doc_create.NewGroup(EA_UTILITY.list_to_system_list(new_element_ids))

        group.GroupType.Name = "EA_Rhino_Drafting_Transfer_({}_{})".format(doc.ActiveView.Name,
                                                                EA_UTILITY.get_formatted_current_time())
    t.Commit()
    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":

    transfer_rhino_drafting(doc = __revit__.ActiveUIDocument.Document # pyright: ignore)


    #print "\n\n----------tool finished."
