#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time


try:
    from pyrevit.forms import WPFWindow
    import REVIT_EVENT
except:
    WPFWindow = object
    # or globals()["WPFWindow"] = object # this is to trick that class can be used

import ERROR_HANDLE
import ENVIRONMENT
import NOTIFICATION
import IMAGE
import DATA_FILE



class EnneadTabModeForm():
    """This form will pause revit and wait for action to continoue
    overload with more function method depanden t on your targetr."""
    pass








# A simple WPF form used to call the ExternalEvent
class EnneadTabModelessForm(WPFWindow):
    """
    this form will NOT revit, it cannot return value directly
    overload with more function depend on what you are loading

example:
    class MainSetting(REVIT_FORMS.EnneadTabModelessForm):
        def __init__(self, title, summary, xaml_file_name, **kwargs):
            super(MainSetting, self).__init__(title, summary, xaml_file_name, **kwargs)
            # call supper first so can connect to xaml to get all compenent, 
            # otherwise the load setting will have nothing to load

            self.Height = 800
            self.load_setting()

    """

    def pre_actions(self, *external_funcs):
        self.event_runner = REVIT_EVENT.ExternalEventRunner(*external_funcs)

        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        # self.rename_view_event_handler = SimpleEventHandler(rename_views)
        # self.ext_event_rename_view = ExternalEvent.Create(self.rename_view_event_handler)

    def __init__(self, title, summary, xaml_file_name, **kwargs):
        external_funcs = kwargs.get('external_funcs', [])
        self.pre_actions(*external_funcs)


        #xaml_file_name = "general_renamer_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        # to-do: this is not very efficient,,,, consider store a lookup tab;e during startup
        for folder, _, file in os.walk(ENVIRONMENT.REVIT_FOLDER):
            if xaml_file_name in file:
                xaml_file_name = os.path.join(folder, xaml_file_name)
                break
        else:
            NOTIFICATION.messenger(main_text="Cannot find the xaml file....")
            return

        WPFWindow.__init__(self, xaml_file_name)
        
        self.title.Text = title
        self.Title = title
        if hasattr(self, "semmery"):
            self.summary.Text = summary

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
   
        self.Show()

        

    def load_setting(self, setting_file):
        data = DATA_FILE.get_data(setting_file)
        for key, value in data.items():
            ui_obj = getattr(self, key, None)
            if not ui_obj:
                continue
            if "checkbox" in key or "toggle_bt" in key or "radio_bt" in key:
                setattr(ui_obj, "IsChecked", value)
            if "textbox" in key:
                setattr(ui_obj, "Text", str(value))
        

    def save_setting(self, setting_file):
        with DATA_FILE.update_data(setting_file) as data:
            setting_list = self.get_all_xaml_component_names()
            
            for key in setting_list:
                ui_obj = getattr(self, key)
                if "checkbox" in key or "toggle_bt" in key or "radio_bt" in key:
                    data[key] = getattr(ui_obj, "IsChecked")
                if "textbox" in key:
                    data[key] = getattr(ui_obj, "Text")

                    
    def get_all_xaml_component_names(self):
        def contain_keyword(x):
            if "bt_" in x or "textbox" in x or "label" in x or "checkbox" in x or "toggle_bt" in x or "radio_bt" in x:
                return True
            return False
        return [x for x in self.__dict__ if contain_keyword(x)]


    def Sample_bt_Click(self, sender, e):
        return
        self.rename_view_event_handler.kwargs = sheets, is_default_format
        self.ext_event_rename_view.Raise()
        res = self.rename_view_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    def handle_click(self, sender, args):
        print ("surface clicked")
        
    def close_click(self, sender, e):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        sender.DragMove()


# A simple WPF form used to call the ExternalEvent
class NotificationModelessForm(EnneadTabModelessForm):
    """
    Simple modeless form sample
    """

    def __init__(self,
                main_text,
                sub_text,
                button_name,
                window_title,
                self_destruct,
                window_width,
                window_height):


        xmal_template = "{}\\REVIT\\REVIT_FORMS_NOTIFICATION.xaml".format(ENVIRONMENT.CORE_FOLDER)
        WPFWindow.__init__(self, xmal_template)
        self.title_text.Text = main_text
        self.simple_text.Text = sub_text
        self.primary_button.Content = button_name
        self.foot_text.Text = ""
        self.Title = window_title
        self.Height = window_height
        self.Width = window_width

        self.Show()


        if self_destruct > 0:
            self.timer(self_destruct)


    def primary_button_click(self, sender, e):
        self.Close()


    def timer(self, life_span):
        #print "inside closer"

        deco_1 = "<"
        deco_2 = ">"
        segement = 5
        for i in range(life_span * segement,0,-1):

            if i % segement != 0:
                self.primary_button.Content = deco_1 + self.primary_button.Content + deco_2
                try:
                    print ("")
                except Exception as e:
                    pass
                    #print_note(e)
            else:
                self.primary_button.Content = self.primary_button.Content.replace(deco_1, "").replace(deco_2, "")
                try:
                    print( i / segement)
                except Exception as e:
                    pass
                    #print_note(e)
            self.foot_text.Text = "Window will close in {} seconds".format(i / segement)
            time.sleep(1.0/segement)
        self.Close()



def notification(main_text = "",
                sub_text = "",
                window_title = "EnneadTab",
                button_name = "Close",
                self_destruct = 0,
                window_width = 500,
                window_height = 500):
    """simple window that do not take any resonse from user.

    Args:
        main_text (str, optional): _description_. Defaults to "".
        sub_text (str, optional): _description_. Defaults to "".
        window_title (str, optional): _description_. Defaults to "EnneadTab".
        button_name (str, optional): _description_. Defaults to "Close".
        self_destruct (int, optional): if value other than 0, will close after that many secs. Defaults to 0.
        window_width (int, optional): _description_. Defaults to 500.
        window_height (int, optional): _description_. Defaults to 500.
    """


    #xmal_template = remap_filepath_between_folder(xmal_template, new_folder_after_dot_extension = "lib")
    NotificationModelessForm(main_text,
                            sub_text,
                            button_name,
                            window_title,
                            self_destruct,
                            window_width,
                            window_height)


def dialogue( title = "EnneadTab",
            main_text = "main_text",
            sub_text = None,
            options = None,
            footer_link = "http://www.ennead.com",
            footer_text = "EnneadTab",
            use_progress_bar = False,
            expended_content = None,
            extra_check_box_text = None,
            verification_check_box_text = None,
            icon = "shield"):
    """    
    Basic windows that take up to 4 user selection option.
    
    extra check box appear before commands options
    verification_check_box_text appear after commands options
    is activaed, the result of dialogue will return a tuple of two values.

    options = [["opt 1","description long long long long"], ["opt 2"]]   if options is a string, then used as main text, but if it is a list of two strings, the second string will be used as description. In either case, the command link will return main text


    TaskDialogIconNone,	No icon.
    TaskDialogIconShield,	Shield icon.
    TaskDialogIconInformation,	Information icon.
    TaskDialogIconError,	Error icon.
    TaskDialogIconWarning, Warning icon

    Args:
        title (str, optional): _description_. Defaults to "EnneadTab".
        main_text (str, optional): _description_. Defaults to "main_text".
        sub_text (_type_, optional): _description_. Defaults to None.
        options (_type_, optional): _description_. Defaults to None.
        footer_link (str, optional): _description_. Defaults to "http://www.ennead.com".
        footer_text (str, optional): _description_. Defaults to "EnneadTab".
        use_progress_bar (bool, optional): _description_. Defaults to False.
        expended_content (_type_, optional): _description_. Defaults to None.
        extra_check_box_text (_type_, optional): _description_. Defaults to None.
        verification_check_box_text (_type_, optional): _description_. Defaults to None.
        icon (str, optional): _description_. Defaults to "shield".
    """
    


    def result_append_checkbox_result(res):
        try:
            extra_checkbox_status = main_dialog.WasExtraCheckBoxChecked ()
            return res, extra_checkbox_status #extra_checkbox_status:{}".format(extra_checkbox_status)
        except:
            pass
        try:
            verification_checkbox_status = main_dialog.WasVerificationChecked  ()

            return res , verification_checkbox_status #"#verification_checkbox_status:{}".format(verification_checkbox_status)
        except:
            pass
        return res



    from Autodesk.Revit import UI # pyright: ignore
    main_dialog = UI.TaskDialog(title)
    main_dialog.MainInstruction = main_text
    main_dialog.MainContent = sub_text
    main_dialog.TitleAutoPrefix = False
    if footer_link is not None:
        #https://www.ennead.com/
        #http://usa.autodesk.com/adsk/servlet/index?siteID=123112&id=2484975
        main_dialog.FooterText = "<a href=\"{} \">".format(footer_link) + "{}</a>".format(footer_text)
    else:
        main_dialog.FooterText = footer_text

    if extra_check_box_text is not None:
        main_dialog.ExtraCheckBoxText  = extra_check_box_text
    else:
        if verification_check_box_text is not None:
            main_dialog.VerificationText   = verification_check_box_text
    main_dialog.ExpandedContent  = expended_content

    from pyrevit.coreutils import get_enum_values

    if options:
        clinks = get_enum_values(UI.TaskDialogCommandLinkId)
        max_clinks = len(clinks)
        for idx, cmd in enumerate(options):
            if idx < max_clinks:
                if isinstance(cmd, list):
                    main_dialog.AddCommandLink(clinks[idx], cmd[0], cmd[1])
                else:
                    main_dialog.AddCommandLink(clinks[idx], cmd)

    if icon == "shield":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconShield
    elif icon == "warning":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconWarning
    elif icon == "error":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconError
    elif icon == "info":
        main_dialog.MainIcon = UI.TaskDialogIcon.TaskDialogIconInformation
    res = main_dialog.Show()


    if res == UI.TaskDialogResult.Close:
        res = "Close"
    if res == UI.TaskDialogResult.Cancel:
        res = "Cancel"


    if 'CommandLink' in str(res):
        tdresults = sorted([x for x in get_enum_values(UI.TaskDialogResult) if 'CommandLink' in str(x)])
        residx = tdresults.index(res)
        if isinstance(options[residx], list):
            res = options[residx][0]
        else:
            res = options[residx]


    return result_append_checkbox_result(res)

def result_item_result_clicked(sender, e, debug=False):
    """Callback for a result item click event."""
    if debug:
        print("Result clicked")  # using print_md here will break the script
    pass


def show_balloon(header, text, tooltip='', group='', is_favourite=False, is_new=False, timestamp=None, click_result=result_item_result_clicked):
    r"""Show ballon in the info center section.

    Args:
        header (str): Category section (Bold)
        text (str): Title section (Regular)
        tooltip (str): Tooltip
        group (str): Group
        is_favourite (bool): Add a blue star before header
        is_new (bool): Flag to new
        timestamp (str): Set timestamp
        click_result (def): Executed after a click event

    Examples:
        ```python
        from pyrevit import forms
        date = '2019-01-01 00:00:00'
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        forms.show_balloon("my header", "Lorem ipsum", tooltip='tooltip',   group='group', is_favourite=True, is_new=True, timestamp = date, click_result = forms.result_item_result_clicked)
        ```
    """
    result_item = Autodesk.Internal.InfoCenter.ResultItem() # pyright: ignore
    result_item.Category = header
    result_item.Title = text
    result_item.TooltipText = tooltip
    result_item.Group = group
    result_item.IsFavorite = is_favourite
    result_item.IsNew = is_new
    if timestamp:
        result_item.Timestamp = timestamp
    result_item.ResultClicked += click_result
    balloon = Autodesk.Windows.ComponentManager.InfoCenterPaletteManager.ShowBalloon(result_item) # pyright: ignore
    return balloon



