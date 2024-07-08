#!/usr/bin/python
# -*- coding: utf-8 -*-
import RHINO_FORMS

import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
import ENVIRONMENT
if ENVIRONMENT.is_Rhino_environment():
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

# [] is no longer good because it trigger layertable lookup error if put at very front.
# <> seems to be better
def rhino_layer_to_user_layer(name):
    return "<{}>".format(name.replace("::", "> - <"))


def user_layer_to_rhino_layer(name):
    return name[1:-1].replace("> - <", "::")


def get_layers(multi_select = True, message = "", layers = None):
    if layers is None:
        layers = sorted(rs.LayerNames())

    options = [rhino_layer_to_user_layer(x) for x in layers]
    sel_layers = RHINO_FORMS.select_from_list(options, multi_select = multi_select, message = message)
    if not sel_layers:
        return None
    layers = [user_layer_to_rhino_layer(x) for x in sel_layers]
    return layers

def get_layer(message = ""):
    return get_layers(multi_select = False, message = message)[0]

def secure_layer(layer):
    if not rs.IsLayer(layer):
        rs.AddLayer(layer)
    return layer
