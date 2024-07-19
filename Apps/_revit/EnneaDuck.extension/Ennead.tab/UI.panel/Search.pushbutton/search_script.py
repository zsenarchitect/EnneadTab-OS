# -*- coding=utf-8 -*-
#pylint: disable=undefined-variable,import-error,invalid-name
__doc__ = "Commandline for Revit\n\nFind those button function you might not know where to find.\nThe search result is ranked as follow:\n-Tool name begins with user input text.\n-Tool name contains user input text.\n-Tool help documentation contains user input text.\n\nThe main info panel shows the button icon image, which panel to find it, the full documentation, any hyper link to EI post and Youtube Demo video if available. \nYou can also directly activate the tool with the 'GO' button or 'Enter' key.\n\nYou also have the option to search only EnneadTab buttons or Native Revit buttons.\nOn top left corner there is a minimize button, so you can keep it small when not using it."
__title__ = "Search\nCommand"
__tip__ = True


import clr
import System
import time
import traceback
import random
import sys

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException


from pyrevit.revit import ErrorSwallower
from pyrevit import script, forms
try:
    from pyrevit.loader import sessionmgr
except:
    # allow startup query to skip the external event creation
    pass
from pyrevit import coreutils
import pyrevit.extensions as py_extensions
from pyrevit import HOST_APP

import proDUCKtion # pyright: ignore 

from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import USER, ENVIRONMENT, SOUND, TIME, ERROR_HANDLE, FOLDER


uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True


WPF_COLLAPSED = System.Windows.Visibility.Collapsed
WPF_VISIBLE = System.Windows.Visibility.Visible


@ERROR_HANDLE.try_catch_error()
def run_command_action(command, is_enneadtab):

    def run_enneadtab_command(command):
        from pyrevit.loader import sessionmgr
        sessionmgr.execute_command(command.unique_id)


    def run_native_command(command):
        """
        if matched_cmdname in postable_cmds.keys():
            if any(switches.values()):
                forms.alert('This is a native Revit command.')
            else:
        """
        __revit__.PostCommand(command.rvtobj)



    if is_enneadtab:
        run_enneadtab_command(command)
    else:
        run_native_command(command)






# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(*self.kwargs)
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"




# A simple WPF form used to call the ExternalEvent
class EA_search_UI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.run_command_action_event_handler = SimpleEventHandler(run_command_action)
        #self.clock_event_handler = SimpleEventHandler(clock_work)
        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.run_command_action_event_handler)
        #self.ext_event_clock = ExternalEvent.Create(self.clock_event_handler)
        #print "preaction done"
        #print self.run_command_action_event_handler
        #print self.run_command_action_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'EA_search_UI.xaml'
        try:
            forms.WPFWindow.__init__(self, xaml_file_name)
        except:
            return
        
        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.load_commands()
        self._result_index = 0
        self._search_results = []
        self.doc_textblock.Text = ""
        self.search_textbox.Focus()
        self.search_textbox.SelectAll()
        self.set_visibility_collapse(self.doc_display_panel)

        self.Show()
        self.is_x_imported("System", "after UI iniite and show")



    @property
    def entered_text(self):
        return self.search_textbox.Text

    @property
    def _search_data_keys(self):
        return self.search_datas.keys()


    def is_enneadtab_command(self, command):
        if command.name and command.extension == "ENNEAD":
            if command.tooltip:
                tooltips = command.tooltip.lower()
                if "legacy" in tooltips or "not in use" in tooltips:
                    return False
            return True
        return False

    def is_native_command(self, command):
        if command.name and command.extension == "ENNEAD":
            if command.tooltip:
                tooltips = command.tooltip.lower()
                if "legacy" in tooltips or "not in use" in tooltips:
                    return False
            return True
        return False

    @ERROR_HANDLE.try_catch_error()
    def load_commands(self):
        """
        enneadtab_commands = dict()
        for command in sessionmgr.find_all_available_commands():
            if command.name and command.extension == "ENNEAD":
                enneadtab_commands[command.name] = command

                #print command.name
                if "search" in command.name.lower():
                    for x in dir(command):
                        try:
                            print("{} = {}".format(x, getattr(command, x)))
                        except Exception as e:
                            print (e)
                #print cmd.extension
        """


        #print dir(cmd)





        # build the search database
        self.search_datas = dict()

        if self.checkbox_enneadtab.IsChecked:
            from pyrevit.loader import sessionmgr
            for command in filter(self.is_enneadtab_command, sessionmgr.find_all_available_commands()):
                title, doc_string, script_path, youtube_link, post_link = self.get_command_title_and_docstring_and_panel_location(command)
                self.search_datas[title] = (doc_string, script_path, youtube_link, post_link)
        """
            if "version note" in command.name.lower():
                for x in dir(command):
                    try:
                        print("\n{} = {}".format(x, getattr(command, x)))
                    except Exception as e:
                        print (e)
        """

        if self.checkbox_native.IsChecked:
            from pyrevit import HOST_APP
            native_commands_dict = {x.name: x for x in HOST_APP.get_postable_commands()}
            for native_command_name in native_commands_dict:
                self.search_datas[native_command_name] = ("Refer to Revit tooltips.", "", None, None)

        return

        for name, tooltip in self.search_datas.items():
            print("\n#######################")
            print(name)
            print(tooltip)



    def get_command_title_and_docstring_and_panel_location(self, command):
        from pyrevit import coreutils
        import pyrevit.extensions as py_extensions
        #panel_location = command.script.lower().split(".panel")[0].split(".tab\\")[1].capitalize()
        try:
            script_content = coreutils.ScriptFileParser(command.script)
        except:
            return command.name, command.tooltip, command.script, None, None
        #print script_content
        doc_string = script_content.get_docstring()
        custom_docstring = script_content.extract_param(py_extensions.DOCSTRING_PARAM)
        if custom_docstring:
            doc_string = custom_docstring

        final_title = command.name
        custom_title = script_content.extract_param("__title__")

        youtube_link = script_content.extract_param("__youtube__")
        post_link = script_content.extract_param("__post_link__")
        # if link is not None:
        #     print link

        if custom_title:
            final_title = custom_title


        #print panel_location
        return final_title.replace("\n", " "), doc_string, command.script, youtube_link, post_link



    #@TIME.timer
    @ERROR_HANDLE.try_catch_error()
    def update_results_display(self, fill_match = False):


        """Update search prompt results based on current input text."""
        self.is_x_imported("System", "update result deisplay begin")
        #import System
        # print "###############"
        # print "raw result = " + str(self._search_results)

        if not self._search_results:
            self.set_visibility_collapse(self.search_guess_textbox)

            return

        if self._result_index > len(self._search_results) - 1:
            self._result_index = 0
        if self._result_index < 0:
            self._result_index = len(self._search_results) - 1

        if self._result_index - 1 >= 0:
            opts_before = self._search_results[0:self._result_index]
        else:
            opts_before = []

        if self._result_index + 1 <= len(self._search_results) - 1:
            opts_after = self._search_results[self._result_index + 1:]
        else:
            opts_after = []


        self.set_visibility_visible(self.search_guess_textbox)
        self.search_guess_textbox.Text = self._search_results[self._result_index]
        doc_string, script_path, youtube_link, post_link = self.search_datas[self.search_guess_textbox.Text]
        panel_location = self.get_button_panel(script_path)
        self.doc_textblock.Text = "Button Name: [{}]\nButton Location: {}\n##############\n\n{}".format(self.search_guess_textbox.Text,
                                                                                                panel_location,
                                                                                                doc_string)
        self.set_visibility_visible(self.doc_display_panel)
        self.set_button_icon_display(script_path)

        # print link
        if youtube_link:
            self.set_visibility_visible(self.button_play_video)
            self.youtube_link = youtube_link
        else:
            self.set_visibility_collapse(self.button_play_video)

        # print link
        if post_link:
            self.set_visibility_visible(self.button_ei_post)
            self.post_link = post_link
        else:
            self.set_visibility_collapse(self.button_ei_post)


        max_display = 6
        if len(opts_before) > 0:
            self.set_visibility_visible(self.textblock_before)
            if len(opts_before) > max_display:
                actual_max = min(max_display, len(self._search_results))
                opts_before = ["..."] + opts_before[-actual_max:]
            self.textblock_before.Text = "\n".join(opts_before)


        else:
            self.set_visibility_collapse(self.textblock_before)


        if len(opts_after) > 0:
            self.set_visibility_visible(self.textblock_after)
            if len(opts_after) > max_display:
                actual_max = min(max_display, len(self._search_results))
                opts_after = opts_after[:actual_max] + ["..."]
            self.textblock_after.Text = "\n".join(opts_after)
        else:
            self.set_visibility_collapse(self.textblock_after)

        # print "before textblock text = " + self.textblock_before.Text
        # print "after textblock text = " + self.textblock_after.Text
        # print "opts before = " + str(opts_before)
        # print "opts after = " + str(opts_after)
        # print "raw result = " + str(self._search_results)
        # print "raw index = " + str(self._result_index)

        #print "ui updated"
    @ERROR_HANDLE.try_catch_error()
    def set_button_icon_display(self, script_path):
        import os
        if not os.path.exists(script_path):
            self.set_visibility_collapse(self.button_icon_display)
            return 'Native Revit'

        
        from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
        from EnneadTab import USER, ENVIRONMENT, SOUND, TIME, ERROR_HANDLE, FOLDER
        folder = FOLDER.get_folder_path_from_path(script_path)
        for file in FOLDER.get_filenames_in_folder(folder):
            if "icon.png" in file.lower():
                break
        icon_path = "{}\{}".format(folder, file)
        try:
            self.set_image_source(self.button_icon_display, icon_path)
            self.set_visibility_visible(self.button_icon_display)
        except:
            self.set_visibility_collapse(self.button_icon_display)


    def get_button_panel(self, script_path):
        import os
        if not os.path.exists(script_path):
            return 'This is a native Revit Command.'
        panel_location = script_path.lower().split(".panel")[0].split(".tab\\")[1].capitalize()

        note = ""
        if "tailor" in panel_location.lower():
            note += "\nNote that Tailor tools were designed for sepecific person/project. They might not work on every projetcs but can be tweaked to be generic tool. Talk to Sen Zhang if you want to bring certain functions to your project."
        return "<{}> Panel.{}".format( panel_location, note)


    def set_visibility_collapse(self, obj):
        #global WPF_COLLAPSED
        #obj.Visibility = WPF_COLLAPSED
        #return
        import System
        obj.Visibility = System.Windows.Visibility.Collapsed

    def set_visibility_visible(self, obj):
        #global WPF_VISIBLE
        #obj.Visibility = WPF_VISIBLE
        #return
        import System
        obj.Visibility = System.Windows.Visibility.Visible

    @ERROR_HANDLE.try_catch_error()
    def handle_keyboard_key(self, sender, args):    #pylint: disable=W0613
        """Handle keyboard input event."""
        self.is_x_imported("System", "handle keyboard input begin")
        from pyrevit.framework import Input
        import System
        
        from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
        from EnneadTab import USER, ENVIRONMENT, SOUND, TIME, ERROR_HANDLE, FOLDER
        # Escape: set response to none and close
        if args.Key == Input.Key.Escape:
            #self.Close()
            print("escape")
        # Enter: close, returns matched response automatically
        elif args.Key == Input.Key.Enter:
        #if self.search_guess_textbox.Text != '':
            self._setup_response()
            #args.Handled = True

        # Up, Down: Cycle through matches
        elif args.Key == Input.Key.Up:
            self._result_index -= 1
            self.update_results_display()
            self.search_textbox.Focus()
            #SOUND.play_sound("sound_effect_menu_page_trun_backward.wav")
        elif args.Key == Input.Key.Down:
            self._result_index += 1
            self.update_results_display()
            self.search_textbox.Focus()
            #SOUND.play_sound("sound_effect_menu_page_trun_forward.wav")

        self.debug_textbox.Text = "Index = {}".format(self._result_index + 1)

        return


    @ERROR_HANDLE.try_catch_error()
    def _setup_response(self):
        if self.search_guess_textbox.Text == '':
            return

        from pyrevit.loader import sessionmgr


        # response = self.search_guess_textbox.Text
        for command in filter(self.is_enneadtab_command, sessionmgr.find_all_available_commands()):
            title, doc_string, script_path, youtube_link, post_link = self.get_command_title_and_docstring_and_panel_location(command)
            #print title
            if title == self.search_guess_textbox.Text:
                selected_cmd = command
                self.run_command_action_event_handler.kwargs = selected_cmd, True
                self.ext_event.Raise()
                return


        from pyrevit import HOST_APP
        for native_command in HOST_APP.get_postable_commands():

            if native_command.name == self.search_guess_textbox.Text:
                #print native_command.name
                selected_cmd = native_command
                self.run_command_action_event_handler.kwargs = selected_cmd, False
                self.ext_event.Raise()













    #@TIME.timer
    def set_search_results(self, *collections):
        """Set search results for returning."""
        self._result_index = 0
        self._search_results = []


        for resultset in collections:
            self._search_results.extend(sorted(resultset))

        temp = []
        for x in self._search_results:
            if x not in temp:
                temp.append(x)
        self._search_results = temp

        if len(self._search_results) == 0:

            self.set_visibility_collapse(self.textblock_before)
            self.set_visibility_collapse(self.textblock_after)
            self.set_visibility_collapse(self.search_guess_textbox)
            self.set_visibility_collapse(self.doc_display_panel)


    #@TIME.timer
    def find_direct_match(self, input_text):
        """Find direct text matches in search term."""
        results = []
        if input_text:
            for command_name in self._search_data_keys:
                if command_name.lower().startswith(input_text):
                    results.append(command_name)

        return results

    #@TIME.timer
    def find_word_match(self, input_text):
        """Find direct word matches in search term."""
        results = []
        if input_text:
            cur_words = input_text.split(' ')
            for command_name in self._search_data_keys:
                if all([x in command_name.lower() for x in cur_words]):
                    results.append(command_name)

        return results

    #@TIME.timer
    def find_in_doc_match(self, input_text):
        """Find direct word matches in search term."""
        def has_keyword_in_doc(command_name, keywords):
            doc_string = self.search_datas[command_name][0]

            if not doc_string:
                return False

            for keyword in keywords:

                if keyword.lower() in doc_string.lower():
                    #print keyword
                    #print doc_string
                    return True
            return False

        results = []
        if input_text:
            cur_words = input_text.split(' ')
            for command_name in self._search_data_keys:
                if has_keyword_in_doc(command_name, cur_words):
                    results.append(command_name)

        return results


    @ERROR_HANDLE.try_catch_error()
    def search_box_value_changed(self, sender, args):
        """Handle text changed event."""

        self.is_x_imported("System", "searchbox text changed")



        #import System
        if len(self.entered_text) == 0:
            self.set_visibility_collapse(self.textblock_before)
            self.set_visibility_collapse(self.textblock_after)
            self.set_visibility_collapse(self.search_guess_textbox)
            self.set_visibility_collapse(self.doc_display_panel)
            return


        direct_match_results = self.find_direct_match(self.entered_text)

        word_results = self.find_word_match(self.entered_text)
        in_doc_results = self.find_in_doc_match(self.entered_text)
        self.set_search_results(direct_match_results, word_results, in_doc_results)

        #print self._search_results


        self.update_results_display()


    def activate_click(self, sender, args):
        self._setup_response()

    def checkbox_changed(self, sender, args):
        self.load_commands()
        self.search_box_value_changed(sender, args)

    def clear_click(self, sender, args):
        self.search_textbox.Text = ""
        self.search_textbox.Focus()

    def handleclick(self, sender, args):
        print ("surface clicked")

    def play_video_click(self, sender, args):
        import webbrowser
        try:
            webbrowser.open(self.youtube_link)
        except:
            print("Cannot play video.")

    @ERROR_HANDLE.try_catch_error()
    def main_expander_changed(self, sender, args):
        if self.main_expander.IsExpanded:
            self.main_expander.Header = "Minimize"
            self.main_border.CornerRadius = System.Windows.CornerRadius(12,25,25,25)
        else:
            self.main_expander.Header = "EnneadTab Search Command "
            self.main_border.CornerRadius = System.Windows.CornerRadius(12)

    def show_post_click(self, sender, args):
        import webbrowser
        try:
            webbrowser.open(self.post_link)
        except:
            print("Cannot show post.")

    def close_click(self, sender, args):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()

    def got_focus(self, sender, args):
        return
        self.back_pane.Opacity = 0.2

    def lose_focus(self, sender, args):
        return
        self.back_pane.Opacity = 0.2

    def is_x_imported(self, x, mark = "xx"):
        return
        import sys
        for module_name in sys.modules:
            if x == module_name:
                print("+++++++++++<{}> is imported at line {}".format(x, mark))
                return
        print("--------------<{}> is NOT imported at line {}".format(x, mark))


@ERROR_HANDLE.try_catch_error()
def main():
    #print_dir(__file__)


    modeless_form = EA_search_UI()

def list_imported_modules():
    print("Currently imported modules:")
    for module_name in sys.modules:
        print(module_name)







def print_dir(x):
    for attr in dir(x):
        print("{} = {}".format(attr, getattr(x, attr)))
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # if not USER.IS_DEVELOPER:
    #     REVIT_FORMS.notification(main_text = "This is a work in progress tool.")
    main()
    
