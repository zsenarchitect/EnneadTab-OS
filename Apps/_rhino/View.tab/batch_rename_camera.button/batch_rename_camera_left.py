
__title__ = "BatchRenameCamera"
__doc__ = "Rename multiple cameras without activating them."

import Rhino # pyright: ignore
import Eto # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

from EnneadTab import SOUND
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_UI

class rename_dialog(Eto.Forms.Dialog[bool]):

    # Initializer
    def __init__(self):
        # Initialize dialog box
        self.Title = 'Ennead Camera Batch Rename'
        self.Padding = Eto.Drawing.Padding(5)
        #self.Resizable = True
        #self.Height = 500
        self.Width = 600




        # the bm of forms buttoms
        button_layout = Eto.Forms.TableLayout()
        button_layout.Spacing = Eto.Drawing.Size(5, 5)


        button_layout.Rows.Add(Eto.Forms.TableRow(None, self.create_update_names_button(), self.CloseButton()))


        # helper text
        self.m_label = Eto.Forms.Label(Text = 'Double click to rename new name.')


        # datagrid view
        self.m_gridview = Eto.Forms.GridView()
        self.m_gridview.ShowCellBorders = True
        self.m_gridview.ShowHeader = True
        self.m_gridview.Height = 600
        self.m_gridview.CellDoubleClick += self.OnDblClickCell
        #self.m_gridview.DataStore = [['current name1', 'new name1'],['current name1', 'new name1']]
        view_names = rs.NamedViews()
        self.m_gridview.DataStore = [[x, x] for x in view_names]

        column_headers = ["Current Name", "New Name"]
        for i, header in enumerate(column_headers):
            column = Eto.Forms.GridColumn()
            column.Width = self.Width/2 * 0.9
            column.HeaderText = header
            column.Editable = True if "new" in header.lower() else False
            column.DataCell = Eto.Forms.TextBoxCell(i)
            self.m_gridview.Columns.Add(column)



        # Create main layout
        layout = Eto.Forms.StackLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = 5
        layout.HorizontalContentAlignment = Eto.Forms.HorizontalAlignment.Stretch

        logo_layout = Eto.Forms.DynamicLayout()
        logo_layout.AddSeparateRow(None, self.CreateLogoImage())


        layout.Items.Add(logo_layout)
        layout.Items.Add(self.m_label)
        layout.Items.Add(self.m_gridview)

        layout.Items.Add(None)
        layout.Items.Add(button_layout)
        # Set the dialog content
        self.Content = layout
        
        RHINO_UI.apply_dark_style(self)




    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        return self.logo

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):

        self.Close(True)


    # Grid.CellDoubleClick event and method----> isolate and refresh viewport
    def OnDblClickCell(self, sender,e):
        pass


    # update button click handler
    def OnUpdateButtonClick(self, sender, e):
        """
        main body of update

        self.m_gridview.SelectedItems to access select item to update the viewport
        Grid.OnCellEdited event and method----> check blockname allowed
        Grid.CellDoubleClick event and method----> isolate and refresh viewport
        """
        #print 123
        #print rs.NamedViews()
        #print sc.doc.NamedViews
        #print "@@@"
        for data in self.m_gridview.DataStore:

            #print data
            old_name = data[0]
            new_name = str(data[1])
            if new_name == old_name:
                continue

            while True:
                if new_name not in rs.NamedViews():
                    break
                new_name += "_Name Conflict"


            """
            for view in sc.doc.NamedViews:
                if view.Name == old_name:
                    view.Name = new_name
                    break
            """
            sc.doc.NamedViews.Rename( old_name, new_name)


        self.Close(True)

    # Create button control
    def CloseButton(self):
        # Create the default button
        self.DefaultButton = Eto.Forms.Button(Text = 'Close')
        self.DefaultButton.Click += self.OnCloseButtonClick
        return self.DefaultButton

    def create_update_names_button(self):
        # Create the update button, change text and bind action
        self.update_button = Eto.Forms.Button(Text = 'Update Camera Names')
        self.update_button.Click += self.OnUpdateButtonClick
        return self.update_button








@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def batch_rename_camera():
    dlg = rename_dialog()
    dlg.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    SOUND.play_sound()


if __name__ == "__main__":
    batch_rename_camera()