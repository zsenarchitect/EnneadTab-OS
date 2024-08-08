__doc__ = "Prefix selected ref plane with 'W_' in the name"


from pyrevit import forms, DB, revit, script, output


################## main code below #####################
output = script.get_output()
output.close_others()

rps = revit.get_selection()

with revit.Transaction("rename rps"):

    for i, rp in enumerate(rps):
        #rp.Name = "NS_{}".format(i+1)
        #rp.Name = "E_{}".format(i+1)
        rp.Name = "W_{}".format(i+1)
