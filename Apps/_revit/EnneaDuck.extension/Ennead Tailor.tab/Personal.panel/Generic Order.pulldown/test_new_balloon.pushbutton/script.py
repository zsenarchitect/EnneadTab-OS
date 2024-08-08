"""Activates selection tool that picks a specific type of element.

Shift-Click:
Pick favorites from all available categories
"""
# pylint: disable=E0401,W0703,C0103
from collections import namedtuple

from pyrevit import revit, UI, DB
from pyrevit import forms
from pyrevit import script


def func():
    print ("In func")

import traceback

try:
    forms.show_balloon(header= "header", 
                    text="test", 
                    tooltip='123213', 
                    group='top', 
                    is_favourite=False, 
                    is_new=False, 
                    timestamp=None, 
                    click_result=func)
    
except:
    print (traceback.format_exc())