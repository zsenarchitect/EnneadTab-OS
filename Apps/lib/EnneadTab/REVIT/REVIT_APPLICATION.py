#!/usr/bin/python
# -*- coding: utf-8 -*-

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore



def get_app():
    app = __revit__ # pyright: ignore
    if hasattr(app, 'Application'):
        app = app.Application
    return app


def get_uiapp():
    """Return UIApplication provided to the running command."""
    if isinstance(__revit__, UI.UIApplication): # pyright: ignore
        return __revit__  # pyright: ignore

    from Autodesk.Revit import ApplicationServices # pyright: ignore
    if isinstance(__revit__, ApplicationServices.Application): # pyright: ignore
        return UI.UIApplication(__revit__) # pyright: ignore
    return __revit__ # pyright: ignore


def get_uidoc():
    """Return active UIDocument."""
    return getattr(get_uiapp(), 'ActiveUIDocument', None)


def get_doc():
    """Return active Document."""
    return getattr(get_uidoc(), 'Document', None)


