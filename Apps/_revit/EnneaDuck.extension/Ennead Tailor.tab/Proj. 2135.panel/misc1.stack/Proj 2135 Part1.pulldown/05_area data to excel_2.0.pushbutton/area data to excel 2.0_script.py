__doc__ = "Gather the data of GFA area plans and publish it to Excel in the format requested by the client."
__title__ = "05_area to excel 2.0, N3 Only"
__youtube__ = "https://youtu.be/wom2_hzjBi0"
from pyrevit import forms, DB, revit, script
import xlsxwriter as xw
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()



def check_area_content(area, fix = False):
    #check discount ration, and if not department infor presented
    #print str((area.LookupParameter("MC_$Discount Ratio").AsDouble() ))
    #print area.LookupParameter("MC_$Discount Ratio").HasValue
    if not area.LookupParameter("MC_$Discount Ratio").HasValue:
        if not fix:
            return False
        main_msg = "Area {}:{}:{} does not have a discount ratio value, do you want to give it as  [.....]".format(revit.doc.GetElement(area.LevelId).Name, area.LookupParameter("Area Department").AsString(),area.LookupParameter("Name").AsString())
        #print main_msg
        ratio_values = ["0","0.5","1"]
        ratio = float(forms.alert(options = ratio_values , msg = main_msg))
        area.LookupParameter("MC_$Discount Ratio").Set(ratio)
    #ask to fix? show detail information
    return True

def find_level_row_in_excel(level):
    initial_row = 7
    if "ROOF LEVEL" in level.Name:
        return initial_row + 33 - 1

    #print level.Name
    if "roof" in level.Name.lower():
        level_num = 33

    elif "bh" in level.Name.lower():
        level_num = 34
    else:
        #print level.Name
        level_num = level.Name.split("LVL")[1].replace("(REFUGE)","")
    return initial_row + int(level_num) - 1


def find_area_definition_column_in_excel(area):
    global special_departments
    global area_name_checklist
    department_name = area.LookupParameter("Area Department").AsString()
    area_name = area.LookupParameter("Name").AsString()

    if department_name in special_departments:
        column = area_name_checklist.index(department_name)
    else:
        try:
            column = area_name_checklist.index(area_name)
        except:
            print("area department:area name = '{}':'{}'.  Not found in chart".format(department_name, area_name))
            column = -2


    initial_column = 2
    return initial_column + column



class data_item():
    def __init__(self, area):
        self.area_num = area.Area * area.LookupParameter("MC_$Discount Ratio").AsDouble()
        self.area_obj = area
        self.row = find_level_row_in_excel(area.Level)
        self.column = find_area_definition_column_in_excel(area)

    def update_data_item_area(self, new_area):
        #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$adding more area to data item-----------"
        self.area_num += new_area.Area * new_area.LookupParameter("MC_$Discount Ratio").AsDouble()

    def print_data_detail(self):
        print("data item detail:{};{}:{}..row:{}...column:{} ---{}".format(self.area_obj.Level.Name,
                                                    self.area_obj.LookupParameter("Area Department").AsString(),
                                                    self.area_obj.LookupParameter("Name").AsString(),
                                                    self.row,
                                                    self.column,
                                                    EA_UTILITY.sqft_to_sqm(self.area_num)))





def get_all_areas_in_GFA_scheme(doc = revit.doc):#but not in basement
    all_areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    above_grade_areas = filter(lambda x: "SITE" not in x.Level.Name, all_areas)
    return filter(lambda x: x.AreaScheme.Name == "Gross Building", above_grade_areas)


def alert_bad_areas( doc = revit.doc):
    global special_departments
    global department_name_checklist
    global area_name_checklist
    GFA_scheme_areas = get_all_areas_in_GFA_scheme(doc)
    bad_area_count = 0
    for area in GFA_scheme_areas:
        if area.LookupParameter("Area Department").AsString() in special_departments:# it does not need to list detail name
            continue
        if area.LookupParameter("Area Department").AsString() not in department_name_checklist or area.LookupParameter("Name").AsString() not in area_name_checklist:
            print("------------This item below cannot find place in chart -------------")
            print_area_detail(area)
            bad_area_count += 1
    if bad_area_count != 0 :
        forms.alert("There are {} area with department name or area name not defined. See output window for details".format(bad_area_count))



def is_area_similar_to_data_item(area, data):
    global special_departments
    if data.area_obj.Level.Name != area.Level.Name:
        return False
    if data.area_obj.LookupParameter("Area Department").AsString() != area.LookupParameter("Area Department").AsString():
        return False

    if data.area_obj.LookupParameter("Area Department").AsString() not in special_departments:#if you are part of the special deparmtment, your area name does not matter and we wnat to combine data regardless
        if data.area_obj.LookupParameter("Name").AsString() != area.LookupParameter("Name").AsString():
            return False
    #print "----------------------------------------------------------find similar"
    return True

def print_area_detail(area):
    print("area detail: {};{}:{}--{}".format(area.Level.Name, area.LookupParameter("Area Department").AsString(), area.LookupParameter("Name").AsString(), EA_UTILITY.sqft_to_sqm(area.Area * area.LookupParameter("MC_$Discount Ratio").AsDouble())))


def write_data_item(worksheet, data):

    #cell_format = get_color_format(data)
    worksheet.write(data.row,
                    data.column,
                    float("{:.2f}".format(EA_UTILITY.sqft_to_sqm(data.area_num))))

def write_header(worksheet):
    global area_name_checklist
    global department_office
    global department_retail
    global department_support
    global department_visitor_center
    global department_public_circulation
    global department_others

    header = area_name_checklist
    for i in range(len(header)):
        if i == area_name_checklist.index(department_retail[-1]):
            format = workbook.add_format({'bg_color' : '#FFC000'})
        elif i == area_name_checklist.index(department_office[-1]):
            format = workbook.add_format({'bg_color' : '#DDEBF7'})
        elif i <= area_name_checklist.index(department_visitor_center[-1]):
            format = workbook.add_format({'bg_color' : '#F8CBAD'})
        elif i <= area_name_checklist.index(department_support[-1], len(department_office + department_retail + department_visitor_center)):
            format = workbook.add_format({'bg_color' : '#FFE699'})
        elif i <= area_name_checklist.index(department_public_circulation[-1]):
            format = workbook.add_format({'bg_color' : '#b5c6ba'})
        else:
            format = workbook.add_format({'bg_color' : '#DC9090'})

        worksheet.write(6, i + 2, header[i], format)
        worksheet.set_column(i +2,i+2, 1.3 * max( len(header[i]), 5))



def write_levels(worksheet):
    cell_format = workbook.add_format()
    cell_format.set_bg_color('#808080')
    for i in range(1, 33):
        worksheet.write(i+6, 1 ,  "level {}".format(i), cell_format)
    worksheet.write(i+6+1, 1, "roof level", cell_format)
################## main code below #####################
output = script.get_output()
output.close_others()

check = filter(lambda x: not check_area_content(x, fix = False), get_all_areas_in_GFA_scheme())
if len(check) != 0:
    res = forms.alert(options = ["Fix Now", "Ignore"], msg = "There are {} area that has no discount ratio value assigned, i want to [...]".format(len(check)))
else:
    res = "OK"

if res == "Fix Now":
    with revit.Transaction("Fix up area number"):
        map(lambda x: check_area_content(x, fix = True), get_all_areas_in_GFA_scheme())

#this will also be used as the headers
department_retail = ["RETAIL"]
department_office = ["OFFICE"]
department_visitor_center = ["VISITOR LOBBY",
                            "VISITOR IMAGE DISPLAY",
                            "VISITOR CONFERENCE",
                            "VISITOR TRAINING",
                            "VISITOR FRIENDS RECEPTION",
                            "VISITOR ROUND THEATER",
                            "VISITOR TRAINING TERRACE",
                            "VISITOR CIRCULATION",
                            "VIP/GR CONFERENCE",
                            "VIP/GR LOBBY",
                            "VIP/GR MEETING",
                            "CORE"]
department_support = ["TRAINING",
                    "MULTIFUNCTION HALL",
                    "SERVICE CENTER",
                    "GYM",
                    "LEISURE SPACE",
                    "CORE"]
department_public_circulation = ["PUBLIC CIRCULATION"]
department_others = ["OTHERS"]

area_name_checklist = department_retail +\
                        department_office + \
                        department_visitor_center + \
                        department_support + \
                        department_public_circulation + \
                        department_others

special_departments = ["RETAIL", "OFFICE", "OTHERS","PUBLIC CIRCULATION"]#those deparment can have other name defined and combined to single output
department_name_checklist =  special_departments + ["VISITOR CENTER", "SUPPORT"]



data_collection = []
safety = 0
for area in get_all_areas_in_GFA_scheme():
    safety += 1
    if safety > 1500:
        break

    #print_area_detail(area)
    #print "---"

    if len(data_collection) == 0:
        data_collection.append(data_item(area))
        continue

    found_similar = False
    for data in data_collection:
        #data.print_data_detail()
        if is_area_similar_to_data_item(area, data):
            #print "find similar"
            data.update_data_item_area(area)
            found_similar = True
            break
        else:
            #print "data item not similar, keep looking"
            #keep looking
            pass
    if not found_similar:
        #print "no similar data found, adding to collection"
        data_collection.append(data_item(area))




# Create a workbook and add a worksheet.
#forms.save_excel_file()
file_location = forms.save_excel_file()
workbook = xw.Workbook(file_location)
worksheet = workbook.add_worksheet("N3 AREA CHART")

#print data_collection
print("*"*50)
for data in data_collection:
    data.print_data_detail()
    write_data_item(worksheet, data)



write_levels(worksheet)
write_header(worksheet)
try:
    workbook.close()
    forms.alert("Excel saved at '{}'".format(file_location))
except:
    forms.alert("the excel file you picked is still open, cannot override. Writing cancelled.")


alert_bad_areas()
