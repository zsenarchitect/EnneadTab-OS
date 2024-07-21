#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Merge a few family types to a target family type: \n\nFor instance parameters, the tool tries to record as much information as it can, so after the merging, similar data can be applied back to maintain the graphical consistency.\n\nThere is a built-in check that will search for differences in type parameter data. Should differences be found, you will be prompted to decide to continue with merge or cancel.\n\nIf you find no ideal target type, you may also choose to create a new type under good family with the bad type data and type name.\n\nThis tool will work for most 2D and 3D families, as well as Tags."
__title__ = "Merge\nFamily"
__youtube__ = "https://youtu.be/xZhCxpuQKCs"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29705"
__tip__ = True
from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException



from pyrevit.revit import ErrorSwallower
from pyrevit import script, forms


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import IMAGE, NOTIFICATION, DATA_CONVERSION, ERROR_HANDLE


import traceback
import random
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
# uidoc = __revit__.ActiveUIDocument
# doc = __revit__.ActiveUIDocument.Document # pyright: ignore
__persistentengine__ = True


@ERROR_HANDLE.try_catch_error()
def get_all_instance_of_type(type, active_view_only):

    if active_view_only:
        filtered_collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id)
    else:
        filtered_collector = DB.FilteredElementCollector(doc)

    type_filter = DB.FamilyInstanceFilter (doc, type.Id)


    instances = list(filtered_collector.OfClass(DB.FamilyInstance).WherePasses (type_filter).ToElements())
    #print instances
    #print type
    #print type.Id

    all_independent_tags = list(filtered_collector.OfClass(DB.IndependentTag  ).WhereElementIsNotElementType().ToElements())
    independent_tags = filter(lambda x: x.GetTypeId() == type.Id, all_independent_tags)

    all_spatial_tags = list(filtered_collector.OfClass(DB.SpatialElementTag ).WhereElementIsNotElementType().ToElements())


    def is_match_type(x):
        if hasattr(x, "RoomTagType"):
            return x.RoomTagType.Id == type.Id

        if hasattr(x, "AreaTagType"):
            return x.AreaTagType.Id == type.Id

        return False

    spatial_tags = filter(is_match_type, all_spatial_tags)

    instances.extend(spatial_tags)
    instances.extend(independent_tags)
    return instances


@ERROR_HANDLE.try_catch_error()
def merge_action(window):
    t = DB.Transaction(doc, __title__)
    t.Start()
    solution = Solution(window.bad_type, window.target_type, window.family_target, window.is_current_view_only)
    text_out = "Merging Finished:\n[{}]: {} --> [{}]: {}".format(solution.bad_type.Family.Name,
                                                                solution.bad_type.LookupParameter("Type Name").AsString(),
                                                                solution.target_type.Family.Name,
                                                                solution.target_type.LookupParameter("Type Name").AsString())
    # get all instacen of bad family, first check can we get a matching type name, record all instacne data
    bad_instances = get_all_instance_of_type(solution.bad_type, solution.is_current_view_only)
    #print len(bad_instances)


    if len(bad_instances) == 0:
        note = "Cannot get anything from {}".format(solution.bad_type.LookupParameter("Type Name").AsString())
        REVIT_FORMS.notification(main_text = note,
                                                sub_text = "There might be no instance of bad type in the file, you should try purging.",
                                                window_title = "EnneadTab",
                                                button_name = "Close",
                                                self_destruct = 15,
                                                window_width = 1200)

        return

    output.print_md( "--Merging **[{}]:{}** ---> **[{}]:{}** ----Found {} Items".format(solution.bad_type.Family.Name,
                                            solution.bad_type.LookupParameter("Type Name").AsString(),
                                            solution.target_type.Family.Name,
                                            solution.target_type.LookupParameter("Type Name").AsString(),
                                            len(bad_instances)))
    #print all_instances
    map(solution.process_instance_recording, bad_instances)
    #envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED")
    #envvars.set_pyrevit_env_var("EA_INSTANCE_DATA_TRANSFER", DATA)

    # change them to good family by matching type name
    map(solution.changing_type, bad_instances)



    # apply the data from record
    map(solution.process_instance_applying, bad_instances)


    solution.cleanup_type()


    NOTIFICATION.messenger(sub_text = "",
                                main_text = "Family Merge Finished!")


    t.Commit()
    window.update_drop_down_selection_source()
    window.debug_textbox.Text = text_out
    window.debug_textbox.FontSize = 12

class Solution:
    def __init__(self, bad_type, target_type, family_target, is_current_view_only):
        self.bad_type = bad_type
        self.family_target = family_target
        if isinstance(target_type, str):
            self.target_type = self.create_new_type(bad_type, family_target)
        else:
            self.target_type = target_type

        self.data = dict()
        self.is_current_view_only = is_current_view_only

    def cleanup_type(self):
        bad_family = self.bad_type.Family

        #always!!!! check whole file, not just current view for type count
        if len(get_all_instance_of_type(self.bad_type, active_view_only = False)) == 0:
            doc.Delete(self.bad_type.Id)

        #DO NOT DO this, this will purge everything
        if len( bad_family.GetFamilySymbolIds ()) == 0:
            doc.Delete(bad_family.Id)

    def changing_type(self, instance):
        if hasattr(instance, "RoomTagType"):
            #print "room tag"
            instance.RoomTagType = self.target_type
            return

        if hasattr(instance, "AreaTagType"):
            #print "area tag"
            instance.AreaTagType = self.target_type
            return


        if hasattr(instance, "Symbol"):
            #print "generic"
            #print bad_instance.Category.Name
            #print bad_instance
            instance.Symbol = doc.GetElement(self.target_type.Id)
            return

        try:
            instance.LookupParameter("Type").Set(self.target_type.Id)
        except Exception as e:

            print ("###Cannot change {} becasue {}".format(output.linkify(instance.Id, title = instance.Category.Name), e))





    def process_instance_recording(self, instance):
        # print "###############"
        # print instance
        # print instance.UniqueId
        data_entry_pack = []
        for para in instance.Parameters:
            definition = para.Definition
            # print definition.Name
            #print para.StorageType
            if para.StorageType == DB.StorageType.Integer:
                #print para.AsInteger()
                data_entry = (definition.Name, "int", para.AsInteger())
            if para.StorageType == DB.StorageType.Double:
                #print para.AsDouble()
                data_entry = (definition.Name, "dbl", para.AsDouble())
            if para.StorageType == DB.StorageType.String:
                #print para.AsString()
                data_entry = (definition.Name, "str", para.AsString())
            if para.StorageType == DB.StorageType.ElementId:
                #print para.AsElementId()
                data_entry = (definition.Name, "id", para.AsElementId())

            data_entry_pack.append(data_entry)


        #DATA[instance.Id.IntegerValue] = para
        self.data[instance.UniqueId] = data_entry_pack
        # print data_entry_pack



    def process_instance_applying(self, instance):

        data_entry_pack = self.data[instance.UniqueId]
        for data_entry in data_entry_pack:
            #print data_entry
            para_name, para_type, value = data_entry


            if para_name in ["Type Id", "Type", 'Family and Type', "Family"]:
                #print "Skip assinging those parameter: {}".format(para_name)
                continue
            para = instance.LookupParameter(para_name)
            if not para:
                print("No matching instance parameter to apply: {}".format(para_name))
                continue

            if para.IsReadOnly:
                #print "<" + para_name + "> is read-only"
                continue

            if value is None:
                continue
                #print "Skip assinging those parameter if has no value in record: {}".format(para_name)

            try:
                if para_type == "str":
                    try:
                        id = DB.ElementId(int(value))
                        para.Set(id)
                    except:
                        para.SetValueString (value)
                else:
                    para.Set(value)
            except Exception as e:
                print (e)
                #print "Cannot assign {} becasue: {}".format(para_name, e)

    def create_new_type(self, bad_type, target_type_family):
        sample_type = doc.GetElement(list(target_type_family.GetFamilySymbolIds ())[0])
        try:
            new_good_type = sample_type.Duplicate(bad_type.LookupParameter("Type Name").AsString())
        except Exception as e:
            print (e)
            return bad_type


        bad_type_paras = bad_type.Parameters
        target_type_paras = new_good_type.Parameters

        def get_para_by_name(type, name):
            for para in type.Parameters:
                if para.Definition.Name == name:
                    return para
            return None


        for bad_para in bad_type_paras:
            para_name = bad_para.Definition.Name

            if para_name in ["Family Name", "Edited by", "Workset"]:
                continue
            good_para = get_para_by_name(new_good_type, para_name)
            if not good_para:
                continue

            if good_para.IsReadOnly :
                continue

            if bad_para.StorageType == DB.StorageType.Integer:
                bad_value = bad_para.AsInteger()
                good_value = good_para.Set(bad_value)
                continue

            if bad_para.StorageType == DB.StorageType.Double:
                bad_value = bad_para.AsDouble()
                good_value = good_para.Set(bad_value)
                continue

            if bad_para.StorageType == DB.StorageType.String:
                bad_value = bad_para.AsString()
                # print para_name
                # print bad_value
                try:
                    id = DB.ElementId(int(bad_value))
                    good_value = good_para.Set(id)
                except:
                    good_value = good_para.SetValueString (bad_value)
                continue

            if bad_para.StorageType == DB.StorageType.ElementId:
                bad_value = bad_para.AsElementId()
                good_value = good_para.Set(bad_value)
                continue

        return new_good_type
# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(*self.kwargs)
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"

class DropDownItem():
    def __init__(self, item):
        if isinstance(item, str):
            self.item = item
            self.display_text = item
            return

        self.item = item
        self.display_text = item.LookupParameter("Type Name").AsString()


# A simple WPF form used to call the ExternalEvent
class MergeFamily_UI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.merge_action_event_handler = SimpleEventHandler(merge_action)
        #self.clock_event_handler = SimpleEventHandler(clock_work)
        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.merge_action_event_handler)
        #self.ext_event_clock = ExternalEvent.Create(self.clock_event_handler)
        #print "preaction done"
        #print self.merge_action_event_handler
        #print self.merge_action_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'MergeFamily_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)
        
        
        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.Height = 800
        self.family_bad = None
        self.family_target = None



        instruction_text = "How to use Family Merger?"
        instruction_text += "\n\nStep 1: Pick two families for the source, you can use same family."
        instruction_text += "\n\nStep 2: Pick types to merge from dropdown list. You can use zoom to see a sample instance of the element. You can also just create a new type in the good family based on bad type data."
        instruction_text += "\n\nStep 3: Click merge to merge. There is also a built in check, if the two types have different type data, or the instance have different parameter structure, you will have to option to pause merge or force merge."
        instruction_text += "\n\nStep 4: All the instance parameter data is recorded as much as it can, then the type will be swapped, and instance parameter reapplied."
        instruction_text += "\n\nStep 5: Repeat."
        self.instruction_textblock.Text = instruction_text
        self.Show()


    @property
    def bad_type(self):
        if not self.type_list_bad.SelectedItem:
            return None
        return doc.GetElement(self.type_list_bad.SelectedItem.item.Id)



    @property
    def target_type(self):
        if not self.type_list_target.SelectedItem:
            return None
        if isinstance(self.type_list_target.SelectedItem.item, str):
            return self.type_list_target.SelectedItem.item
        return doc.GetElement(self.type_list_target.SelectedItem.item.Id)

    @property
    def is_current_view_only(self):
        return self.checkbox_current_view_only.IsChecked

    def is_type_safe_to_merge(self):
        bad_type = self.bad_type
        target_type = self.target_type
        if isinstance(target_type, str):
            return True
        self.mismatch_detail = ""
        if not target_type:
            return
        if not bad_type:
            return
        """
        should add check for instance level so if the instance parameter are different, it should also warn might not be safe to merge
        """
        #print bad_type
        #print target_type
        bad_type_paras = bad_type.Parameters
        target_type_paras = target_type.Parameters

        def get_para_by_name(type_or_instance, name):
            for para in type_or_instance.Parameters:
                if para.Definition.Name == name:
                    return para
            return None

        def is_detail_checked(para_name, bad_value, good_value):
            if bad_value == good_value:
                return True
            #print "Type Value Difference between bad type and target type: <{}>: {} VS {}".format(para_name, bad_value, good_value)
            note = "\n\nType A: Type Value <{}> = {}".format(para_name, bad_value)
            note += "\nType B: Type Value <{}> = {}".format(para_name,  good_value)
            print (note)
            self.mismatch_detail += note
            return False


        found_mismatch = False
        for bad_para in bad_type_paras:
            para_name = bad_para.Definition.Name
            if para_name in ["Family Name", "Edited by", "Workset"]:
                continue
            good_para = get_para_by_name(target_type, para_name)
            if not good_para:
                continue

            if bad_para.StorageType == DB.StorageType.Integer:
                bad_value = bad_para.AsInteger()
                good_value = good_para.AsInteger()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue

            if bad_para.StorageType == DB.StorageType.Double:
                bad_value = bad_para.AsDouble()
                good_value = good_para.AsDouble()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue

            if bad_para.StorageType == DB.StorageType.String:
                bad_value = bad_para.AsString()
                good_value = good_para.AsString()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue

            if bad_para.StorageType == DB.StorageType.ElementId:
                bad_value = bad_para.AsElementId()
                good_value = good_para.AsElementId()
                if not is_detail_checked(para_name, bad_value, good_value):
                    found_mismatch = True
                continue


        sample_instances_bad = get_all_instance_of_type(bad_type, self.is_current_view_only)
        sample_instances_target = get_all_instance_of_type(target_type, self.is_current_view_only)
        if len(sample_instances_bad) * len(sample_instances_target) != 0:
            sample_instance_bad = sample_instances_bad[0]
            sample_instance_target = sample_instances_target[0]
            for instance_para in sample_instance_bad.Parameters:
                para_name = instance_para.Definition.Name
                if not get_para_by_name(sample_instance_target, para_name):
                    note = "\n\nType A: Instance Parameter <{}>".format(para_name)
                    note += "\nType B: Cannot find a matching instance parameter."
                    print(note)
                    self.mismatch_detail += note
                    found_mismatch = True

        if found_mismatch:
            print("Please beaware there are mismatch of type parameter between <{}>:{} and <{}>:{}".format(bad_type.Family.Name,
                                                                                                        bad_type.LookupParameter("Type Name").AsString(),
                                                                                                        target_type.Family.Name,
                                                                                                        target_type.LookupParameter("Type Name").AsString()))
            return False
        return True


    @ERROR_HANDLE.try_catch_error()
    def merge_clicked(self, sender, args):
        if not self.bad_type:
            return
        if not self.target_type:
            return

        if not self.is_type_safe_to_merge():
            note = "Type A = <{}>: {}\nType B = <{}>: {}\n{}".format(self.bad_type.Family.Name,
                                            self.bad_type.LookupParameter("Type Name").AsString(),
                                            self.target_type.Family.Name,
                                            self.target_type.LookupParameter("Type Name").AsString(),
                                            self.mismatch_detail)
            opts = [["Stop Merging for those two types.","Let me look at the detailed comparison."], ["Keep Merging.", "Ignore local difference, just use the tartget type data."]]
            res = REVIT_FORMS.dialogue(main_text = "There are type parameter data not matching between the two types you picked.",
                                                        sub_text = note,
                                                        options = opts)


            if res == opts[1][0]:
                pass
            else:
                return
        self.data = dict()


        self.merge_action_event_handler.kwargs = self,
        self.ext_event.Raise()







    def open_details_describtion(self, sender, args):
        main_text = "How to use Family Merger?"
        sub_text = "Step 1: Pick two families for the source, you can use same family."
        sub_text += "\nStep 2: Pick types to merge from dropdown list. You can use zoom to see a sample instance of the element. You can also just create a new type in the good family based on bad type data."
        sub_text += "\nStep 3: Click merge to merge. There is also a built in check, if the two types have different type data, or the instance have different parameter structure, you will have to option to pause merge or force merge."
        sub_text += "\nStep 4: All the instance parameter data is recorded as much as it can, then the type will be swapped, and instance parameter reapplied."
        sub_text += "\nStep 5: Repeat."
        REVIT_FORMS.notification(main_text = main_text,
                                                sub_text = sub_text,
                                                window_title = "EnneadTab",
                                                button_name = "Close",
                                                self_destruct = 60,
                                                window_width = 800,
                                                window_height = 800)


    def open_youtube(self, sender, args):
        """
        REVIT_FORMS.notification(main_text = "not recorded yet",
                                                sub_text = "blah blah blah",
                                                window_title = "EnneadTab",
                                                button_name = "Close",
                                                self_destruct = 15,
                                                window_width = 1200,
                                                window_height = 800)
        """
        script.open_url(r"https://youtu.be/xZhCxpuQKCs")

    def pick_type_target(self, sender, args):
        #print "pick target type"
        self.family_target = self.get_family(is_picking_bad_type = False)


    def pick_type_bad(self, sender, args):
        #print "pick bad type"
        self.family_bad = self.get_family(is_picking_bad_type = True)



    @ERROR_HANDLE.try_catch_error()
    def get_family(self, is_picking_bad_type):

        families = DB.FilteredElementCollector(doc).OfClass(DB.Family).WhereElementIsNotElementType().ToElements()
        families = sorted(families, key = lambda x: x.Name.lower())
        if is_picking_bad_type == False and self.family_bad is not None:
            families = filter(lambda x: x.FamilyCategoryId == self.family_bad.FamilyCategoryId, families)

        if is_picking_bad_type:
            family = forms.SelectFromList.show(families,
                                                multiselect = False,
                                                name_attr = 'Name',
                                                width = 1000,
                                                title = "Pick family that is BAAAAAAAAAAAAAAAAAAD",
                                                button_name = 'Select Bad Family')
            if not family:
                return
            self.family_bad = family
            self.family_name_bad.Text = family.Name
            self.type_list_bad.SelectedIndex = 0
        else:
            family = forms.SelectFromList.show(families,
                                                multiselect = False,
                                                name_attr = 'Name',
                                                width = 1000,
                                                title = "Pick family that is GOOOD",
                                                button_name = 'Select Good Family')
            if not family:
                return
            self.family_target = family
            self.family_name_target.Text = family.Name
            self.type_list_target.SelectedIndex = 0


        self.update_drop_down_selection_source()
        return family



    def get_types(self, family):
        if not family or not family.IsValidObject :
            return []
        if len(family.GetFamilySymbolIds ()) == 0:
            return []
        types = [doc.GetElement(x) for x in family.GetFamilySymbolIds ()]
        types = sorted(types, key = lambda x: x.LookupParameter("Type Name").AsString())
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "{}".format(self.LookupParameter("Type Name").AsString())
        types = [MyOption(x) for x in types]
        return types

    def update_drop_down_selection_source(self):

        #raw_subC_names = ["- Waiting Assignment -"] +  get_all_subC_names() + ["<Use Source File Name as SubC>"]
        # self.type_list_bad.ItemsSource = self.get_types(self.family_bad)
        # self.type_list_target.ItemsSource = self.get_types(self.family_target)
        selected_index = max(self.type_list_bad.SelectedIndex, 0)
        #print "%%%%%%%%%%"
        #print selected_index
        self.type_list_bad.ItemsSource = [DropDownItem(x) for x in self.get_types(self.family_bad)]
        self.type_list_bad.SelectedIndex = min(selected_index, len(self.type_list_bad.ItemsSource) - 1)
        #print self.type_list_bad.SelectedIndex
        #print "^^^^^^^"

        selected_index = max(self.type_list_target.SelectedIndex, 0)
        if len(self.get_types(self.family_target)) > 0:
            temp = [DropDownItem(x) for x in self.get_types(self.family_target)]
            temp.append(DropDownItem("<Create Type from Bad Type>"))
        else:
            temp = []
        self.type_list_target.ItemsSource = temp
        self.type_list_target.SelectedIndex = min(selected_index, len(self.type_list_target.ItemsSource) - 1)


        return

  
    def dropdown_list_value_changed(self, sender, args):
        return
        #self.is_pass_convert_precheck()
        print(self.type_list_bad.ItemsSource)
        for x in self.type_list_bad.ItemsSource:
            print(x)
            print(x.item)
            print(x.display_text)

        print("###################################")
        if not self.type_list_target.ItemsSource:
            return
        print(self.type_list_target.ItemsSource)
        for x in self.type_list_target.ItemsSource:
            print(x)
            print(x.item)
            print(x.display_text)

    def zoom_target_click(self, sender, args):
        self.handle_zoom(is_bad_type = False)

    def zoom_bad_click(self, sender, args):
        self.handle_zoom(is_bad_type = True)

    @ERROR_HANDLE.try_catch_error()
    def handle_zoom(self, is_bad_type):
        try:
            if is_bad_type:
                type = self.bad_type
            else:
                type = self.target_type
        except Exception as e:
            print (e)
            return
        if not type:
            return

        instances = get_all_instance_of_type(type, self.is_current_view_only)
        if len(instances) == 0:
            NOTIFICATION.messenger(main_text = "Found no elements of this type.", force_toast = True)
            return
        random.shuffle(instances)
        instance = instances[0]
        uidoc.ShowElements(instance)
        uidoc.Selection.SetElementIds(DATA_CONVERSION.list_to_system_list([instance.Id]))


    def handleclick(self, sender, args):
        print ("surface clicked")

    def close_click(self, sender, args):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()



@ERROR_HANDLE.try_catch_error()
def main():
    modeless_form = MergeFamily_UI()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    
    main()
   
