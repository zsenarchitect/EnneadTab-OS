try:
    import System # pyright: ignore
    import Rhino # pyright: ignore

    import rhinoscriptsyntax as rs

    import Eto # pyright: ignore
    import scriptcontext as sc
    REF_CLASS = Eto.Forms.Dialog[bool]
except:
    REF_CLASS = object   

try:
    import RHINO_UI
except :
    pass



import os
import fnmatch

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations

# make modal dialog
class List2ListSelectionDialog(REF_CLASS):
    # Initializer
    def __init__(self, options_A, options_B, title, message, search_A_text, search_B_text, multi_select_A, multi_select_B, button_names , width, height):
        # Eto initials
        self.Title = title
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        # self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = height
        self.width = width
        self.Multi_Select_A = multi_select_A
        self.Multi_Select_B = multi_select_B
        self.Message = message
        self.Button_Names = button_names
        self.search_A_text = search_A_text
        self.search_B_text = search_B_text


        # fields
        #self.ScriptList_A = self.InitializeScriptList()
        self.ScriptList_A = options_A
        self.SearchedScriptList_A = self.ScriptList_A[::]
        self.ScriptList_B = options_B
        self.SearchedScriptList_B = self.ScriptList_B[::]

        # initialize layout
        layout_A = Eto.Forms.DynamicLayout()
        layout_A.Padding = Eto.Drawing.Padding(5)
        layout_A.Spacing = Eto.Drawing.Size(5, 5)

        layout_A.BeginVertical()
        layout_A.AddRow(*self.CreateSearchBar_A())
        layout_A.EndVertical()

        # add listBox
        layout_A.BeginVertical()
        layout_A.AddRow(self.CreateScriptListBox_A())
        layout_A.EndVertical()
        if self.Multi_Select_A:
            layout_A.AddSeparateRow(*self.Create_Option_Buttons_A())

        layout_B = Eto.Forms.DynamicLayout()
        layout_B.Padding = Eto.Drawing.Padding(5)
        layout_B.Spacing = Eto.Drawing.Size(5, 5)

        layout_B.BeginVertical()
        layout_B.AddRow(*self.CreateSearchBar_B())
        layout_B.EndVertical()

        # add listBox
        layout_B.BeginVertical()
        layout_B.AddRow(self.CreateScriptListBox_B())
        layout_B.EndVertical()
        if self.Multi_Select_B:
            layout_B.AddSeparateRow(*self.Create_Option_Buttons_B())



        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        # add message
        layout.AddSeparateRow(None, self.CreateLogoImage())
        layout.BeginVertical()
        layout.AddRow(self.CreateMessageBar())
        layout.EndVertical()


        temp = Eto.Forms.Label()
        temp.Text = "-->"
        layout.BeginVertical()
        layout.AddRow(layout_A, temp, layout_B)
        layout.EndVertical()

        # add buttons
        layout.BeginVertical()
        layout.AddRow(*self.CreateButtons())
        layout.EndVertical()

        # set content
        self.Content = layout
        
        RHINO_UI.apply_dark_style(self)



    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()
        return self.logo

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = self.Message
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left

    # create search bar function
    def CreateSearchBar_A(self):
        """
        Creates two controls for the search bar
        self.lbl_Search_A as a simple label
        self.tB_Search_A as a textBox to input search strings to
        """
        self.lbl_Search_A = Eto.Forms.Label()
        self.lbl_Search_A.Text = "Type Here to {}: ".format(self.search_A_text)
        self.lbl_Search_A.VerticalAlignment = Eto.Forms.VerticalAlignment.Center

        self.tB_Search_A = Eto.Forms.TextBox()
        self.tB_Search_A.TextChanged += self.tB_Search_TextChanged_A

        return [self.lbl_Search_A, self.tB_Search_A]


    def CreateSearchBar_B(self):
        """
        Creates two controls for the search bar
        self.lbl_Search_B as a simple label
        self.tB_Search_B as a textBox to input search strings to
        """
        self.lbl_Search_B = Eto.Forms.Label()
        self.lbl_Search_B.Text = "Type Here to {}: ".format(self.search_B_text)
        self.lbl_Search_B.VerticalAlignment = Eto.Forms.VerticalAlignment.Center

        self.tB_Search_B = Eto.Forms.TextBox()
        self.tB_Search_B.TextChanged += self.tB_Search_TextChanged_B

        return [self.lbl_Search_B, self.tB_Search_B]


    def CreateScriptListBox_A(self):
        # Create a multi selection box with grid view - this is similar to Rhino MultipleListBox
        self.lb_A = Eto.Forms.GridView()
        self.lb_A.ShowHeader = True
        self.lb_A.AllowMultipleSelection = self.Multi_Select_A
        self.lb_A.Height = self.height
        self.lb_A.AllowColumnReordering = True

        self.lb_A.DataStore = [[False, x[0]] for x in sorted(self.ScriptList_A)]
        self.Record_A = dict()
        for x in self.ScriptList_A:
            self.Record_A[str(x[0])] = False
        #print sorted(self.ScriptList_B)
        #print self.lb_A.DataStore

        self.lb_A.SelectedRowsChanged += self.RowsChanged_A
        self.lb_A.CellClick  += self.event_cell_click_A

        # Create Gridview Column
        column0 = Eto.Forms.GridColumn()
        column0.Editable = True
        column0.Width = 20
        column0.DataCell = Eto.Forms.CheckBoxCell(0)
        self.lb_A.Columns.Add(column0)

        column1 = Eto.Forms.GridColumn()
        column1.Editable = False
        column1.Width = self.width
        column1.DataCell = Eto.Forms.TextBoxCell(1)
        self.lb_A.Columns.Add(column1)

        #self.lb_A.DataStore = self.SearchedScriptList_A

        return self.lb_A


    def CreateScriptListBox_B(self):
        # Create a multi selection box with grid view - this is similar to Rhino MultipleListBox
        self.lb_B = Eto.Forms.GridView()
        self.lb_B.ShowHeader = True
        self.lb_B.AllowMultipleSelection = self.Multi_Select_B
        self.lb_B.Height = self.height
        self.lb_B.AllowColumnReordering = True

        self.lb_B.DataStore = [[False, x[0]] for x in sorted(self.ScriptList_B)]
        self.Record_B = dict()
        for x in self.ScriptList_B:
            self.Record_B[str(x[0])] = False

        self.lb_B.SelectedRowsChanged += self.RowsChanged_B
        self.lb_B.CellClick  += self.event_cell_click_B


        # Create Gridview Column
        column0 = Eto.Forms.GridColumn()
        column0.Editable = True
        column0.Width = 20
        column0.DataCell = Eto.Forms.CheckBoxCell(0)
        self.lb_B.Columns.Add(column0)

        column1 = Eto.Forms.GridColumn()
        column1.Editable = False
        column1.Width = self.width
        column1.DataCell = Eto.Forms.TextBoxCell(1)
        self.lb_B.Columns.Add(column1)



        return self.lb_B



    def Create_Option_Buttons_A(self):

        buttons = []

        self.btn_check = Eto.Forms.Button()
        self.btn_check.Text = "Check Selected"
        self.btn_check.Click += self.btn_check_Clicked_A

        self.btn_uncheck = Eto.Forms.Button()
        self.btn_uncheck.Text = "UnCheck Selected"
        self.btn_uncheck.Click += self.btn_uncheck_Clicked_A

        buttons.extend([ None, self.btn_check, self.btn_uncheck])
        return buttons

    def Create_Option_Buttons_B(self):

        buttons = []

        self.btn_check = Eto.Forms.Button()
        self.btn_check.Text = "Check Selected"
        self.btn_check.Click += self.btn_check_Clicked_B

        self.btn_uncheck = Eto.Forms.Button()
        self.btn_uncheck.Text = "UnCheck Selected"
        self.btn_uncheck.Click += self.btn_uncheck_Clicked_B

        buttons.extend([ None, self.btn_check, self.btn_uncheck])
        return buttons



    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []
        for b_name in self.Button_Names:
            self.btn_Run = Eto.Forms.Button()
            self.btn_Run.Text = b_name
            self.btn_Run.Click += self.btn_Run_Clicked
            user_buttons.append(self.btn_Run)

        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked

        user_buttons.extend([ None, self.btn_Cancel])
        return user_buttons


    def update_ListBox_A_DataStore(self, source_list):
        self.lb_A.DataStore = [[self.Record_A[str(x[0])], x[0]] for x in sorted(source_list)]

    def update_ListBox_B_DataStore(self, source_list):
        self.lb_B.DataStore = [[self.Record_B[str(x[0])], x[0]] for x in sorted(source_list)]


    # create a search function
    def Search_A(self, text):
        """
        Searches self.ScriptList_A with a given string
        Supports wildCards
        """
        self.update_record_A()
        if text == "":
            #self.update_ListBox_A_DataStore(source_list = self.ScriptList_A)
            self.SearchedScriptList_A = self.ScriptList_A
        else:
            #print self.ScriptList_A
            temp = [ [str(x[0])] for x in self.ScriptList_A]
            #print "AAAAAA"
            #print self.ScriptList_A
            #print "BBBBBBB"
            #print temp

            #print flatten(temp)
            #print fnmatch.filter(flatten(temp), "*" + text + "*")
            #print graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1)
            #print list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            self.SearchedScriptList_A = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))
            #self.SearchedScriptList_A = fnmatch.filter(flatten(temp), "*" + text + "*")


            #print "*******"
            #print self.SearchedScriptList_A
            #[('Default',), ('Layer 01',), ('Layer 02',), ('Layer 03',), ('Layer 04',), ('Layer 05',)]

            #original method only work with pure list of string
            #self.SearchedScriptList_A = list(graft(fnmatch.filter(flatten(self.ScriptList_A), "*" + text + "*"), 1))

        self.update_ListBox_A_DataStore(source_list = self.SearchedScriptList_A)

    def Search_B(self, text):
        """
        Searches self.ScriptList_A with a given string
        Supports wildCards
        """
        self.update_record_B()
        if text == "":
            #self.update_ListBox_B_DataStore(source_list = self.ScriptList_B)
            self.SearchedScriptList_B = self.ScriptList_B
        else:
            #print self.ScriptList_B
            temp = [ [str(x[0])] for x in self.ScriptList_B]
            #print temp
            #print flatten(temp)
            #print fnmatch.filter(flatten(temp), "*" + text + "*")
            #print graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1)
            #print list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            self.SearchedScriptList_B = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            #original method only work with pure list of string
            #self.SearchedScriptList_A = list(graft(fnmatch.filter(flatten(self.ScriptList_A), "*" + text + "*"), 1))

        self.update_ListBox_B_DataStore(source_list = self.SearchedScriptList_B)



    # Gridview SelectedRows Changed Event
    def RowsChanged_A (self,sender,e):
        if self.Multi_Select_A:
            return self.lb_A.SelectedRows
        #self.lb_B.DataStore is only_assign_one_check_value------------------------------------


        if list(self.lb_A.SelectedItems) != []:
            self.update_record_A(reset = True)
            #print "$$$$$$$$$$$$$$$$$$$$$$$$$$"
            #print list(self.lb_A.SelectedItems)
            flag_checked , flag_entry = list(self.lb_A.SelectedItems)[0]
            self.Record_A[flag_entry] = flag_checked
            self.update_ListBox_A_DataStore(source_list = self.SearchedScriptList_A)
        return self.lb_A.SelectedRows

    def RowsChanged_B (self,sender,e):
        if self.Multi_Select_B:
            return self.lb_B.SelectedRows
        #self.lb_B.DataStore is only_assign_one_check_value------------------------------------


        if list(self.lb_B.SelectedItems) != []:
            self.update_record_B(reset = True)
            #print "$$$$$$$$$$$$$$$$$$$$$$$$$$"
            #print list(self.lb_B.SelectedItems)
            flag_checked , flag_entry = list(self.lb_B.SelectedItems)[0]
            self.Record_B[flag_entry] = flag_checked
            self.update_ListBox_B_DataStore(source_list = self.SearchedScriptList_B)
        return self.lb_B.SelectedRows

    def event_cell_click_A(self, sender, e):
        return
        if list(self.lb_A.SelectedItems) == []:
            return
        if e.Column == 0:
            print ("column 0")
            for checked , entry in list(self.lb_A.SelectedItems):
                self.Record_A[entry] = not list(self.lb_A.SelectedItems)[0]
            self.update_ListBox_A_DataStore(source_list = self.SearchedScriptList_A)
        pass

    def event_cell_click_B(self, sender, e):
        return
        if list(self.lb_B.SelectedItems) == []:
            return
        pass

    def update_record_A(self, reset = False):

        #print list(self.lb_A.DataStore)
        if list(self.lb_A.DataStore) != []:
            for checked , entry in list(self.lb_A.DataStore):
                #print checked , entry
                if reset:
                    self.Record_A[str(entry)] = False
                else:
                    self.Record_A[str(entry)] = checked


    def update_record_B(self, reset = False):

        #print list(self.lb_B.DataStore)
        if list(self.lb_B.DataStore) != []:
            for checked , entry in list(self.lb_B.DataStore):
                #print checked , entry
                if reset:
                    self.Record_B[str(entry)] = False
                else:
                    self.Record_B[str(entry)] = checked


    # function to run when call at button click
    def RunScript(self):
        # return selected items
        """
        for A, change to all cheked item only
        """
        #print self.lb_A.DataStore
        OUT_A = filter(lambda x: x[0], self.lb_A.DataStore)
        OUT_B = filter(lambda x: x[0], self.lb_B.DataStore)
        return OUT_A, OUT_B



    # event handler handling text input in ther search bar
    def tB_Search_TextChanged_A(self, sender, e):
        self.Search_A(self.tB_Search_A.Text)

    def tB_Search_TextChanged_B(self, sender, e):
        self.Search_B(self.tB_Search_B.Text)

    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.Close(True)
        self.RunScript()


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)




    def btn_check_Clicked_A(self, sender, e):
        self.unify_selection_A(target_boolean = True)


    def btn_check_Clicked_B(self, sender, e):
        self.unify_selection_B(target_boolean = True)



    def btn_uncheck_Clicked_A(self, sender, e):
        self.unify_selection_A(target_boolean = False)

    def btn_uncheck_Clicked_B(self, sender, e):
        self.unify_selection_B(target_boolean = False)


    def unify_selection_A(self, target_boolean = True):
        for checked , entry in list(self.lb_A.SelectedItems):
            self.Record_A[entry] = target_boolean
        self.update_ListBox_A_DataStore(source_list = self.SearchedScriptList_A)

    def unify_selection_B(self, target_boolean = True):
        for checked , entry in list(self.lb_B.SelectedItems):
            self.Record_B[entry] = target_boolean
        self.update_ListBox_B_DataStore(source_list = self.SearchedScriptList_B)


def ShowList2ListSelectionDialog(options_A,
                                options_B,
                                title = "EnneadTab",
                                message = "",
                                search_A_text = "search AAA",
                                search_B_text = "search BBB",
                                multi_select_A = True,
                                multi_select_B = True,
                                button_names = ["Run"],
                                width = 300,
                                height = 200):


    # for reason not understood yet, value is not displayed in grid view if not contained by list, must convert list format: [1,2,3,"abc"] ----> [[1],[2],[3],["abd"]]
    formated_list_A = [[x] for x in options_A]
    formated_list_B = [[x] for x in options_B]
    """
    i = 0
    while i < len(docLayers):
        to_do.append(docLayers[i:i+1])
        i += 1
    """
    print (formated_list_A)
    dlg = List2ListSelectionDialog(formated_list_A, formated_list_B, title, message,search_A_text, search_B_text, multi_select_A, multi_select_B, button_names, width, height)
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)

    if (rc):

        return_list_A, return_list_B = dlg.RunScript()
        OUT_A = [x[1] for x in return_list_A]
        OUT_A.sort()
        OUT_B = [x[1] for x in return_list_B]
        OUT_B.sort()
        #pickedLayers.append(dlg.RunScript())

        #print OUT
        if not multi_select_A and OUT_A != []:
            OUT_A = OUT_A[0]
        if not multi_select_B and OUT_B != []:
            OUT_B = OUT_B[0]
        print ("OUT_A = {}".format(OUT_A))
        print ("OUT_B = {}".format(OUT_B))
        return OUT_A, OUT_B

    else:
        print ("Dialog did not run")
        return None, None


def test():
    docLayers = rs.LayerNames()
    docLayers.extend([1, 2, 3, True])

    to_do = []
    i = 0
    while i < len(docLayers):
        to_do.append(docLayers[i:i+1])
        i += 1
    #ShowList2ListSelectionDialog(to_do)
    to_do = [[1],["add"],[3],[4]]

    try:
        res = ShowList2ListSelectionDialog(docLayers,
                                        docLayers,
                                        title = "new title",
                                        message = "test message",
                                        multi_select_A = True,
                                        multi_select_B = False,
                                        button_names = ["Test Me"],
                                        width = 300,
                                        height = 600)
        OUT_A, OUT_B = res
        print (OUT_A)
        print (OUT_B)
    except Exception as e:
        import traceback
        error =  traceback.format_exc()
        print (error)

        import NOTIFICATION
        NOTIFICATION.messenger(main_text = "error")
        filepath = r"C:\Users\szhang\Desktop\error.txt"
        import DATA_FILE
        DATA_FILE.save_list_to_txt([error], filepath, end_with_new_line = False)

##########################################################
if __name__ == "__main__":
    test()