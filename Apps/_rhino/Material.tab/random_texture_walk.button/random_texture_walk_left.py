
__title__ = "RandomTextureWalk"
__doc__ = "Randomly walk the texture map a bit to avoid them lineup"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # pyright: ignore
import random
import clr # pyright: ignore
from EnneadTab import DATA_FILE, NOTIFICATION
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def random_texture_walk():
    objs = rs.GetObjects("Pick objs to random texture walk", preselect=True)
    if not objs:
        NOTIFICATION.messenger("nothing selected.")
        return

    default_mapping = None

    default_factor = DATA_FILE.get_sticky_longterm("TEXTURE_RANDOM_WALK", 1)
    limit = rs.RealBox("range from -? to ?", default_number=default_factor) # from -1 to 1
    for obj in objs:
        original_transform =  clr.StrongBox[Rhino.Geometry.Transform](Rhino.Geometry.Transform.Identity)
        try:
            mapping = sc.doc.Objects.FindId (obj).GetTextureMapping(1, original_transform)
            original_transform = original_transform.Value
            default_mapping = mapping
            has_existing_texture = True
        except:
            mapping = default_mapping
            has_existing_texture = False

        move_transform = Rhino.Geometry.Transform.Translation(limit*(random.random()-0.5)*2,
                                                        limit*(random.random()-0.5)*2,
                                                        limit*(random.random()-0.5)*2)

        final_transform = move_transform * original_transform

        if has_existing_texture:
            sc.doc.Objects.FindId (obj).SetTextureMapping(1, mapping, final_transform)
        else:
            sc.doc.Objects.ModifyTextureMapping(obj, 1, mapping)

    DATA_FILE.set_sticky_longterm("TEXTURE_RANDOM_WALK", limit)
    NOTIFICATION.messenger("texture random walk done.")

if __name__ == "__main__":
    random_texture_walk()