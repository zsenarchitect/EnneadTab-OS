import os

from constants import SPECIAL_LIST_KEY
import ButtonHandler as BH

from BaseHandler import BaseHandler
from GuidHandler import GuidHandler



class MenuHandler(BaseHandler):
    def __init__(self, menu_folder):
        self.guid = GuidHandler(menu_folder).guid
        self.menu_folder = menu_folder
        self.menu_name = os.path.basename(menu_folder).replace(".menu", "")
        # order buttons based on some markup file in the menu folder
        self.buttons = BH.get_buttons(menu_folder, is_menu=True)


    def __repr__(self) -> str:
        return f"MenuHandler({self.menu_name})"

    
    
    def as_json(self):
        data = {
            "@guid": self.guid,
            "text": {"locale_1033": self.menu_name},
            SPECIAL_LIST_KEY: [x.as_json() for x in self.buttons]
            
        }
        data = {"menu":data}
        return data

def get_menus(search_folder):

    menus = []

    for folder, _, files in os.walk(search_folder):
        if folder.endswith(".menu"):
            menus.append(MenuHandler(folder))


    # print (menus)
    return menus


if __name__ == "__main__":
    menus = get_menus()
    print (menus)

    for menu in menus:
        print ("\n\n")
        print (menu.as_json())