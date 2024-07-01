
__alias__ = "(1634)ExportWithoutCrv"
__doc__ = "Export the rhino file as dwg but solidate all blocks and remove all crvs."

import rhinoscriptsyntax as rs
from EnneadTab import NOTIFICATION


def export_without_crv():
    block_collection = []
    all_block_names = rs.BlockNames( sort = False )
    for i, block_name in enumerate(all_block_names):

        print ("{}/{} {}".format(i+1, len(all_block_names), block_name))

        if rs.IsBlockReference(block_name):
            continue
        try:
            blocks = rs. BlockInstances(block_name)
        except:
            print ("Bad block name: " + block_name)
            continue
        blocks = [x for x in blocks if not rs.IsObjectHidden(x)]
        block_collection.extend(blocks)

    block_collection_trash = rs.CopyObjects(block_collection)

    rs.StatusBarProgressMeterShow(label = "working {} blocks".format(len(block_collection_trash)),
                                lower = 0,
                                upper = len(block_collection_trash),
                                embed_label = True,
                                show_percent = True)
    trash_geo = []
    if block_collection_trash is not None:
        for i, block in enumerate(block_collection_trash):
            rs.StatusBarProgressMeterUpdate(position = i, absolute = True)
            if (i+1) % 10 == 0:
                NOTIFICATION.messenger("{}/{} {}".format(i+1, len(block_collection_trash), rs.BlockInstanceName(block)))
            try:
                trash_geo.extend(rs.ExplodeBlockInstance(block, explode_nested_instances = True))
            except Exception as e:
                print (e)
                continue

    rs.StatusBarProgressMeterHide()
    all_objs = rs.AllObjects()
    good_objs = [x for x in all_objs + trash_geo if not rs.IsBlockInstance(x) and  not rs.IsCurve(x)]
    rs.UnselectAllObjects()
    rs.SelectObjects(good_objs)

    if rs.DocumentName() == "MotherBabyLobby.3dm":
        filepath = "J:\\1643\\0_BIM\\02_Linked CAD\\TempStudy_MotherBabyLobby.dwg"
    else:
        filepath = "J:\\1643\\0_BIM\\02_Linked CAD\\TempStudy.dwg"
    rs.Command("!_-Export \"{}\" Scheme  \"2007 Solids\" -Enter -Enter".format(filepath), echo = False)


    rs.DeleteObjects(trash_geo)
    rs.UnselectAllObjects()

    NOTIFICATION.messenger(main_text = "special dwg exported!")