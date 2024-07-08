"""

                                                                                                                                                                   
                                                                                                                                                                   
                          tttt               tttt                                                         tttt            iiii                                     
                       ttt:::t            ttt:::t                                                      ttt:::t           i::::i                                    
                       t:::::t            t:::::t                                                      t:::::t            iiii                                     
                       t:::::t            t:::::t                                                      t:::::t                                                     
  aaaaaaaaaaaaa  ttttttt:::::tttttttttttttt:::::ttttttt        eeeeeeeeeeee    nnnn  nnnnnnnn    ttttttt:::::ttttttt    iiiiiii    ooooooooooo   nnnn  nnnnnnnn    
  a::::::::::::a t:::::::::::::::::tt:::::::::::::::::t      ee::::::::::::ee  n:::nn::::::::nn  t:::::::::::::::::t    i:::::i  oo:::::::::::oo n:::nn::::::::nn  
  aaaaaaaaa:::::at:::::::::::::::::tt:::::::::::::::::t     e::::::eeeee:::::een::::::::::::::nn t:::::::::::::::::t     i::::i o:::::::::::::::on::::::::::::::nn 
           a::::atttttt:::::::tttttttttttt:::::::tttttt    e::::::e     e:::::enn:::::::::::::::ntttttt:::::::tttttt     i::::i o:::::ooooo:::::onn:::::::::::::::n
    aaaaaaa:::::a      t:::::t            t:::::t          e:::::::eeeee::::::e  n:::::nnnn:::::n      t:::::t           i::::i o::::o     o::::o  n:::::nnnn:::::n
  aa::::::::::::a      t:::::t            t:::::t          e:::::::::::::::::e   n::::n    n::::n      t:::::t           i::::i o::::o     o::::o  n::::n    n::::n
 a::::aaaa::::::a      t:::::t            t:::::t          e::::::eeeeeeeeeee    n::::n    n::::n      t:::::t           i::::i o::::o     o::::o  n::::n    n::::n
a::::a    a:::::a      t:::::t    tttttt  t:::::t    tttttte:::::::e             n::::n    n::::n      t:::::t    tttttt i::::i o::::o     o::::o  n::::n    n::::n
a::::a    a:::::a      t::::::tttt:::::t  t::::::tttt:::::te::::::::e            n::::n    n::::n      t::::::tttt:::::ti::::::io:::::ooooo:::::o  n::::n    n::::n
a:::::aaaa::::::a      tt::::::::::::::t  tt::::::::::::::t e::::::::eeeeeeee    n::::n    n::::n      tt::::::::::::::ti::::::io:::::::::::::::o  n::::n    n::::n
 a::::::::::aa:::a       tt:::::::::::tt    tt:::::::::::tt  ee:::::::::::::e    n::::n    n::::n        tt:::::::::::tti::::::i oo:::::::::::oo   n::::n    n::::n
  aaaaaaaaaa  aaaa         ttttttttttt        ttttttttttt      eeeeeeeeeeeeee    nnnnnn    nnnnnn          ttttttttttt  iiiiiiii   ooooooooooo     nnnnnn    nnnnnn
                                                                                                                                                                   
                                                                                                                                                                   
                                                                                                                                                                   
                                                                                                                                                                   
                                                                                                                                                                   
                                                                                                                                                                   
                                                                                                                                                                   

THIS is direct copy from old MARK_HISTORY script with NO modification, it will faill for sure. 2023-12-07
To-Do migrate this to new way of doing things and make startup.py point to this"""

try:
    from Autodesk.Revit import DB # pyright: ignore
except:
    pass

try:
    import REVIT_FORMS
except:
    pass


def get_dwgs(doc):
    dwgs_list = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).WhereElementIsNotElementType().ToElements()
    if len(dwgs_list) != 0:
        list(dwgs_list).sort(key = lambda x: x.LookupParameter("Name"), reverse = True)
    return dwgs_list





def output_info(elements,doc,output):
    for el in elements:
        try:
            output.print_md("DWG Id = {}".format(el.Id))
        except:
            print ("DWG Id = {}".format(el.Id))

        dwg_name = el.LookupParameter("Name").AsString()
        workset = doc.GetWorksetTable().GetWorkset(el.WorksetId).Name
        try:
            output.print_md ("- DWG name = {}".format(dwg_name))
        except:
            continue

        if el.ViewSpecific:
            view_id = el.OwnerViewId
            try:#revit 2020 and 2019 use diffrent propety for names
                view_name = doc.GetElement(view_id).ViewName
            except AttributeError:
                view_name = doc.GetElement(view_id).Name

            output.print_md ("- It is view specific 2D dwg in view '{}'".format(view_name))

            if el.IsHidden(doc.GetElement(view_id)):
                output.print_md ("- It is currently hidden in the view.")
        else:
            output.print_md ("- It is 3D dwg. ")
            output.print_md ("- Workset = {}".format(workset))

def show_CAD_history(dwgs):
    doc = dwgs[0].Document
   
    title = "Total {} **imported** DWGs found. Please replace imported CAD with linked CAD.\nUse EnneadTab 'DWGs Manager' tool to locate them.".format(len(dwgs))
    sub_title = ""
    for dwg in dwgs:

        element_history = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, dwg.Id)
        element_note_basic = "\n\ndwg name:'{3}'\n\tImported by: {0}\n\tCurrent Owner: {1}\n\tLast Changed By: {2}".format(element_history.Creator,
                                                                                                                           element_history.Owner,
                                                                                                                           element_history.LastChangedBy ,
                                                                                                                           dwg.LookupParameter("Name").AsString())

        if dwg.ViewSpecific:
            view_id = dwg.OwnerViewId
            try:#revit 2020 and 2019 use diffrent propety for names
                view_name = doc.GetElement(view_id).ViewName
            except AttributeError:
                view_name = doc.GetElement(view_id).Name

            additional_note = ("\n\tIt is view specific 2D dwg in view '{}'".format(view_name))

            if dwg.IsHidden(doc.GetElement(view_id)):
                additional_note += "\tIt is currently hidden in the view."
        else:
            additional_note = "\n\tIt is 3D dwg."
            workset = doc.GetWorksetTable().GetWorkset(dwg.WorksetId).Name
            additional_note += " Workset = {}".format(workset)


        element_note = element_note_basic + additional_note
        sub_title += element_note

    REVIT_FORMS.dialogue(main_text = title, sub_text = sub_title, icon = "warning")


def get_import_CAD(doc, output):
    all_dwgs = get_dwgs(doc)

    dwgs_imported = [dwg for dwg in all_dwgs if not dwg.IsLinked]


    if len(dwgs_imported) == 0:
        return False
    
    
    output_info(dwgs_imported,doc,output)

    output.print_md("# Summary")
    output.print_md("Total {} **imported** DWGs found.".format(len(dwgs_imported)))
    if len(dwgs_imported)>5:
        print ("Too many imported DWGs.")
    print ("If possible, use as little as possible imported DWGs.")
    if doc.IsWorkshared:
        show_CAD_history(dwgs_imported)
        
    return True
