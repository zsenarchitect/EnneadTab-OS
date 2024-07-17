#!/usr/bin/python
# -*- coding: utf-8 -*-




def notification(title = "EnneadTab For Rhino",
                main_text = "sample header",
                sub_text = "",
                self_destruct = None,
                button_name = "Sure...",
                width = 500,
                height = 150):



    import _RHINO_FORMS_NOTIFICATION as FORMS_NTF
    return FORMS_NTF.show_NotificationDialog(title,
                                            main_text,
                                            sub_text,
                                            self_destruct,
                                            button_name,
                                            width,
                                            height)

def select_from_list(options,
                    title = "EnneadTab For Rhino",
                    message = "test message",
                    button_names = ["Select"],
                    width = 500,
                    height = 500,
                    multi_select = True):



    import _RHINO_FORMS_LIST_SELECTION as FORMS_L
    return FORMS_L.show_ListSelectionDialog(options,
                                            title,
                                            message,
                                            multi_select,
                                            button_names,
                                            width,
                                            height)




def select_from_list2list(options_A,
                        options_B,
                        title = "EnneadTab For Rhino",
                        message = "",
                        search_A_text = "search AAA",
                        search_B_text = "search BBB",
                        multi_select_A = True,
                        multi_select_B = True,
                        button_names = ["Select"],
                        width = 300,
                        height = 200):



    import _RHINO_FORMS_LIST2LIST_SELECTION as FORMS_L2L
    return FORMS_L2L.ShowList2ListSelectionDialog(options_A,
                                                options_B,
                                                title,
                                                message,
                                                search_A_text,
                                                search_B_text,
                                                multi_select_A,
                                                multi_select_B,
                                                button_names,
                                                width,
                                                height)
