#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that allow you to transfer view templates, object styles (SubCategory) and materials.\n\nThe main difference between this and the default 'Transfer Project Standard', is that this tool allow you to be selective on what to bring."
__title__ = "Content\nTransfer"
__tip__ = True

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import ENVIRONMENT, NOTIFICATION, DATA_CONVERSION, ERROR_HANDLE
import traceback
from Autodesk.Revit import DB # pyright: ignore 

from Autodesk.Revit import UI # pyright: ignore

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True



class CopyUseDestination(DB.IDuplicateTypeNamesHandler):
    """Handle copy and paste errors."""
    def __init__(self, is_strict=True):
        self.is_strict = is_strict
        pass

    def OnDuplicateTypeNamesFound(self, args):  #pylint: disable=unused-argument
        """Use destination model types if duplicate."""
        if self.is_strict:
            elements = [args.Document.GetElement(x) for x in args.GetTypeIds()]
            print("{} has duplicate name in [{}].".format([x.Name for x in elements], args.Document.Title))
            return DB.DuplicateTypeAction.Abort
        else:
            return DB.DuplicateTypeAction.UseDestinationTypes


#############universal transfer between files by id
@ERROR_HANDLE.try_catch_error()
def copy_elements(element_ids, src_doc, dest_doc, is_strict):
    cp_options = DB.CopyPasteOptions()
    cp_options.SetDuplicateTypeNamesHandler(CopyUseDestination(is_strict = is_strict))

    success = []
    failed = []
    for id in element_ids:
        try:
            new_item_id = DB.ElementTransformUtils.CopyElements(src_doc,
                                                    DATA_CONVERSION.list_to_system_list([id]),
                                                    dest_doc, None, cp_options)
            success.append(new_item_id)
        except Exception as e:
            #print (e)
            failed.append(id)

    return success, failed # in list.    if success, return new id, if failed, return original id

    




@ERROR_HANDLE.try_catch_error()
def transfer_templates(templates, src_doc, dest_docs, use_prefix):

        
    T = DB.Transaction(src_doc, "temp")
    T.Start()
    if use_prefix:
        for template in templates:
            template.Name += "_Transfered from doc_{}".format(src_doc.Title)
    template_ids = [x.Id for x in templates]

    for dest_doc in dest_docs:
        if dest_doc.Title == src_doc.Title:
            continue

        t = DB.Transaction(dest_doc, "Transfer In Template")
        t.Start()
        copy_elements(template_ids, src_doc, dest_doc, is_strict = not use_prefix)
        t.Commit()

    T.RollBack()
    NOTIFICATION.messenger(main_text = "Transfer template finished.")


def get_elevation_marker(doc, elevation_view):
    all_markers = DB.FilteredElementCollector(doc).OfClass(DB.ElevationMarker ).ToElements()
    for marker in all_markers:
        if marker.GetViewId() == elevation_view.Id.IntegerValue:
            return marker

@ERROR_HANDLE.try_catch_error()
def transfer_views(views, src_doc, dest_docs):

        
    T = DB.Transaction(src_doc, "temp")
    T.Start()
 
    section_view_ids = [x.Id for x in views if x.ViewType == DB.ViewType.Section]
    elevation_views = [x for x in views if x.ViewType == DB.ViewType.Elevation]
    

    for dest_doc in dest_docs:
        if dest_doc.Title == src_doc.Title:
            continue

        t = DB.Transaction(dest_doc, "Transfer In SectionView")
        t.Start()
        copy_elements(section_view_ids, src_doc, dest_doc, is_strict = True)
        t.Commit()

        t = DB.Transaction(dest_doc, "Transfer In ElevationView")
        t.Start()
        for elevation_view in elevation_views:
            marker = get_elevation_marker(src_doc, elevation_view)
            success, failed = copy_elements([marker.Id], src_doc, dest_doc, is_strict = True)
            print(success, failed)

        t.Commit()


    T.RollBack()
    NOTIFICATION.messenger(main_text = "Transfer views finished.")


    





@ERROR_HANDLE.try_catch_error()
def transfer_OSTs(subCs, src_doc, dest_docs, update_OST_definition):

        
    T = DB.Transaction(src_doc, "temp")
    T.Start()

    subC_ids = [x.Id for x in subCs]

    for dest_doc in dest_docs:
        if dest_doc.Title == src_doc.Title:
            continue
        

        # if update_OST_definition:
        #     all_dest_subcs = []
        #     for x in dest_doc.Settings.Categories:
        #         all_dest_subcs.extend(list(x.SubCategories))
        #     all_dest_subc_names = [x.Name for x in all_dest_subcs]

        #     overlap_subc_names = [subC.Name for subC in subCs if subC.Name in all_dest_subc_names]
            

        t = DB.Transaction(dest_doc, "Transfer In Object Style")
        t.Start()
        _, failed_ids = copy_elements(subC_ids, src_doc, dest_doc, is_strict = True)

        if update_OST_definition:
            overlap_names = [src_doc.GetElement(x).Name for x in failed_ids if src_doc.GetElement(x)]
            for name in overlap_names:
                src_subc = REVIT_SELECTION.get_subc(src_doc, name)
                dest_subc = REVIT_SELECTION.get_subc(dest_doc, name)
                match_OST_definition(src_subc, dest_subc)

        t.Commit()

    T.RollBack()
    NOTIFICATION.messenger(main_text = "Transfer object style finished.")


def match_OST_definition(src_subc, dest_subc):
    # match OST definition

    attr_list = ["LineWeight"] #"LinePatternId", 
    for attr in attr_list:
        for style_type in [DB.GraphicsStyleType.Projection, DB.GraphicsStyleType.Cut]:
            src_method = getattr(src_subc, "Get" + attr)
            value = src_method(style_type)

            dest_method = getattr(dest_subc, "Set" + attr)
            dest_method(value, style_type)

    
    attr_list = ["LineColor", "Material"]
    for attr in attr_list:
        value = getattr(src_subc,  attr)
        setattr(dest_subc, attr, value)
   




def get_material_by_name(doc, name):
    materials = DB.FilteredElementCollector(doc).OfClass(DB.Material).WhereElementIsNotElementType().ToElements()
    material = filter(lambda x: x.Name == name, materials)
    if len(material) == 0:
        return None
    else:
        return material[0]

@ERROR_HANDLE.try_catch_error()
def transfer_materials(materials, src_doc, dest_docs, preserve_keynote):

        
    T = DB.Transaction(src_doc, "temp")
    T.Start()

    material_ids = [x.Id for x in materials]

    for dest_doc in dest_docs:
        if dest_doc.Title == src_doc.Title:
            continue
        
        if preserve_keynote:
            keynote_map = dict()
            for material in materials:
                record_mat = get_material_by_name(dest_doc, material.Name)
                if record_mat is  None:
                    continue
                keynote_map[material.Name] = record_mat.LookupParameter("Keynote").AsString()
                 
        t = DB.Transaction(dest_doc, "Transfer In Material")
        t.Start()
        new_mat_ids, _ = copy_elements(material_ids, src_doc, dest_doc, is_strict = False)


        if preserve_keynote and new_mat_ids is not None:
            # flatten the list first
            new_mat_ids = [x[0] for x in new_mat_ids]
            
            for mat in [dest_doc.GetElement(x) for x in new_mat_ids]:
                if mat.Name not in keynote_map:
                    continue
                mat.LookupParameter("Keynote").Set(keynote_map[mat.Name])


        t.Commit()

    T.RollBack()
    
    NOTIFICATION.messenger(main_text = "Transfer material finished.")


@ERROR_HANDLE.try_catch_error()
def transfer_family(families, src_doc, dest_docs, shared_using_project):
    LOG = ""
    for family in families:
        LOG += "\n-- Transfering [{}]".format(family.Name)
        family_doc = src_doc.EditFamily(family)

        for doc in dest_docs:
            family_doc.LoadFamily(doc, FamilyOption(shared_using_project))

        family_doc.Close(False)

        
    print(LOG)
    print("\n\nDone!")
    NOTIFICATION.messenger(main_text = "Transfer family finished.")
    

class FamilyOption(DB.IFamilyLoadOptions):
    def __init__(self, shared_using_project):
        self.shared_using_project = shared_using_project


    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues = True
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):

        overwriteParameterValues = True

        if self.shared_using_project:
            source = DB.FamilySource.Project
        else:
            source = DB.FamilySource.Family
        return True

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


class MyOptionPickDoc(forms.TemplateListItem):
    @property
    def name(self):
        note = "[Revit Link]:" if self.item.IsLinked else ""
        note += "[Family]:" if self.item.IsFamilyDocument else ""
        return "{}{}".format(note, self.item.Title)


# A simple WPF form used to call the ExternalEvent
class content_transfer_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        self.transfer_templates_event_handler = SimpleEventHandler(transfer_templates)
        self.ext_event_transfer_templates = ExternalEvent.Create(self.transfer_templates_event_handler)

        self.transfer_OST_event_handler = SimpleEventHandler(transfer_OSTs)
        self.ext_event_transfer_OST = ExternalEvent.Create(self.transfer_OST_event_handler)

        self.transfer_material_event_handler = SimpleEventHandler(transfer_materials)
        self.ext_event_transfer_material = ExternalEvent.Create(self.transfer_material_event_handler)



        self.transfer_view_event_handler = SimpleEventHandler(transfer_views)
        self.ext_event_transfer_view = ExternalEvent.Create(self.transfer_view_event_handler)
        

        
        self.transfer_family_event_handler = SimpleEventHandler(transfer_family)
        self.ext_event_transfer_family= ExternalEvent.Create(self.transfer_family_event_handler)

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "content_transfer_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Selective Transfer"

        self.sub_text.Text = __doc__


        self.Title = self.title_text.Text

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)


        self.source_doc = None
        self.target_docs  = None
        self.selected_templates  = None
        self.selected_categories = None
        self.selected_materials = None
        self.selected_views = None
        self.selected_family_docs = None

        self.Show()



    @ERROR_HANDLE.try_catch_error()
    def pick_source_doc_click(self, sender, e):
        """self doc + opened docs + links docs"""
        all_top_docs = REVIT_APPLICATION.get_top_revit_docs()
        all_links_docs = REVIT_APPLICATION.get_revit_link_docs(link_only = True)
        all_family_docs = REVIT_APPLICATION.get_all_family_docs(including_current_doc = True)


        
        self.source_doc = forms.SelectFromList.show([MyOptionPickDoc(x) for x in all_top_docs + all_links_docs + all_family_docs],
                                                    title = "Pick a source document",
                                                    multiselect = False)

        if self.source_doc:
            additional_note = "[Revit Link] " if self.source_doc.IsLinked else ""
            self.textblock_source_display.Text = "Source Document:\n" + additional_note + self.source_doc.Title


        self.varify_UI()


    @ERROR_HANDLE.try_catch_error()
    def pick_target_docs_click(self, sender, e):
        """self doc + opened doc """
        all_top_docs = REVIT_APPLICATION.get_top_revit_docs()
        all_family_docs = REVIT_APPLICATION.get_all_family_docs(including_current_doc = True)
        self.target_docs = forms.SelectFromList.show([MyOptionPickDoc(x) for x in all_top_docs + all_family_docs],
                                                    title = "Pick a target document",
                                                    multiselect = True)

        if self.target_docs:
            names = "\n".join([x.Title for x in self.target_docs])
            self.textblock_target_display.Text = "Target Documents:\n" + names

        self.varify_UI()


    @ERROR_HANDLE.try_catch_error()
    def pick_template_click(self, sender, e):
        if not self.varify_UI():
            return

        self.selected_templates = forms.select_viewtemplates(title='Select View Templates', 
                                             
                                            doc=self.source_doc)
        if not self.selected_templates:
            self.textbox_template_name.Text = "No Templates Picked."
            return
        note = "Templates Picked:\n"
        self.textbox_template_name.Text = note +"\n".join([x.Name for x in self.selected_templates])


    @ERROR_HANDLE.try_catch_error()
    def transfer_template_click(self, sender, e):
        if not self.varify_UI():
            return

        if not self.selected_templates:
            self.textbox_template_name.Text = "No Templates Picked."
            return

        self.transfer_templates_event_handler.kwargs = self.selected_templates, self.source_doc,self.target_docs, self.radio_bt_template_prefix.IsChecked
        self.ext_event_transfer_templates.Raise()


    @ERROR_HANDLE.try_catch_error()
    def pick_OST_click(self, sender, e):
        if not self.varify_UI():
            return


        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}]{}".format(self.item.Parent.Name, self.item.Name)


        all_categories = [x for x in self.source_doc.Settings.Categories if ".dwg" not in x.Name.lower()]
        all_subcategories = []
        for category in all_categories:
            all_subcategories += [MyOption(x) for x in category.SubCategories]



        all_categories.sort(key = lambda x: x.Name)
        self.selected_categories = forms.SelectFromList.show(all_subcategories,
                                                multiselect = True,
                                                name_attr = "Name",
                                                title = "Pick ObjectStyle that you want to process.",
                                                button_name = 'Select ObjectStyle to Transfer')
        if not self.selected_categories:
            self.textbox_OST_name.Text = "No ObjectStyle Picked."
            return
        note = "ObjectStyle Picked:\n"
        self.textbox_OST_name.Text = note +"\n".join(["[{}]{}".format(x.Parent.Name, x.Name) for x in self.selected_categories])


    @ERROR_HANDLE.try_catch_error()
    def transfer_OST_click(self, sender, e):
        if not self.varify_UI():
            return

        if not self.selected_categories:
            self.textbox_OST_name.Text = "No ObjectStyle Picked."
            return

        self.transfer_OST_event_handler.kwargs = self.selected_categories, self.source_doc,self.target_docs, self.checkbox_update_OST_definition.IsChecked
        self.ext_event_transfer_OST.Raise()















    @ERROR_HANDLE.try_catch_error()
    def pick_material_click(self, sender, e):
        if not self.varify_UI():
            return




        all_materials = list(DB.FilteredElementCollector(self.source_doc).OfClass(DB.Material).WhereElementIsNotElementType().ToElements())
      
        all_materials.sort(key = lambda x: x.Name)
        self.selected_materials = forms.SelectFromList.show(all_materials,
                                                multiselect = True,
                                                name_attr = "Name",
                                                title = "Pick Materials that you want to process.",
                                                button_name = 'Select Materials to Transfer')
        if not self.selected_materials:
            self.textbox_material_name.Text = "No Materials Picked."
            return
        note = "Materials Picked:\n"
        self.textbox_material_name.Text = note +"\n".join(x.Name for x in self.selected_materials)


    @ERROR_HANDLE.try_catch_error()
    def transfer_material_click(self, sender, e):
        if not self.varify_UI():
            return

        if not self.selected_materials:
            self.textbox_material_name.Text = "No Materials Picked."
            return

        self.transfer_material_event_handler.kwargs = self.selected_materials, self.source_doc,self.target_docs, self.checkbox_preserve_mat_keynote.IsChecked
        self.ext_event_transfer_material.Raise()














    @ERROR_HANDLE.try_catch_error()
    def pick_view_click(self, sender, e):
        if not self.varify_UI():
            return




        all_views = list(DB.FilteredElementCollector(self.source_doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements())
        #all_views = filter(lambda x: x.ViewType in [DB.ViewType.Section, DB.ViewType.Elevation], all_views)
        all_views = filter(lambda x: x.ViewType in [DB.ViewType.Section], all_views)


        all_views.sort(key = lambda x: x.Name)
        self.selected_views = forms.SelectFromList.show(all_views,
                                                multiselect = True,
                                                name_attr = "Name",
                                                title = "Picking sections.",
                                                button_name = 'Select Views to Transfer')
        if not self.selected_views:
            self.textbox_views_name.Text = "No Views Picked."
            return
        note = "Views Picked:\n"
        self.textbox_views_name.Text = note +"\n".join(x.Name for x in self.selected_views)


    @ERROR_HANDLE.try_catch_error()
    def transfer_view_click(self, sender, e):
        if not self.varify_UI():
            return

        if not self.selected_views:
            self.textbox_views_name.Text = "No Views Picked."
            return

        self.transfer_view_event_handler.kwargs = self.selected_views, self.source_doc,self.target_docs
        self.ext_event_transfer_view.Raise()









    @ERROR_HANDLE.try_catch_error()
    def pick_family_click(self, sender, e):
        if not self.varify_UI():
            return


        #docs = REVIT_APPLICATION.get_application().Documents
        #family_docs = [doc for doc in docs if doc.IsFamilyDocument]
        all_families = DB.FilteredElementCollector(self.source_doc).OfClass(DB.Family).ToElements()
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                try:
                    return "[{}]{}".format(self.item.FamilyCategory.Name, self.item.Name)
                except:
                    
                    return "{}".format(self.item.Name)

        all_families = [MyOption(x) for x in all_families if x.IsUserCreated ]
        all_families.sort(key = lambda x: x.Name)



        self.selected_family_docs = forms.SelectFromList.show(all_families,
                                                            multiselect = True,
                                                            title = "pick families to load",
                                                            button_name='pick family')




        if not self.selected_family_docs:
            self.textbox_family_name.Text = "No Families Picked."
            return
        note = "Families Picked:\n"
        self.textbox_family_name.Text = note +"\n".join(x.Name for x in self.selected_family_docs)


    @ERROR_HANDLE.try_catch_error()
    def transfer_family_click(self, sender, e):
        if not self.varify_UI():
            return

        if not self.selected_family_docs:
            self.textbox_family_name.Text = "No Families Picked."
            return

        self.transfer_family_event_handler.kwargs = self.selected_family_docs, self.source_doc,self.target_docs, self.radio_bt_shared_use_project.IsChecked
        self.ext_event_transfer_family.Raise()







    def varify_UI(self):
        if not self.source_doc:
            self.textblock_source_display.Text = "No Source Document Selected."
            return False
        if not self.target_docs:
            self.textblock_target_display.Text = "No Target Documents Selected."
            return False
        return True


    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()






################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:
        modeless_form = content_transfer_ModelessForm()
        
    except:
        print (traceback.format_exc())
