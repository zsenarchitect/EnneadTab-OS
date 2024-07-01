import os
import yaml

from constants import MAIN_FOLDER, SPECIAL_LIST_KEY
import ButtonHandler as BH
from IconHandler import IconHandler
from BaseHandler import BaseHandler
from GuidHandler import GuidHandler


class TabHandler(BaseHandler):
    def __init__(self, tab_folder):
        self.guid = GuidHandler(tab_folder).guid
        self.tab_folder = tab_folder
        self.tab_name = os.path.basename(tab_folder).replace(".tab", "")
        # order buttons based on some markup file in the tab folder
        self.buttons = BH.get_buttons(tab_folder)
        self.icon = self.get_icon()


    def __repr__(self) -> str:
        return f"TabHandler({self.tab_name})"

    def get_icon(self):
        # self.tab_folder = os.path.dirname(self.tab_folder)
        for f in os.listdir(self.tab_folder):
            if 'icon' in f:
                # make sure the file extension is either .png or .svg
                if f.endswith('.png') or f.endswith('.svg'):
                    icon_path = os.path.join(self.tab_folder, f)
                    
                    return IconHandler(icon_path, caller=self.tab_name)

        return IconHandler(None, caller=self.tab_name) 
      
    
    def as_json(self):
        data = {
            "@guid": self.guid,
            "@bitmap_id": self.icon.guid,
            "@item_display_style": "control_and_text",
            "text": {"locale_1033": self.tab_name},
            SPECIAL_LIST_KEY: [x.as_json() for x in self.buttons]
            
        }
        data = {"tool_bar":data}
        return data


def get_yaml(folder):
    for folder, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".yaml"):
                return os.path.join(folder, file)

    return None

def get_tabs():

    tabs = []
    
    layout_file = get_yaml(MAIN_FOLDER)


            
    for folder, _, files in os.walk(MAIN_FOLDER):
        if folder.endswith(".tab"):
            tabs.append(TabHandler(folder))

    if layout_file:
        with open(layout_file, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        order = data.get('layout', None)  
        if order:
            return get_ordered_tabs(order, tabs)
    # print (tabs)
    return tabs


def get_ordered_tabs(order, tabs):
    ordered_tabs = []
            
    for prefered_tab in order:
        if prefered_tab == "---":
            continue
        for tab in tabs:
            if tab.tab_name == prefered_tab:
                ordered_tabs.append(tab)
                tabs.remove(tab)
                break
    
    if len(tabs) > 0:
        ordered_tabs.extend(tabs)

    
    return ordered_tabs

if __name__ == "__main__":
    tabs = get_tabs()
    print (tabs)

    for tab in tabs:
        print ("\n\n")
        print (tab.as_json())