__doc__ = "Set surface divider number on selected face."
__title__ = "09_add node to surf, N3 spehere only"

from pyrevit import forms, DB, revit, script


################## main code below #####################
output = script.get_output()
output.close_others()



selection = revit.get_selection()

with revit.Transaction("turn on nodes"):
    for item in selection:
        #print item.Category.Name
        item.Parameter[DB.BuiltInParameter.DIVIDED_SURFACE_DISPLAY_NODES].Set(1)
        #print item.Parameter[DB.BuiltInParameter.DIVIDED_SURFACE_RULE_2_SUSPENSION].AsInteger()
        #print item.Parameter[DB.BuiltInParameter.DIVIDED_SURFACE_GRID_OPTION_PARAM_1].AsInteger()
        #print item.Parameter[DB.BuiltInParameter.DIVIDED_SURFACE_GRID_OPTION_PARAM_2].AsInteger()
        #print item.NumberOfUGridlines
        #print item.NumberOfVGridlines
        item.USpacingRule.SetLayoutNone()
        item.VSpacingRule.SetLayoutFixedNumber(30,DB.SpacingRuleJustification.Center,0,0)
