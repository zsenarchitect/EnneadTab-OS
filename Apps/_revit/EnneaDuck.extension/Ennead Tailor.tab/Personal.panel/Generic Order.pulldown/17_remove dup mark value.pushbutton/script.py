#from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
from pyrevit import coreutils
output = script.get_output()
output.close_others()


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
__title__ = "remove dup value"
__doc__ = 'remove dup value in warning'



def process_warning(warning):

    des =  warning.GetDescriptionText()
    print(des)
    key = ""
    if "have duplicate" in des:
        if "Number" in des:
            key = "Number"
        elif "Mark" in des:
            key = "Mark"
    if  key == "":
        return
    print ("#{0} {1}:".format(counter, warning.GetSeverity()))

    error_els = warning.GetFailingElements()
    for error_el in error_els:
        print ("Element Id = {0}-->{1}".format(error_el,output.linkify(error_el, title = "Go To Element")))
        if key != "":
            el = revit.doc.GetElement(error_el)
            current_owner = el.LookupParameter("Edited by").AsString()
            if current_owner != "" and current_owner != EnneadTab.USER.get_autodesk_user_name():
                print("skip element ownded by {}".format(current_owner))
                continue
            try:
                old_value = el.LookupParameter(key).AsString()
                new_value = old_value + "_ID: " + str(el.Id)
                el.LookupParameter(key).Set(new_value)
            except Exception as e:
                print (e)
    #print warning.GetType()

    try:
        print ("Try {}.".format(warning.GetDefaultResolutionCaption()))
    except:
        pass
        #print "There are No default Resolution."


    #script.insert_divider(level = "")
    print("-------------------------------------")

class w_dict:
    def __init__(self, description):
        self.description = description
        self.count = 1

    def new_data(self):
        self.count += 1



#-------------main code below-------------
#output.freeze()
counter = 0
all_warnings = revit.doc.GetWarnings()
unique_warning_description = set() #used to
warning_dicts = []
for warning in all_warnings:
    counter += 1
    #process_warning(warning)
    #print warning.GetDescriptionText()
    current_description = warning.GetDescriptionText()
    error_els = warning.GetFailingElements()
    cate_involved = list(set([revit.doc.GetElement(x).Category.Name for x in error_els]))
    cate_involved.sort()
    current_description = "{}_{}".format(current_description, cate_involved)
    if current_description not in unique_warning_description:
        warning_dicts.append(w_dict(current_description))
        unique_warning_description.add(current_description)
    else:
        for w in warning_dicts: # update count number only for those existing warning
            if current_description == w.description:
               w.new_data()


#print unique_warning_description
#print len(unique_warning_description)
#print warning_dicts

select_list = []
for item in warning_dicts:
    #print item.description
    #print item.count
    select_list.append("{" + str(item.count) + "}: " + str(item.description))
#output.unfreeze()


selected_warnings_raw = forms.SelectFromList.show(select_list, title = "Select the warnings you want to expand.", button_name='Select Warnings',multiselect  = True)
#selected_warnings_raw = select_list
#print selected_warnings_raw


if selected_warnings_raw == None:
    script.exit()

if len(selected_warnings_raw) == 0:
    script.exit()

selected_warnings = []
for item in selected_warnings_raw:
    selected_warnings.append(item.split("}: ")[1])
#print selected_warnings

output.freeze()
counter = 0
with revit.Transaction("remove dup"):
    for warning in all_warnings:
        current_description = warning.GetDescriptionText()
        error_els = warning.GetFailingElements()
        cate_involved = list(set([revit.doc.GetElement(x).Category.Name for x in error_els]))
        cate_involved.sort()
        current_description = "{}_{}".format(current_description, cate_involved)
        if current_description in selected_warnings:
            process_warning(warning)
            counter += 1
output.unfreeze()


print ("There are totally {} warnings in the projects.\nCurrently reviewing {} warnings".format(len(all_warnings), counter))






#output.open_url("https://knowledge.autodesk.com/support/revit-products/troubleshooting/caas/CloudHelp/cloudhelp/2019/ENU/Revit-Troubleshooting/files/GUID-F0945713-4389-4F8E-B5DB-DCE03A8C1ADF-htm.html")
