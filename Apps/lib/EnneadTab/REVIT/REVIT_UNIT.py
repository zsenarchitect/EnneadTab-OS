#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    from Autodesk.Revit import DB # pyright: ignore
except:
    pass

try:
    import REVIT_FORMS
except:
    pass


def get_doc_length_units(doc):
    unit = doc.GetUnits()

    length_spec = lookup_unit_spec_id("length")
    format_option = unit.GetFormatOptions (length_spec)
    #print format_option.GetUnitTypeId()
    return format_option.GetUnitTypeId()

def is_doc_unit_mm(doc):
    return get_doc_length_units(doc) == lookup_unit_id(key = "millimeters")

def is_doc_unit_feet(doc):
    return get_doc_length_units(doc) == lookup_unit_id(key = "feet")

def is_doc_unit_inches(doc):
    return get_doc_length_units(doc) == lookup_unit_id(key = "inches")

def pick_incoming_file_unit(main_text = "What is the file unit of the incoming file?"):
    opts = ["Millimeters", "Feet"]
    res = REVIT_FORMS.dialogue( title = "EnneadTab: Pick incoming file unit.",
                                main_text = main_text,
                                sub_text = None,
                                options = opts)
    return opts.index(res)



def sqft_to_sqm(x):
    try:
        return DB.UnitUtils.ConvertFromInternalUnits(x, lookup_unit_id("squareMeters"))
    except:
        return DB.UnitUtils.ConvertFromInternalUnits(x, DB.DisplayUnitType.DUT_SQUARE_METERS)
    #return x/10.764

def sqm_to_internal(x):
    try:
        return DB.UnitUtils.ConvertToInternalUnits(x, lookup_unit_id("squareMeters"))
    except:
        return DB.UnitUtils.ConvertToInternalUnits(x, DB.DisplayUnitType.DUT_SQUARE_METERS)
    #return x/10.764

def internal_to_mm(x):
    try:
        return DB.UnitUtils.ConvertFromInternalUnits(x, lookup_unit_id("millimeters"))
    except:
        return DB.UnitUtils.ConvertFromInternalUnits(x,DB.DisplayUnitType.DUT_MILLIMETERS)
    #forge_type_id = GetUnitTypeId()
    #return DB.UnitUtils.ConvertFromInternalUnits(x, forge_type_id)

def mm_to_internal(x):
    try:
        return DB.UnitUtils.ConvertToInternalUnits(x, lookup_unit_id("millimeters"))
    except:
        return DB.UnitUtils.ConvertToInternalUnits (x,DB.DisplayUnitType.DUT_MILLIMETERS)

def m_to_internal(x):
    try:
        return DB.UnitUtils.ConvertToInternalUnits(x, lookup_unit_id("meters"))
    except:
        return DB.UnitUtils.ConvertToInternalUnits(x, DB.DisplayUnitType.DUT_METERS)

def radian_to_degree(radian):
    try:
        return DB.UnitUtils.Convert(radian,
                                    lookup_unit_id("radians"),
                                    lookup_unit_id("degrees"))
    except:
        return DB.UnitUtils.Convert(radian,
                                    DB.DisplayUnitType.DUT_RADIANS,
                                    DB.DisplayUnitType.DUT_DECIMAL_DEGREES)

"""

  // Pre 2021

  DisplayUnitType displayUnitType = fp.DisplayUnitType;
  value = UnitUtils.ConvertFromInternalUnits(
    nullable.Value, displayUnitType ).ToString();

  //2021

  ForgeTypeId forgeTypeId = fp.GetUnitTypeId();
  value = UnitUtils.ConvertFromInternalUnits(
    nullable.Value, forgeTypeId ).ToString();
"""
def lookup_unit_id(key):
    """
    feet
    inches
    meters
    millimeters

    squareFeet
    squareInches
    squareMeters

    radians
    degrees
    """
    for unit_type_id in DB.UnitUtils.GetAllUnits():
        if key == str(unit_type_id.TypeId).split("-")[0].split("unit:")[1]:
            return unit_type_id



def lookup_unit_spec_id(key):
    """
    length
    number
    area
    angle
    yesno
    text
    integer
    
    """
    #for x in dir(DB.UnitUtils):
        #print x
    

    """ these if-if-if is stupid, should format it to a dictionary or parsing function
    # also  look at multiline text, images, urls, and other interesting forgetypeID"""
    # https://www.revitapidocs.com/2022/901adcef-5279-8855-f267-6bb1f53621ca.htm
    # https://www.revitapidocs.com/2022/53b81699-df25-f340-3d4d-8e8fb3ed1e71.htm
    # https://www.revitapidocs.com/2022/3f507360-05c2-b25f-df4f-06f104fb0a6b.htm
    # https://www.revitapidocs.com/2022/e6410045-9c5a-7f2d-2805-3d5828aceb66.htm
    # https://www.revitapidocs.com/2022/cd7d3c3d-b476-9579-1a30-b6b82f1a66d7.htm
    #
    # 
    if key == "yesno":
        return DB.SpecTypeId.Boolean.YesNo
    if key == "length":
        return DB.SpecTypeId.Length
    if key == "text":
        return DB.SpecTypeId.String.Text
    if key == "integer":
        return DB.SpecTypeId.Int.Integer
    if key == "number":
        return DB.SpecTypeId.Number
    
    try:
        specs = DB.UnitUtils.GetAllMeasurableSpecs ()
    except:
        specs = DB.UnitUtils.GetAllSpecs ()
    for spec_type_id in specs:
        # print spec_type_id.TypeId
        if not "aec:" in str(spec_type_id.TypeId):
            continue
        if key == str(spec_type_id.TypeId).split("-")[0].split("aec:")[1]:
            return spec_type_id


def get_unit_spec_name(forge_id):
    if forge_id.NameEquals(DB.SpecTypeId.Length):
        return "Length"
    if forge_id.NameEquals(DB.SpecTypeId.Number):
        return "Number"
    if forge_id.NameEquals(DB.SpecTypeId.Boolean.YesNo):
        return "YesNo"
    if forge_id.NameEquals(DB.SpecTypeId.String.Text):
        return "Text"
    if forge_id.NameEquals(DB.SpecTypeId.Int.Integer):
        return "Integer"
    
    return forge_id.TypeId
