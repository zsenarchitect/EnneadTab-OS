#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Using bluebeam for markup is tricky when your old markup cannot transfer to new PDF background.

Now you have many version of the markup and you need to repeatively markup same content if they are not picked up.

With review Revit on miro, you can export the sheets as images and push them to a dedicated Miro board.
New sheets will be marked with blue cross, updated sheets will be marked with orange star.

You are free to reorganize sheets however you want and mark as much as you like. The updated image will find the replace background image and your markup will continously live untill they are picked up.


Note: Due to CBI account restriction, I can only use a personal miro account for it. Feel free to just ask me for a board."""
__title__ = "Review\nOn Miro"
__tip__ = True
import shutil
from pyrevit import forms #
from pyrevit import script #



from EnneadTab.REVIT import REVIT_EXPORT, REVIT_APPLICATION
from EnneadTab import EXE, DATA_FILE, NOTIFICATION, ERROR_HANDLE, FOLDER
from Autodesk.Revit import DB # pyright: ignore 
import os
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
            
@ERROR_HANDLE.try_catch_error()
def update_miro():

    print ("Note: At the moment CBI does not allow me to connect to Miro, so your team can ask me for a board on my personal account.")
    key = "recent_miro_url"
    recent_url = DATA_FILE.get_sticky_longterm(key,"https://miro.com/app/board/uXjVNsgWNfA=/")
    miro_url = forms.ask_for_string(
        prompt = "Please input the Miro board URL:",
        default= recent_url,
        title = "Makrup Sheet In Miro")

    print ("Miro URL: " + miro_url)
    DATA_FILE.set_sticky_longterm(key, miro_url)

    sheets = forms.select_sheets(title = "Select sheets to update")
    if not sheets:
        return



    res = REVIT_APPLICATION.do_you_want_to_sync_and_close_after_done()

    dump_folder = "{}\\miro_dump".format(FOLDER.get_EA_local_dump_folder())

    # make sure everytig is the lastest in this folder

    try:
        if os.path.exists(dump_folder):
            shutil.rmtree(dump_folder)

        os.mkdir(dump_folder)
    except:
        pass

    for i, sheet in enumerate(sheets):
        sheet_name = sheet.Name
        sheet_num = sheet.SheetNumber
        guid = sheet.UniqueId
        file = "{}^{}^{}.jpg".format(guid,
                                    sheet_num,
                                    sheet_name)

        NOTIFICATION.messenger ("Exporting image {}/{}==> {}:{}".format(i + 1, len(sheets), sheet_num, sheet_name))
        REVIT_EXPORT.export_image(sheet, file, dump_folder)
    
    NOTIFICATION.duck_pop("Image Export done!\nPreparing to upload to Miro!")
    
    with DATA_FILE.update_data("miro.json") as data:
        data['url'] = miro_url
        data["images"] = [os.path.join(dump_folder, f) for f in sorted(os.listdir(dump_folder), key=lambda x: x.split("^")[1])]
        data["app"] = "revit_sheet"

    EXE.open_exe("MIRO")


    if res:
        REVIT_APPLICATION.sync_and_close()
    


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_miro()
    







