
import ast



import os


from BaseHandler import BaseHandler
from IconHandler import IconHandler
from GuidHandler import GuidHandler
from constants import MAIN_FOLDER


class MacroHandler(BaseHandler):
    """Note to self:
    Macro is the foundation of all toolbar layout, that link scattered information to UI
    there can be multiple UI items(button left right click, or menu item) call for same macro. In rhino manual edit you can recycle macro usage, but there is little benefit doing that if I am building rui dhnamically, 
    So let each macro be unique is the best/simplest way.."""

    
    """THis is what need to be filled for a typical macro item.
    need to have those attrs:
    - guid -----> created when init instance
    - bitmap_id -----> only retrieve that at this stage by looking for icon file in same folder. 
                        Still use IconHandler but Dont pass a big dict around
    - text ----> parse from script
    - tooltip ----> parse from script
    - help_text ----> parse from script
    - button_text ----> parse from script
    - menu_text ----> parse from script
    - script ----> firgure out here

    Example:    
        <macro_item guid="f15302e0-b388-452e-aa50-791a080ae744" bitmap_id="329c4ab7-6a9e-4e1e-acd7-0a57500af57a">
      <text>
        <locale_1033>macro_name_test</locale_1033>
      </text>
      <tooltip>
        <locale_1033>tooltip text test</locale_1033>
      </tooltip>
      <help_text>
        <locale_1033>help text test</locale_1033>
      </help_text>
      <button_text>
        <locale_1033>button_text_test</locale_1033>
      </button_text>
      <menu_text>
        <locale_1033>menu_text_test</locale_1033>
      </menu_text>
      <script>_show</script>
    </macro_item>


    """
    def __init__(self, script_path):
        self.script_path = script_path
        self.script_name = os.path.basename(script_path).replace(".py", "")
        # create unique guid that looks like this d58ceae7-fdb0-4104-80da-274b94ad44a9
        self.guid = GuidHandler(script_path).guid
        # print (self.guid)
        self.icon = self.get_icon()
        
        # parse this python by load it to extract gloabl vars by path
        self.script_gloabl_vars_dict = extract_global_variables(self.script_path)

        # find a template to write script, tooltip, and other default info.
        self.assign_basic_info()
        self.script = self.get_script()



    def __repr__(self) -> str:
        return f"MacroHandler({self.script_name})"

    def print_detail(self):
        print ("\n\n")
        print ("MacroHandler Details: [{}]".format(self.script_name))
        for attr in sorted(dir(self)):
            if not attr.startswith("_") and not callable(getattr(self, attr)):
                print (attr, getattr(self, attr), sep=": ")

 


    def assign_basic_info(self):
        
        
        attr_dict = {"text":"__alias__", # become the macro name, not visible to user, can have duplicate
                     "tooltip":"__doc__", # become text during mouse hovering, visible to user
                     "help_text":"__doc__", # detailed description, not visible to user
                     "button_text":"__alias__", # become the button text when used as left click macro. Visible to user.
                     "menu_text":"__alias__"} # become the menu text. Visible to user.
        for key, attr in attr_dict.items():

            value = self.script_gloabl_vars_dict.get(attr, "N/A")

            if attr == "__alias__" and value == "N/A":
                value = self.script_name
            if key == "__doc__" and value == "N/A":
                value = "Documentation Pending for <" + self.script_name + ">"
  

            # allow some script to have multiple alias to create with different shorthand
            if isinstance(value, list):
                value = value[0]
                
            setattr(self, key, value)
            
        
    def get_icon(self):
        current_folder = os.path.dirname(self.script_path)
        for f in os.listdir(current_folder):
            if 'icon' in f:
                # make sure the file extension is either .png or .svg
                if f.endswith('.png') or f.endswith('.svg'):
                    icon_path = os.path.join(current_folder, f)
                    
                    return IconHandler(icon_path, caller = self.script_name)
     

        return IconHandler(None, caller = self.script_name)

    def get_script(self):
        """TO-DO:
         use a template format to fill in info. 
        [Or] create alias automatically and call that.

        (Prefer second for long term effort. It is cleaner to read, BUT do require USER to register all alias dynamically.)
        """


        locator = self.script_path.split("Toolbar\\")[1]
        locator = locator.replace("\\", "\\\\")

        #This macro is auto-generated, manual modification will be discarded;
        # note to self: using ; at the end of the line to simulate a one-liner python
        script = """! _-RunPythonScript (
import sys
sys.path.append('L:\\\\4b_Applied Computing\\\\03_Rhino\\\\12_EnneadTab for Rhino\\\\Toolbar')
import RHINO_MODULE_HELPER
locator = '{}'
RHINO_MODULE_HELPER.run_Rhino_button(locator)
)
""".format(locator)
        return script

    
    def as_json(self):
        data =  {
            "@guid": self.guid,
            "@bitmap_id": self.icon.guid,
            "text": {"locale_1033": self.text},
            "tooltip": {"locale_1033": self.tooltip},
            "help_text": {"locale_1033": self.help_text},
            "button_text": {"locale_1033": self.button_text},
            "menu_text": {"locale_1033": self.menu_text},
            "script": self.script
        }

        return {"macro_item": data}
        


def force_load_enneadtab(contents):
    contents.insert(0, "import sys\nimport importlib\n\n")
    contents.insert(1, "sys.path.append('C:\\\\Users\\\\szhang\\\\github\\\\EnneadTab-for-Rhino\\\\Source Codes\\\\lib')\n\n\n")
    add = """
temp_spec = importlib.util.spec_from_file_location("EnneadTab", 
                                                'C:\\\\Users\\\\szhang\\\\github\\\\EnneadTab-for-Rhino\\\\Source Codes\\\\lib\\\\EnneadTab\\\\__init__.py')
temp_module = importlib.util.module_from_spec(temp_spec)

sys.modules[temp_spec.name] = temp_module
temp_spec.loader.exec_module(temp_module)
"""
    contents.insert(2, add)


    return contents

class ClickBehavior:
    Left = "_left.py"
    Right = "_right.py"

def get_macro(button_folder, click):

    for folder, _, files in os.walk(button_folder):
        for f in files:
            # dont want to process the helper scripts.
            if click in f:
                script_path = os.path.join(folder, f)
                # macros.append(MacroHandler(script_path))
                return MacroHandler(script_path)

    return None

def extract_global_variables(script_path):
    with open(script_path, 'r') as file:
        script_content = file.read()
    
    tree = ast.parse(script_content)
    global_vars = {}
    
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Handling the value directly if it's a constant
                    if isinstance(node.value, ast.Constant):
                        var_value = node.value.value  # Directly accessing the value of the Constant node
                    else:
                        try:
                            # Fallback for other types using literal_eval for safe evaluation
                            var_value = ast.literal_eval(node.value)
                        except ValueError:
                            # For non-literals or complex cases, keep a representation of the code
                            var_value = "Unsupported value for safe evaluation"
                    global_vars[var_name] = var_value
    
    return global_vars
    
if __name__ == "__main__":
    pass
