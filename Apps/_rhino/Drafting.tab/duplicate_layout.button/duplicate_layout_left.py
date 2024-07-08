
__title__ = "DuplicateLayout"
__doc__ = "Duplicate Layout while allowing X-Y offset, so your layout can capture something else in model space."

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # pyright: ignore

from EnneadTab.RHINO import RHINO_FORMS
from EnneadTab import DATA_FILE, LOG, ERROR_HANDLE



def get_page_by_name(name):
    for view in sc.doc.Views.GetPageViews():
        if view.PageName == name:
            return view

    return None


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def duplicate_layout():

    page_names = [x.PageName for x in sc.doc.Views.GetPageViews()]
    page_names.sort()
    selected_layout_names = RHINO_FORMS.select_from_list(page_names,
                                                        message = "pick the layout(s) to duplicate.",
                                                        multi_select = True)

    if selected_layout_names is None:
        return

    default_X = DATA_FILE.get_sticky_longterm("DUPLICATE_PAGE_CAMERA_SHIFT_X", 100)
    default_Y = DATA_FILE.get_sticky_longterm("DUPLICATE_PAGE_CAMERA_SHIFT_Y", 0)
    X, Y = rs.PropertyListBox(["X increment(file unit)", "Y increment(file unit)"], [default_X,default_Y], message = "For duplicated sheet's viewport, how do you want to shift camera?")
    X, Y = float(X), float(Y)
    DATA_FILE.set_sticky_longterm("DUPLICATE_PAGE_CAMERA_SHIFT_X", X)
    DATA_FILE.set_sticky_longterm("DUPLICATE_PAGE_CAMERA_SHIFT_Y", Y)

    for page_name in selected_layout_names:
        page = get_page_by_name(page_name)
        new_page = page.Duplicate(True)
        new_page.PageName = page_name + "_duplicated"
        #till here the duplicatation is finished


        for detail_view in new_page.GetDetailViews():
            #print detail_view.Name
            #print detail_view
            #detail_view.IsActive = True
            original_lock_statge = detail_view.DetailGeometry.IsProjectionLocked
            #print original_lock_statge
            detail_view.DetailGeometry.IsProjectionLocked = False
            detail_view.CommitChanges()
            #print rs.DetailLock(detail_view)
            viewport = detail_view.Viewport
            viewport.SetCameraLocation(viewport.CameraLocation + Rhino.Geometry.Vector3d(X,Y,0), True)
            detail_view.CommitViewportChanges()
            rs.DetailLock(detail_view, lock = original_lock_statge)
            #print rs.DetailLock(detail_view)



if __name__ == "__main__":
    duplicate_layout()