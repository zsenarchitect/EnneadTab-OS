__doc__ = "Attemp to match sketch element. DO NOT USE, see newer api for eketch class."
__title__ = "GUI\nMatch Pink"
# dependencies
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml
from pyrevit import UI
from pyrevit import script, revit, forms, HOST_APP
from pyrevit.forms import WPFWindow
xamlfile = script.get_bundle_file('UI.xaml')

# import WPF creator and base Window
import wpf
from System import Windows

class UI_Window(WPFWindow):
    def __init__(self):
        WPFWindow.__init__(self, xamlfile)
        #wpf.LoadComponent(self, xamlfile)
        self.set_image_source(self.logo_img, "logo_V.png")
        output= script.get_output()
        output.close_others()

    @property
    def shared_varabile(self):
        return self.textbox1.Text


    def BT_pick_ref_element(self, sender, args):###sender and args must be here even when not used to pass data between GUI and python
        variable = self.shared_varabile
        #variable = self.textbox1.Text   use this line if dont want to use @property in the class

        selection = revit.pick_element()
        """
        object_type = UI.Selection.ObjectType.Element
        selection = HOST_APP.uidoc.Selection
        selection.PickObject(object_type,\
                            "pick a floor or ceiling")
                            """


        while True:
            if len(selection) != 1:
                forms.alert("Please select 1 element only.")
                continue
            if selection[0].Category.Name not in ["Floors", "Ceilings"]:
                forms.alert("Need to be floor or ceiling.")
                continue
            break


        for item in selection:
            print(item)
        elid = selection.element_ids
        data = elid[0].IntegerValue

        print("Function run ok after clicking button\n\tget: {}".format(variable))
        forms.alert("ref element selected: {}".format(data))
        UI.TaskDialog.Show(
            "title here from script",
            "sample text in function with: {}".format(variable)
            )


UI_Window().ShowDialog()
