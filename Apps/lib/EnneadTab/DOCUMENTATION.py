
import os
import random
import imp
import traceback


import ENVIRONMENT
import FOLDER
import USER
import OUTPUT

TIP_KEY = "__tip__"
SCOTT_TIPS = ["https://ei.ennead.com/post/3046/revit-legends-legend-components",
              "https://ei.ennead.com/post/2777/revit-short-subject-purge-cad-before-linking-into-revit",
              "https://ei.ennead.com/post/3007/don-t-use-groups-as-single-entities",
              "https://ei.ennead.com/post/2981/keeping-enough-c--drive-free-space",
              "https://ei.ennead.com/post/2824/revit-short-subject-acc-bim-360-requirements",
              "https://ei.ennead.com/post/2673/revit-short-subject-worksharing-etiquette",
              "https://ei.ennead.com/post/31/revit-short-subject-design-options",
              "https://ei.ennead.com/post/19/revit-short-subject-keyboard-shortcuts",
              "https://ei.ennead.com/post/47/revit-short-subject-3d-view-navigation",
              "https://ei.ennead.com/post/64/revit-short-subject-don-t-manually-hide-elements",
              "https://ei.ennead.com/post/75/revit-short-subject-limit-use-of-groups",
              "https://ei.ennead.com/post/99/revit-short-subject-the-cad-query-tool",
              "https://ei.ennead.com/post/114/revit-short-subject-best-practice-for-new-views"]

def show_scott_tip():
    if ENVIRONMENT.is_Revit_environment():
        from pyrevit import script
        output = script.get_output()
        output.print_image("L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Misc\\scott_but_younger.png")
    else:
        output = OUTPUT.Output()
    tip = random.choice(SCOTT_TIPS)
    import webbrowser
    webbrowser.open(tip)
    output.print_md ("#Scott's Tip of the day:\n{}".format(tip))

    embed_html = """<!DOCTYPE html>
<html>
<head>
    <title>Embedding a Webpage</title>
</head>
<body>
    <h1>...............................................</h1>
    
    <!-- Use an iframe to embed the webpage -->
    <iframe src={} width="1200" height="900" frameborder="0"></iframe>
    
    <p>Enjoy!</p>
</body>
</html>""".format(tip)
    # output.print_html(embed_html)
    OUTPUT.display_output_on_browser()
    

def get_files_with_keyword(keyword, folder):
    max_open = 10
    opened = 0
    matching_files = []
    for root, dirs, files in os.walk(folder):
        
        
        
        if "Ennead Tailor.tab" in root:
            continue
        
        if "lib" in root:
            # ignore core modules
            continue
        
        if "archive" in root:
            continue
        
        if "Utility.panel" in root:
            continue
        
        if "MakeFloatingBox" in root:
            continue
        
        for file in files:
            if "DOCUMENTATION" in file:
                # ignore this file that is searching other files
                continue
            if "template" in file:
                continue
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # # tester
                # if "Merge_Family_UI" in file_path:
                #     return file_path
                
                
                with open(file_path, 'r') as f:
                    contents = f.read()
                    if "Sen Zhang has not writed documentation for this tool, but he should!" in contents:
                        continue
                    
                    if "__main__" not in contents:
                        # this is to skip file that can actually run the whole thing during import. This is bad. shoud report back to SEn to fix
                        if USER.is_SZ():
                            print ("\n\nThis contain dangerous format that can run during import:\n" + file_path + "\nYou can add this...")
                            print ("""if __name__ == "__main__":
    pass""")
                            if opened < max_open:
                                opened += 1
                                os.startfile(file_path)
                        continue
                    
                    if keyword in contents:
                        #print "Found keyword '%s' in file: %s" % (keyword, file_path)
                        matching_files.append(file_path)

    return matching_files
    if len(matching_files) > 0:
        # print "Totally {} file with bad documentation".format(len(matching_files))
        random_files = random.sample(matching_files, min(output_count, len(matching_files)))
        # print "Opening randomly selected files:"
        return random_files
        for file in random_files:
            return file
    else:
        # print "No files found containing keyword '%s'" % keyword
        pass

def get_title_tip_from_folder(folder, is_random_single = True):
    """_summary_

    Args:
        folder (_type_): _description_
        is_random_single (bool, optional): _description_. Defaults to True.

    Returns:
        list of (title,tip) tutple
    """
    
    matching_files = get_files_with_keyword(TIP_KEY, folder)
    
    if is_random_single:

        return [get_title_tip_from_file(random.choice(matching_files), is_random_single)]
    
    return [get_title_tip_from_file(x, is_random_single) for x in matching_files]

def get_icon_from_path(file_path):
    button_folder = os.path.dirname(file_path)
    for file in os.listdir(button_folder):
        if "icon.png" == file:
            return os.path.join(button_folder, file)
        
    for file in os.listdir(button_folder):
        if "icon" in file:
            return os.path.join(button_folder, file)
   
def get_title_tip_from_file(lucky_file, is_random_single):
    
    icon_path = get_icon_from_path(lucky_file)
        
    module_name = FOLDER.get_file_name_from_path(lucky_file).replace(".py", "")
    try:
        ref_module = imp.load_source(module_name, lucky_file)

    except Exception as e:
        if USER.is_SZ():
            print ("\n\nSZ visible only logging:")
            print (traceback.format_exc())
        return module_name, None, icon_path
    
    tip = getattr(ref_module,TIP_KEY)
    
    if isinstance(tip, list): #>>>>>>>if manually define many tips then use that, otherwise use __doc__, it shold not require double writing
        pass
    else:
        tip = [ref_module.__doc__]
        
    if is_random_single:
        tip = [random.choice(tip)]

        
    if hasattr(ref_module, "__title__"):
        title = ref_module.__title__.replace("\n", " ")
    else:
        title = module_name
    
    
    return title, tip, icon_path

def show_tip_revit(is_random_single=True):
    import REVIT
    import TEXT
    from pyrevit import script
    output = script.get_output()
    if not output:
        output = OUTPUT.Output()
    folder =  "{}\ENNEAD.extension".format(ENVIRONMENT.PUBLISH_BETA_FOLDER_FOR_REVIT)
    if os.path.exists(ENVIRONMENT.WORKING_FOLDER_FOR_REVIT):
        folder =  "{}\ENNEAD.extension".format(ENVIRONMENT.WORKING_FOLDER_FOR_REVIT)
   
    
    for title_titp_tuple in get_title_tip_from_folder(folder, is_random_single):
        title, tips, icon_path = title_titp_tuple
        if tips:
            print ("\n\n\n\n")
            if is_random_single:
                # output.print_md (TEXT.centered_text("#EnneadTab Tip of the day:"))
                output.print_md ("#EnneadTab Tip of the day:")
            if icon_path:
                # output.print_image(icon_path)
                output.print_html("<span style='text-align: center;'><img src=\"file:///{0}\"></span>".format(icon_path))
            # output.print_md(TEXT.centered_text("##Did you know in [{}]...".format(title)))
            # output.print_md (TEXT.centered_text("{}".format(tip)))
            output.print_md("##Did you know in [{}]...".format(title))
            
            for tip in tips:
                print ("\n\n")
                for line in tip.split("\n"):
                    output.print_md (line)

    print ("\n\n\n\n")
    output.print_md ("<span style='color:blue'>(Note)If you are not seeing this feature on your toolbar, you might be using the ***LITE*** version right now. See if you have a little icon of 'LITE' next to your Setting Gear Icon</span>")
    output.print_md ("<span style='color:blue'>Switch to ***Pro*** Version to unlock all the cool features!</span>")
    if is_random_single:
        OUTPUT.display_output_on_browser()

    
def show_tip_rhino():
    print("TO_DO: use tool lookup data")

def tip_of_day():
    if random.random() < 0.3:
        return
    if ENVIRONMENT.is_Revit_environment():
        if random.random() < 0.7:
            show_tip_revit()
        else:
            show_scott_tip()
    if ENVIRONMENT.is_Rhino_environment():
        show_tip_rhino()
        
        
def unit_test():
    # tip_of_day()
    pass
    
    
def print_documentation_book_for_review_revit():
    """print all the tip in a book or webpage so can check spelling and doc updates."""
    show_tip_revit(is_random_single=False)
    
    OUTPUT.display_output_on_browser()

def show_floating_box_warning():
    import NOTIFICATION
    NOTIFICATION.duck_pop(main_text="Click has no use for this button. Just hold down on the arrow and drag to make the window floating.\nThis will always stay on top even when changed to another tab.")
    
    
def get_floating_box_documentation():
    return "Hold down on the arrow and drag to make the window floating. This will always stay on top even when changed to another tab."
    
    
    
    
    
if __name__ == "__main__":
    show_scott_tip()
    