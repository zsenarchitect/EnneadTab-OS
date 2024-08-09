

from Autodesk.Revit import DB # pyright: ignore
from pyrevit import script


from EnneadTab.REVIT import REVIT_VIEW, REVIT_UNIT, REVIT_FAMILY
from EnneadTab import USER, ENVIRONMENT




def validate_all(UI):
    """make all the test in one func so it is esier to check in the main script.
    there should only return one true or false
    """

    # make sure the container view exsit
    validate_container_view(UI.doc, UI.option)


    # make sure the final schdule view is meeting the requeirement
    validate_schedule_view(UI.doc, UI.option)


    # print current process logic to user
    show_logic(UI.doc, UI.option, UI.show_log)
    
    
    # make sure the calcualator family is a good family
    if not is_family_valid(UI.doc, UI.option):
        return False

    # test if each type has exactly one instance
    if not is_family_types_valid(UI.doc, UI.option):
        return False

    return True


def show_logic(doc, option, show_log):
    output = script.get_output()
    if not show_log:
        return

    output.print_md("## Logic for [{}]".format(option.formated_option_name))
    note = ""

    note += "The AreaScheme used for department data is [{}]".format(option.DEPARTMENT_AREA_SCHEME_NAME)
    note += "\nThe parameter used in getting category is [{}]".format(option.DEPARTMENT_KEY_PARA)
    note += "\nThe AreaScheme used for overall data is [{}]".format(option.OVERALL_AREA_SCHEME_NAME)
    note += "\nAny valid area will count toward overall area."
    
    
    note += "\nThe family used in checking is [{}]".format(option.CALCULATOR_FAMILY_NAME)


    container_view = REVIT_VIEW.get_view_by_name(option.CALCULATOR_CONTAINER_VIEW_NAME, doc = doc)
    note += "\nThe view used to contain all calculator is [{}]".format(output.linkify(container_view.Id, 
                                                                                         title=option.CALCULATOR_CONTAINER_VIEW_NAME))
    
    
    schedule_view = REVIT_VIEW.get_view_by_name(option.FINAL_SCHEDULE_VIEW_NAME, doc = doc)
    note += "\nThe view used to contain final schedule is [{}]".format(output.linkify(schedule_view.Id, 
                                                                                         title=option.FINAL_SCHEDULE_VIEW_NAME))


    note += "\n\nThe level names used in checking is below:"
    for x in option.LEVEL_NAMES:
        note += "\n   -[{}]".format(x)
        
        
        
    note += "\n\nThe value of area should fall in to one of below so it can match the excel table:"
    for para, nick_name in option.PARA_TRACKER_MAPPING.items():
        note += "\n   -[{}]-->[{}]".format(para, nick_name)
        
    note += "\n\nWhen the department category of area is not part of the above mapping table, it should alert exception. HOWEVER, category in below list will silent the alert, and they will NOT count toward department calculation."
    for para in option.DEPARTMENT_IGNORE_PARA_NAMES:
        note += "\n   -Ingore [{}]".format(para)


    note += "\n\nUnder the hood, Here is how the script logic is handled:"
    note += "\n1, search through all the area in area scheme [{}], ignoring area on levels that not part of the defined Level Names".format(option.DEPARTMENT_AREA_SCHEME_NAME)
    note += "\n2, Look at the parameter [{}] of the area, map that value to the Excel version, and add the area to the related field of the level".format(option.DEPARTMENT_KEY_PARA)
    note += "\n3, Search through all the area in area scheme [{}], add any area to the overall area of this level".format(option.OVERALL_AREA_SCHEME_NAME)
    note += "\n4, Search through all the calculator types in the family [{}], get the predefined Factor in this level, apply that factor to each blue column data. Overall GFA and MERS are excluded in this act, they use factor 1 always".format(option.CALCULATOR_FAMILY_NAME)
    note += "\n5, The unfactored sum of blue coloumn is filled to [{0}], and [{1}] is completed by {0}x{2}".format(option.DESIGN_SF_PARA_NAME, option.ESTIMATE_SF_PARA_NAME, option.FACTOR_PARA_NAME)
    note += "\n6, after all the level based data is filled out, a dummy summery is filled by summing up the similar paramter names above."
    note += "\n7, the target data is left untouched. THE TEAM IS EXPECTED TO FILL IN THOSE INFO BASED ON YOUR DESIRED TARGET. The delta is caulated by looking up the difference between dummy summery and manual target."
    note += "\n8, after main option is processed, option is look into to primaryu area scheme and copy over data that is not BEDS."

    
    note += "\n\nOk ok, enough talking, let's start checking....\n\n\n"

    print(note)




def validate_container_view(doc, option):
    # test if container view exist
    view = REVIT_VIEW.get_view_by_name(option.CALCULATOR_CONTAINER_VIEW_NAME, doc = doc)
    if view:
        return

    t = DB.Transaction(doc, "Making Container View")
    t.Start()
    view = DB.ViewDrafting.Create(doc, 
                                  REVIT_VIEW.get_default_view_type("drafting").Id)
    view.Name = option.CALCULATOR_CONTAINER_VIEW_NAME
    view.Scale = 250
    t.Commit()


def validate_schedule_view(doc, option):
    # test if schedule view exist
    view = REVIT_VIEW.get_view_by_name(option.FINAL_SCHEDULE_VIEW_NAME, doc = doc)
    if not view:
        t = DB.Transaction(doc, "Making Final Schedule View")
        t.Start()
        view = DB.ViewSchedule.CreateNoteBlock(doc, REVIT_FAMILY.get_family_by_name(option.CALCULATOR_FAMILY_NAME, doc).Id ) 
        # view = DB.ViewSchedule.CreateSchedule (doc, 
        #                                         DB.Category.GetCategory(doc,
        #                                                                 DB.BuiltInCategory.OST_GenericAnnotation).Id)
        view.Name = option.FINAL_SCHEDULE_VIEW_NAME
        t.Commit()
        
        format_schedule(doc, option)

def format_schedule(doc, option):
    if not USER.is_SZ():
        return
    # test if schedule has all required parameters as field
    # create a schedule with defined rules(get viewschedule.definition, then add field, and set order)
    view = REVIT_VIEW.get_view_by_name(option.FINAL_SCHEDULE_VIEW_NAME, doc = doc)

    t = DB.Transaction(doc, "Check schedule contents.")
    t.Start()
    definition = view.Definition
    field_names = []  
    for index in range(definition.GetFieldCount()):
        field = definition.GetField(index)
        field_names.append(field.GetName())
        
        
        # options = field.GetFormatOptions()
        # style = field.GetStyle()
        # overrideOptions = style.GetCellStyleOverrideOptions()
        # overrideOptions.BackgroundColor = True
        # style.BackgroundColor = DB.Color(100,100,100)
        
        
        if field.GetName() not in option.FAMILY_PARA_COLLECTION:
            print ("[{}] should not appear in the schedule field".format(field.GetName()))
            definition.RemoveFeild(field.Id)
    
    def get_schedulable_field_by_name(name):
        for schedulable_field in definition.GetSchedulableFields():
            if schedulable_field.GetName(doc) == name:
                return schedulable_field
        return None
    
    
    for para_name in option.FAMILY_PARA_COLLECTION:
        if para_name not in field_names:
            print ("[{}] should be added to the field".format(para_name))
          
            new_field = get_schedulable_field_by_name(para_name)
            definition.AddField (new_field)
            
            
    def get_field_id_by_name(name):
        for index in range(definition.GetFieldCount()):
            field = definition.GetField(index)
            if field.GetName() == name:
                return field.Id
        return None
            
    # set order
    # order = [get_field_id_by_name(x) for x in SCHEDULE_FIELD_ORDER]
    # definition.SetFieldOrder(EnneadTab.DATA_CONVERSION.list_to_system_list(order, use_IList=True))
    
    
    
    
    t.Commit()
    # TO-DO

    # test if each schedule field is the right format(align to right, set whole number, digit grouping)
    # TO-DO
    pass


def is_family_types_valid(doc, option):

    #  make sure the entire collection of family types is exactly matching the level names, so perform the following two steps.
    # 1, each type should have one and only one instance in the project
    validate_singular_instance(doc, option)
       
    # 2, removing unrelated type from the project.
    remove_unrelated_types(doc, option)
    
    
    
    # set order index for each type. This will set the display order in schdeule
    set_type_order_index(doc, option)

    return True

def validate_singular_instance(doc, option):
    # make sure each type is placed exactly once
    for type_name in option.TYPE_NAME_COLLECTION:

        
        calcs = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(option.CALCULATOR_FAMILY_NAME, type_name, doc)
        if calcs is None:
            # make new type and place on the container view
            make_new_calcualtor(doc, option, type_name)
            continue

        foot_note = "level [{}]".format(type_name) if type_name in option.LEVEL_NAMES else "dummy data block [{}]".format(type_name)
        if calcs is not None and len(calcs) == 1:
            
            """maybe consideering force the data block in containner view only, but maybe team wants to have it in area plan view."""
            continue

        # when it is not 1, I want to make sure it is 1!
        elif len(calcs) > 1:
            print("Too many calculator found for {}. Resetting now...".format(foot_note))
        else:
            print("No calculator found for level {}. Creating now...".format(foot_note))

        # try to purge this type first
        purge_type_by_name(doc, option, type_name)

        # make new type and place on the container view
        make_new_calcualtor(doc, option, type_name)


def purge_type_by_name(doc, option, type_name):
    calc_type = REVIT_FAMILY.get_family_type_by_name(option.CALCULATOR_FAMILY_NAME, type_name, doc)
    if calc_type:
        t = DB.Transaction(doc, "Purge Useless Type")
        t.Start()
        doc.Delete(calc_type.Id)
        t.Commit()

def make_new_calcualtor(doc, option, type_name):
    t = DB.Transaction(doc, "Making new type [{}]".format(type_name))
    t.Start()
    new_type = REVIT_FAMILY.get_all_types_by_family_name(option.CALCULATOR_FAMILY_NAME, doc)[0].Duplicate(type_name)
    new_type.Activate()
    doc.Regenerate()

    
    
    unit_distant = 75
    if type_name in option.LEVEL_NAMES:
        index = option.LEVEL_NAMES.index(type_name)
        row_count = 5
        x, y = index % row_count, index // row_count
    if type_name in option.DUMMY_DATA_HOLDER:
        index = option.DUMMY_DATA_HOLDER.index(type_name)
        x = index
        y = -2
        
    doc.Create.NewFamilyInstance(DB.XYZ(unit_distant*x, unit_distant*y, 0), 
                                        new_type,
                                        REVIT_VIEW.get_view_by_name(option.CALCULATOR_CONTAINER_VIEW_NAME, doc = doc))
    t.Commit()
    
    
def remove_unrelated_types(doc, option):
    for calc_type in REVIT_FAMILY.get_all_types_by_family_name(option.CALCULATOR_FAMILY_NAME, doc):
        type_name = calc_type.LookupParameter("Type Name").AsString()

        if type_name not in option.TYPE_NAME_COLLECTION:
            print("Extra type [{}] found . Deleting now...".format(type_name))

            t = DB.Transaction(doc,"Delete extra type [{}]".format(type_name))
            t.Start()
            doc.Delete(calc_type.Id)
            t.Commit()



def set_type_order_index(doc, option):
    
    for calc_type in REVIT_FAMILY.get_all_types_by_family_name(option.CALCULATOR_FAMILY_NAME, doc):
        type_name = calc_type.LookupParameter("Type Name").AsString()
        if type_name in option.LEVEL_NAMES:
            order_index = option.LEVEL_NAMES.index(type_name)
        elif type_name in option.DUMMY_DATA_HOLDER:
            order_index = option.DUMMY_DATA_HOLDER[::-1].index(type_name) - 100
        else:
            print ("!!!!!!!!!!!!!!!!![{}], is not a valid type name".format(type_name))
        
        
        """
        not need to deal with elevation to sort. Use order_index instead
        if type_name in LEVEL_NAMES:
            level = REVIT_SELECTION.get_level_by_name(type_name)
            level_elevation = level.Elevation
        if type_name in DUMMY_DATA_HOLDER:
            # make sure the dummy data is placed at the butotom of shcedule. That schedule is ranked elevation
            level_elevation = -100 * (DUMMY_DATA_HOLDER.index(type_name)+1)
        """
            
            
        current_index = calc_type.LookupParameter(option.INTERNAL_PARA_NAMES["order"]).AsInteger()
        current_level_display = calc_type.LookupParameter(option.INTERNAL_PARA_NAMES["title"]).AsString()
        if current_index != order_index or current_level_display != type_name:
            print ("Fixing order index/title display of [{}]".format(type_name))
            t = DB.Transaction(doc, "Set order index for [{}]".format(type_name))
            t.Start()
            calc_type.LookupParameter(option.INTERNAL_PARA_NAMES["title"]).Set(type_name)
            calc_type.LookupParameter(option.INTERNAL_PARA_NAMES["order"]).Set(order_index)

            # calc_type.LookupParameter("level_elevation").Set(level_elevation)
            t.Commit()
            
            
            

def is_family_valid(doc, option):

    # make sure family exists
    sample_family_path = "{}\\Contents.panel\\2D Contents.pulldown\\HealthCare Data Calculator.content\\EnneadTab AreaData Calculator_content.rfa".format(ENVIRONMENT.REVIT_LIBRARY_TAB)
    REVIT_FAMILY.get_family_by_name(option.CALCULATOR_FAMILY_NAME, doc, load_path_if_not_exist=sample_family_path)
    

    # test if type has all required parameters names
    # by get one fam type and get paras to iterate thru. only process to open fam when para names not match. and attempt to fix
    missing_para_names = get_missing_para_names(doc, option)


    # test if the formula used in family is correct .....
    # maybe do not use fomula in family, try to handle all in python side
    # TO-DO
    if len(missing_para_names) != 0:
        fix_missing_para(doc, option, missing_para_names)
    
    return True


def get_missing_para_names(doc, option):
    sample_type = REVIT_FAMILY.get_all_types_by_family_name(option.CALCULATOR_FAMILY_NAME, doc)[0]
    current_para_names = [para.Definition.Name for para in sample_type.Parameters]

    missing_para_names = []
    for para_name in option.FAMILY_PARA_COLLECTION:
        if para_name not in current_para_names:
            print("Missing parameter [{}] . Please add...otherwise the number might read wrong at end".format(para_name))
            missing_para_names.append(para_name)

    return missing_para_names


def fix_missing_para(doc, missing_para_names, option):
    family = REVIT_FAMILY.get_family_by_name(option.CALCULATOR_FAMILY_NAME, doc)
    fam_doc = doc.EditFamily(family)
    manager = fam_doc.FamilyManager

   
    t = DB.Transaction(fam_doc, "Adding missing paras")
    t.Start()
    for para_name in missing_para_names:
    
        print("Missing parameter [{}] . Adding...".format(para_name))
        
        # here i am assuming any new parameter added later in life cycle is all about area relarted. 
        # Other type nof para should have been set by the sampler family when loaded.
        para_group = DB.GroupTypeId.General 
        para_type = REVIT_UNIT.lookup_unit_spec_id("area")
        manager.AddParameter(para_name, para_group,para_type, False)
    t.Commit()
    
    doc.LoadFamily(fam_doc)
    fam_doc.Close(False)