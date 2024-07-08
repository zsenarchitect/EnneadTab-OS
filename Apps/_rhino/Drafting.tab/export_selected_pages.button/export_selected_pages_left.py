__title__ = "ExportSelectedLayout"
__doc__ = "Export selected layout(s) to pdf"



import rhinoscriptsyntax as rs
from scriptcontext import doc
import Rhino # pyright: ignore
import os

from EnneadTab.RHINO import RHINO_FORMS, RHINO_OUTPUT
from EnneadTab import LOG, ERROR_HANDLE


def get_page_by_name(name):
    for view in doc.Views.GetPageViews():
        if view.PageName == name:
            return view

    return None

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def export_selected_pages_left():

    page_names = [x.PageName for x in doc.Views.GetPageViews()]
    page_names.sort()
    selected_layout_names = RHINO_FORMS.select_from_list(page_names,
                                                        message = "pick the layout(s) to duplicate.",
                                                        multi_select = True)

    if selected_layout_names is None:
        return

    output_folder = rs.BrowseForFolder(message="Where should the output pdf be?",
                                       title = __title__)

    res = rs.ListBox(["Open PDF after export", "Just export"],
                             message = "Do you want to open PDF?",
                             title = __title__)
    should_open = res == "Open PDF after export"
    for page_name in selected_layout_names:
        page = get_page_by_name(page_name)
        # print (page_name)
        # print (page)
        width, height = RHINO_OUTPUT.PaperSize.Tabloid
        filepath = "{}\{}.pdf".format(output_folder, page_name)
        scale = 1
        color_style =  RHINO_OUTPUT.OutputColorStyle.PrintColor
        rs.Command("!_-Print Setup View Viewport \"{}\" Scale {} -Enter Destination Printer \"Microsoft Print to PDF\" PageSize {} {} OutputColor {} -Enter -Enter Go \"{}\" -Enter -Enter".format(page_name,
                                                                                                                                                                                                   scale,
                                                                                                                                                                                                    width,
                                                                                                                                                                                                    height,
                                                                                                                                                                                                    color_style,
                                                                                                                                                                                                    filepath))

        #OutputType Raster -- this is a toggle, not a assignment, hmm tricky


        if should_open:
            os.startfile(filepath)


if __name__ == "__main__":
    export_selected_pages_left()