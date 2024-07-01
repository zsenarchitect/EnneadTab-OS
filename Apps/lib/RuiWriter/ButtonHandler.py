import os

import yaml

from constants import OS_ROOT_FOLDER
import MacroHandler as MH
from BaseHandler import BaseHandler
from GuidHandler import GuidHandler


# <tool_bar_item guid="5c14bc8c-eb99-4599-b7bc-4de133a3d6cc" button_style="spacer" />
# <menu_item guid="6de83a3d-ab35-4bcd-a7d6-b027b675a472" item_type="separator" />
class DividerHandler(BaseHandler):
    def __init__(self, is_menu):
        self.guid = GuidHandler("divider").guid
        self.is_menu = is_menu

    def __repr__(self):
        note= "a divider in menu" if self.is_menu else "a divider in toolbar"
        return f"DividerHandler({note})"
    
    def as_json(self):
        data = {
            "@guid": self.guid,
            "button_style": "separator" if self.is_menu else "spacer"
        }
        if self.is_menu:
            return {"menu_item":data}
        else:
            return {"tool_bar_item":data}


class ButtonHandler(BaseHandler):
    def __init__(self, button_folder, is_menu):
        self.guid = GuidHandler(button_folder).guid
        self.button_folder = button_folder
        self.button_name = os.path.basename(button_folder).replace(".button", "")
        self.macro_left = MH.get_macro(button_folder, MH.ClickBehavior.Left)
        self.macro_right = MH.get_macro(button_folder, MH.ClickBehavior.Right)

        self.is_menu = is_menu


    def __repr__(self) -> str:
        return f"ButtonHandler({self.button_name})"

    
    def as_json(self):
        data = {
            "@guid": self.guid,
            "text": {"locale_1033": self.button_name}
        }

        # do the check in case there are no left/right click planned
        if self.is_menu:
            data["macro_id"] = self.macro_left.guid
            return {"menu_item":data}
        
        else:
            if self.macro_left:
                data["left_macro_id"] = self.macro_left.guid
            if self.macro_right:
                data["right_macro_id"] = self.macro_right.guid
            return {"tool_bar_item":data}
    
def get_buttons(tab_folder, is_menu=False):

    buttons = []
    
    layout_file = None
    for folder, _, files in os.walk(tab_folder):
        for file in files:
            if file.endswith(".yaml"):
                layout_file = os.path.join(folder, file)
                break
    

    for folder, _, files in os.walk(tab_folder):
        if folder.endswith(".button"):
            buttons.append(ButtonHandler(folder, is_menu))

    if layout_file:
        with open(layout_file, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        order = data.get('layout', None)  
        if order:
            return get_ordered_buttons(order, buttons, is_menu)
        
    return buttons

def get_ordered_buttons(order, buttons, is_menu):
    ordered_buttons = []
            
    for prefered_button in order:
        if prefered_button == "---":
            ordered_buttons.append(DividerHandler(is_menu))
            continue
        for button in buttons:
            if button.button_name == prefered_button:
                ordered_buttons.append(button)
                buttons.remove(button)
                break
    
    if len(buttons) > 0:
        ordered_buttons.append(DividerHandler(is_menu))
        ordered_buttons.extend(buttons)
    return ordered_buttons

if __name__ == "__main__":
    buttons = get_buttons(OS_ROOT_FOLDER)
    print (buttons)