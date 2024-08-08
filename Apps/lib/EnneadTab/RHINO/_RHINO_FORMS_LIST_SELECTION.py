try:
    import System # pyright: ignore
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs

    import Eto # pyright: ignore


    import scriptcontext as sc
    REF_CLASS = Eto.Forms.Dialog[bool]
except:
    REF_CLASS = object   
    
import os
import fnmatch

try:
    import RHINO_UI
except:
    pass

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import ERROR_HANDLE
import NOTIFICATION
import ENVIRONMENT


# make modal dialog
class ListSelectionDialog(REF_CLASS):
    # Initializer
    def __init__(self, options, title, message,  multi_select, button_names , width, height):
        # Eto initials
        self.Title = title
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = height
        self.width = width
        self.Multi_Select = multi_select
        self.Message = message
        self.Button_Names = button_names


        # fields
        #self.ScriptList = self.InitializeScriptList()
        self.ScriptList = options
        self.SearchedScriptList = self.ScriptList[::]


        # initialize layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        layout.AddSeparateRow(None, self.CreateLogoImage())

        # add message
        layout.BeginVertical()
        layout.AddRow(self.CreateMessageBar())
        layout.EndVertical()

        # add search
        layout.BeginVertical()
        layout.AddRow(*self.CreateSearchBar())
        layout.EndVertical()

        # add listBox
        layout.BeginVertical()
        layout.AddRow(self.CreateScriptListBox())
        layout.EndVertical()

        # add buttons
        layout.BeginVertical()
        layout.AddRow(*self.CreateButtons())
        layout.EndVertical()

        # set content
        self.Content = layout
        
        RHINO_UI.apply_dark_style(self)



    # collect data for list
    def InitializeScriptList(self):
        pass
        # return allDocLayers()
        #return sorted(allDocLayers)


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
    def CreateSearchBar(self):
        """
        Creates two controls for the search bar
        self.lbl_Search as a simple label
        self.tB_Search as a textBox to input search strings to
        """
        self.lbl_Search = Eto.Forms.Label()
        self.lbl_Search.Text = "Type Here to Search: "
        self.lbl_Search.VerticalAlignment = Eto.Forms.VerticalAlignment.Center

        self.tB_Search = Eto.Forms.TextBox()
        self.tB_Search.TextChanged += self.tB_Search_TextChanged

        return [self.lbl_Search, self.tB_Search]



    def CreateScriptListBox(self):
        # Create a multi selection box with grid view - this is similar to Rhino MultipleListBox
        self.lb = Eto.Forms.GridView()
        self.lb.ShowHeader = True
        self.lb.AllowMultipleSelection = self.Multi_Select
        self.lb.Height = self.height
        self.lb.AllowColumnReordering = True

        self.lb.DataStore = sorted(self.ScriptList)

        self.lb.SelectedRowsChanged += self.RowsChanged


        # Create Gridview Column
        column1 = Eto.Forms.GridColumn()
        column1.Editable = False
        column1.Width = self.width
        column1.DataCell = Eto.Forms.TextBoxCell(0)
        self.lb.Columns.Add(column1)

        self.lb.DataStore = self.SearchedScriptList

        return self.lb



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

        if self.Multi_Select:
            self.btn_select_all = Eto.Forms.Button()
            self.btn_select_all.Text = "Highligh All"
            self.btn_select_all.Click += self.btn_select_all_Clicked
            user_buttons.append(self.btn_select_all)

        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked

        user_buttons.extend([ None, self.btn_Cancel])
        return user_buttons



    # create a search function
    def Search(self, text):
        """
        Searches self.ScriptList with a given string
        Supports wildCards
        """
        if text == "":
            self.lb.DataStore = self.ScriptList
        else:
            #print self.ScriptList
            temp = [ [str(x[0])] for x in self.ScriptList]
            #print temp
            #print flatten(temp)
            #print fnmatch.filter(flatten(temp), "*" + text + "*")
            #print graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1)
            #print list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))

            self.SearchedScriptList = list(graft(fnmatch.filter(flatten(temp), "*" + text + "*"), 1))
            #print "######"
            #print self.SearchedScriptList

            #original method only work with pure list of string
            #self.SearchedScriptList = list(graft(fnmatch.filter(flatten(self.ScriptList), "*" + text + "*"), 1))
            self.lb.DataStore = self.SearchedScriptList


    # Gridview SelectedRows Changed Event
    def RowsChanged (self,sender,e):
        return self.lb.SelectedRows



    # function to run when call at button click
    def RunScript(self):
        # return selected items
        return self.lb.SelectedItems



    # event handler handling text input in ther search bar
    def tB_Search_TextChanged(self, sender, e):
        self.Search(self.tB_Search.Text)



    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error

        #print sender
        #print (e)
        #print self.lb.SelectedItems
        #print dir(self.lb)
        #print len(list(self.lb.SelectedItems))
        #print len(list(self.lb.SelectedRows))
        if len(list(self.lb.SelectedItems)) == 0:
            NOTIFICATION.messenger(main_text = "Need to select at least something")
            return
        self.Close(True)
        self.RunScript()


    # event handler handling clicking on the 'run' button
    def btn_select_all_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.lb.SelectAll()
        NOTIFICATION.messenger(main_text = "{} items slected".format(len(self.SearchedScriptList)))


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)


#@ERROR_HANDLE.try_catch_error()
def show_ListSelectionDialog(options,
                            title = "EnneadTab",
                            message = "",
                            multi_select = False,
                            button_names = ["Run"],
                            width = 300,
                            height = 200):


    # for reason not understood yet, value is not displayed in grid view if not contained by list, must convert list format: [1,2,3,"abc"] ----> [[1],[2],[3],["abd"]]
    formated_list = [[x] for x in options]
    """
    i = 0
    while i < len(docLayers):
        to_do.append(docLayers[i:i+1])
        i += 1
    """

    dlg = ListSelectionDialog(formated_list, title, message, multi_select, button_names, width, height)
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)

    if (rc):


        OUT = [x[0] for x in dlg.RunScript()]
        OUT.sort()
        #pickedLayers.append(dlg.RunScript())

        #print OUT
        if not multi_select:
            return OUT[0]
        return OUT

    else:
        print ("Dialog did not run")
        return None

