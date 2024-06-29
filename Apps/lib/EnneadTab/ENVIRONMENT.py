#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys




IS_PY3 = sys.version.startswith("3")
IS_PY2 = not IS_PY3


# this is the repo folder if you are developer, or EA_dist if you are user
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


INSTALLATION_FOLDER = os.path.join(ROOT, "Installation")


APP_FOLDER = os.path.join(ROOT, "Apps")
REVIT_FOLDER = os.path.join(APP_FOLDER, "_revit")
RHINO_FOLDER = os.path.join(APP_FOLDER, "_rhino")


LIB_FOLDER = os.path.join(APP_FOLDER, "lib")
CORE_FOLDER = os.path.join(LIB_FOLDER, "EnneadTab")
IMAGE_FOLDER = os.path.join(CORE_FOLDER, "images")
AUDIO_FOLDER = os.path.join(CORE_FOLDER, "audios")
DOCUMENT_FOLDER = os.path.join(CORE_FOLDER, "documents")

EXE_ROOT_FOLDER = os.path.join(LIB_FOLDER, "exes")
EXE_PRODUCT_FOLDER = os.path.join(EXE_ROOT_FOLDER, "products")

DEPENDENCY_FOLDER = os.path.join(LIB_FOLDER, "dependency")
if IS_PY2:
    DEPENDENCY_FOLDER += "\\py2"
else:
    DEPENDENCY_FOLDER += "\\py3"




def is_Rhino_environment():
    """Check if current environment is Rhino.

    Returns:
        bool: True if current environment is Rhino.
    """
    try:
        import rhinoscriptsyntax
        return True
    except:
        return False

def is_Grasshopper_environment():
    try:
        import Grasshopper # pyright: ignore
        return True
    except:
        return False

def is_Revit_environment():
    """Check if current environment is Revit.

    Returns:
        bool: True if current environment is Revit.
    """
    try:
        from Autodesk.Revit import DB # pyright: ignore
        return True
    except:
        return False

def is_RhinoInsideRevit_environment():
    try:
        import clr # pyright: ignore
        clr.AddReference('RhinoCommon')
        clr.AddReference('RhinoInside.Revit')
        return True
    except:
        return False

    
def is_terminal_environment():
    return not is_Rhino_environment() and not is_Revit_environment()

def unit_test():
    import inspect
    # get all the global varibales in the current script

    for i, x in enumerate(sorted(globals())):
        content = globals()[x]
        
        if inspect.ismodule(content):
            continue
        
        if not x.startswith("_") and not callable(content):
            print(x, " = ", content)

            
            if isinstance(content, bool):
                continue
            
            if not isinstance(content, list):
                content = [content]

            for item in content:
                if "\\" in item:
                    is_ok = os.path.exists(item) or os.path.isdir(item)
                    assert is_ok

          
IS_RHINO_ENVIRONMENT = is_Rhino_environment()
IS_GRASSHOPPER_ENVIRONMENT = is_Grasshopper_environment()
IS_REVIT_ENVIRONMENT = is_Revit_environment()
IS_RHINOINSIDEREVIT_ENVIRONMENT = is_RhinoInsideRevit_environment()


def get_app_name():
    app_name = "terminal"
    if is_Revit_environment():
        app_name = "revit"
    elif is_Rhino_environment():
        app_name = "rhino"
    return app_name

###############
if __name__ == "__main__":
    unit_test()