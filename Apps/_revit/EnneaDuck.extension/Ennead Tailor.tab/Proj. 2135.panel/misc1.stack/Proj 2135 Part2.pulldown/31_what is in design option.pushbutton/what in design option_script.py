#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Legacy, now you can do better in color code design option"
__title__ = "31_what is in design option?(Legacy)"

from pyrevit import script, forms #
from Autodesk.Revit import DB # pyright: ignore 
doc = __revit__.ActiveUIDocument.Document # pyright: ignore



def print_detail(elements):
    dict = {}

    for element in elements:
        type = str(element.GetType()).replace("Autodesk.Revit.DB.","")
        if type not in dict.keys():
            dict[type] = [element]
        else:
            dict[type].append(element)

    """
    class MyOption2(forms.TemplateListItem):

        @property
        def name(self):

            return "[{}]  {}".format(key, self)
    ops = [MyOption2(x) for x in dict]

    """
    for key in dict.keys():
        for item in dict[key]:
            display = get_display_text(item)
            print("[{}] {}, {}".format(key, display, output.linkify(item.Id)))

    print("*"*20)

    for key in dict.keys():
        print("{} {} elements".format(len(dict[key]), key))

def get_display_text(item):
    for check in ["FamilyInstance", "Panel"]:
        if check in str(item.GetType()):
            display = "{}:{}".format(item.Symbol.FamilyName, item.Name)
            break
    else:
        try:
            display = item.Name
        except:
            display = item.Id

    return display
################## main code below #####################
output = script.get_output()
output.close_others()

design_options = DB.FilteredElementCollector(doc).OfClass(DB.DesignOption).ToElements()


class MyOption(forms.TemplateListItem):
    def get_option_set_name(self):
        return doc.GetElement(self.Parameter[DB.BuiltInParameter.OPTION_SET_ID].AsElementId()).Name

    @property
    def name(self):
        set_name = self.get_option_set_name()
        return "[{}]  {}".format(set_name, self.Name)

ops = [MyOption(x) for x in design_options]
ops.sort(key = lambda x: x.get_option_set_name())
design_option = forms.SelectFromList.show(ops,
                                multiselect=False,
                                button_name='Select option')
# print res


elements = list(DB.FilteredElementCollector(doc).ContainedInDesignOption(design_option.Id).ToElements())
new_list = []
for x in elements:
    for check in ["Panel", "Sketch", "CurtainGridLine", "Dimension", "ElementType","StairsLanding","StairsRun", "FamilySymbol"]:
        #print str(x.GetType())
        if check in str(x.GetType()):
            # elements.remove(x)
            #print "-"*200
            break
    else:
        new_list.append(x)
new_list.sort(key = lambda x: get_display_text(x))
print_detail(new_list)

output.freeze()
print("*"*100)
children = []
parent_elements = []
for element in elements:

    print("*****")
    print(str(element.GetType()))
    child = element.GetDependentElements (None)
    if len(list(child)) <= 1:
        print("-------------------no depdent")
    else:
        print(len(list(child)))
        parent_elements.append(element)
    temp = [str(x.GetType()) for x in list(child)]
    print(temp)
    children.extend([doc.GetElement(x) for x in child])
# children = list(set(children))
# print len(children)
parents = set(elements).difference(set(children))
print_detail(parents)
output.unfreeze()


"""
new_elements = elements[:]
# print len(new_elements)
for child in children:
    if child in elements:
        print("remove****************************")
        new_elements.remove(child)
# print len(new_elements)
print_detail(new_elements)
"""
