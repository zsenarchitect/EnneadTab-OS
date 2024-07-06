
__alias__ = "FilterBlockByName"
__doc__ = "This button does FilterBlockByName when left click"
import rhinoscriptsyntax as rs
import scriptcontext as sc


from Duckitect.RHINO import RHINO_FORMS


def filter_block_by_name():

    # get all block names and sort
    all_block_names = sorted(rs.BlockNames())
    #note = "<Get all currently shortlisted>"
    #all_block_names.insert(0, note)

    # select multuple
    selected_block_names = RHINO_FORMS.select_from_list(all_block_names, 
                                                        multi_select = True, 
                                                        message = "Type the portion of block names you want to select")

    if not selected_block_names:
        return

    # select all blocks pass that names
    OUT = []
    for name in selected_block_names:
        OUT.extend(rs.BlockInstances(name))

    rs.UnselectAllObjects()
    rs.SelectObjects(OUT)