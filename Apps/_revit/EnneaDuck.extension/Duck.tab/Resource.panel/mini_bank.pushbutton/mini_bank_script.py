#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that check the Ennead Minibank record for user ranking and recent event."
__title__ = "MiniBank"
__context__ = "zero-doc"
__tip__ = True

from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #

import EnneadTab
import traceback

uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()
__persistentengine__ = True







# A simple WPF form used to call the ExternalEvent
class mini_bank_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        return


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def __init__(self):
        self.pre_actions()

        xaml_file_name = "mini_bank_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab MiniBank"

        self.sub_text.Text = "The moment of truth... Let's see your debts!"


        self.Title = "EnneadTab MiniBank UI"

        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        self.set_image_source(self.duck_img, "happy_duck.png")
        self.manual_click = 0


        self.Show()
        self.display_ranking()



    @EnneadTab.ERROR_HANDLE.try_catch_error
    def display_ranking(self):
        ENNEAD_LOG.print_leader_board()
        
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def bank_manager_Click(self, sender, e):
        if not EnneadTab.USER.is_SZ():
            EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "This function is only available to Sen Zhang.")
            return

        ENNEAD_LOG.manual_transaction()
    
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def check_account_click(self, sender, e):

        ENNEAD_LOG.print_history()
        
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def manual_coin_Click(self, sender, e):
        self.manual_click += 1
        

        if self.manual_click % 10 == 0:
            EnneadTab.NOTIFICATION.messenger(main_text = " +1UP\n经验+1")
            EnneadTab.SOUND.play_sound("sound_effect_mario_1up.wav")
            return
        EnneadTab.NOTIFICATION.messenger(main_text = " +$1\n金钱+1")
        EnneadTab.SOUND.play_sound("sound_effect_mario_coin.wav")
    
    
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def clear_data_click(self, sender, e):
        ENNEAD_LOG.clear_user_data()
        EnneadTab.NOTIFICATION.messenger(main_text = "Data has been cleared.")
    
    @EnneadTab.ERROR_HANDLE.try_catch_error
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()
        self.update_maunal_coin()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


    def update_maunal_coin(self):
        my_name = ENNEAD_LOG.get_current_user_name()
        data = ENNEAD_LOG.get_data_by_name(my_name)
        current_money = data["money"]
        change = self.manual_click

        data["money"] += int(change)
        ENNEAD_LOG.set_data_by_name(my_name, data)



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:
        modeless_form = mini_bank_ModelessForm()
        
    except:
        print (traceback.format_exc())
