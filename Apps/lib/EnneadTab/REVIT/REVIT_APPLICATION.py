#!/usr/bin/python
# -*- coding: utf-8 -*-

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore



def get_application():
    
    app = __revit__
    if hasattr(app, 'Application'):
        app = app.Application
   
    return app

