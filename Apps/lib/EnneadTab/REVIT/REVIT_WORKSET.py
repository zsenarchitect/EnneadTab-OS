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
TO-DO migrate this to new way of doing things and make startup.py point to this"""

try:
    from pyrevit import DB, revit
except:
    pass

def get_id_card(element):
    try:
        id_card = "[{}]:[{}]".format(element.Symbol.FamilyName, element.Symbol.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString())
    except:
        id_card = "'{}''".format(element.Id)
    return id_card

def get_element_workset(element):
    return revit.doc.GetWorksetTable().GetWorkset(element.WorksetId)

def set_element_workset(element,workset):
    #print element.GetParameters("Workset")[0]
    try:
        para = element.GetParameters("Workset")[0]
        #print para
        para.Set(workset.Id.IntegerValue)
        """
        para = element.Parameter[DB.BuiltInParameter.ELEM_PARTITION_PARAM]
        para.Set(workset)
        """
        return "OK"
    except:
        print( "\n\n--------------  set workset failed  -------------")
        id_card = get_id_card(element)
        ########print element.Symbol.GetPreviewImage(Drawing.Size(200,200))
        #if hasattr(obj, 'attr_name')
        #if isinstance(5, int)


        if element.GroupId != -1: #-1 means not in group
            try:
                group_name = revit.doc.GetElement(element.GroupId).Name
                print ("\nFail to set workset for {0} becasue it is in group '{3}'---> {1}--->{2}".format(id_card,script.get_output().linkify(element.Id, title = "Go To Element"),script.get_output().linkify(element.GroupId, title = "Go To Group"), group_name))
                print ("This group is currently in workset '{}'".format(get_element_workset(revit.doc.GetElement(element.GroupId)).Name))
            except:
                group_name = "None"



            try:
                #if revit.doc.GetElement(element.GroupId).DesignOption:
                print ("The group '{}' is in design option '{}'. You may use 'Go To Group' while that design option is in edit mode.\n\n ".format(group_name, revit.doc.GetElement(element.GroupId).DesignOption.Name))
                return "Group In DesignOption"
            except:#no attribute designoption, just say it is in a group
                return "In Group"
            finally:
                #print ("test" + str(revit.doc.GetElement(element.GroupId).DesignOption))
                pass

        elif element.DesignOption != -1:#-1 means not in design option
            print ("The element is in design option '{}'. You may use 'Go To Element' while that design option is in edit mode.\n\n ".format(element.DesignOption.Name))
            return "Element In DesignOption"

        else:
            print ("Fail to set workset on {0} ---> {1}".format(id_card,script.get_output().linkify(element.Id, title = "Go To Element")))
            return "Unknown"

        print ("Contact SenZhang")

def get_all_userworkset():
    all_worksets = []
    all_worksets_raw = DB.FilteredWorksetCollector(revit.doc).ToWorksets()
    for workset in all_worksets_raw:
        if workset.Kind.ToString() == "UserWorkset":
            all_worksets.append(workset)
    return all_worksets

def get_workset_by_name(name):
    for workset in get_all_userworkset():
        if workset.Name == name:
            return workset

def get_all_userworkset_name():
    all_workset_names = []
    all_worksets_raw = DB.FilteredWorksetCollector(revit.doc).ToWorksets()
    for workset in all_worksets_raw:
        if workset.Kind.ToString() == "UserWorkset":
            all_workset_names.append(workset.Name)
    all_workset_names.sort(reverse = False)
    return all_workset_names
