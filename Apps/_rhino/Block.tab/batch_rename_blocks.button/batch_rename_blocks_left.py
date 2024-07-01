
__alias__ = "BatchRenameBlocks"
__doc__ = "Rename Block Names In a table"


import rhinoscriptsyntax as rs
from scriptcontext import doc
import Eto # pyright: ignore
import Rhino # pyright: ignore

from EnneadTab import SOUNDS, NOTIFICATION
from EnneadTab.RHINO import RHINO_UI

def batch_rename_blocks():
    dlg = rename_dialog()
    dlg.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    SOUNDS.play_sound()







class rename_dialog(Eto.Forms.Dialog[bool]):

    # Initializer
    def __init__(self):
        # Initialize dialog box
        self.Title = 'Ennead Block Batch Rename'
        self.Padding = Eto.Drawing.Padding(5)
        #self.Resizable = True
        #self.Height = 500
        self.Width = 1000
        self.pre_hidden_objs = rs.HiddenObjects()
        # Create viewport controls

        self.viewport = Rhino.UI.Controls.ViewportControl(Size = Eto.Drawing.Size(1000, 500))



        """
        if isolate object, then this viewport will zoom exltent around, make it more usefule.
        """

        # the bm of forms buttoms
        button_layout = Eto.Forms.TableLayout()
        button_layout.Spacing = Eto.Drawing.Size(5, 5)
        button_layout.Rows.Add(Eto.Forms.TableRow(None, self.update_names(), self.CloseButton()))


        # helper text
        self.m_label = Eto.Forms.Label(Text = 'Right mouse to orbit, left mouse to pan, middle wheel to change camera lens.\nDouble click on the item to isolate block.\n\nEdit the desired new name for blocks and click "Update Names"')


        # datagrid view
        self.m_gridview = Eto.Forms.GridView()
        self.m_gridview.ShowCellBorders = True
        self.m_gridview.ShowHeader = True
        self.m_gridview.Height = 200
        self.m_gridview.CellDoubleClick += self.OnDblClickCell
        #self.m_gridview.DataStore = [['current name1', 'new name1'],['current name1', 'new name1']]
        block_names = rs.BlockNames(sort = True)
        self.m_gridview.DataStore = [[x, x] for x in block_names]

        column_headers = ["Current Name", "New Name"]
        for i, header in enumerate(column_headers):
            column = Eto.Forms.GridColumn()
            column.HeaderText = header
            column.Width = self.Width/2 * 0.95
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

        layout.Items.Add(self.viewport)
        layout.Items.Add(self.m_label)
        layout.Items.Add(self.m_gridview)

        layout.Items.Add(None)
        layout.Items.Add(button_layout)
        # Set the dialog content
        self.Content = layout
        
        RHINO_UI.apply_dark_style(self)


    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,30)
        return self.logo


    def pre_closing_check(self):

        #clean_temp_blocks
        temp_blocks = rs.ObjectsByName("EA_temp_block")
        if len(temp_blocks) != 0:
            rs.DeleteObjects(temp_blocks)


        #resotre hidden obj stage
        rs.ShowObjects(rs.HiddenObjects())
        rs.HideObjects(self.pre_hidden_objs)

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.pre_closing_check()
        self.Close(True)


    # Grid.CellDoubleClick event and method----> isolate and refresh viewport
    def OnDblClickCell(self, sender,e):
        """
        isolate the block, update viewport
        """
        #print 999999999999999999
        cell = list(self.m_gridview.SelectedItems)[0]
        #print cell
        current_name = cell[0]
        #print current_name
        instances = rs.BlockInstances(current_name)

        non_exist = False
        if len(instances) == 0:
            instance = rs.InsertBlock(current_name, (0,0,0))
            rs.ObjectName(instance, name = "EA_temp_block")
            non_exist = True
        else:
            instance = instances[0]


        rs.ShowObject(instance)
        rs.UnselectAllObjects()
        rs.SelectObject(instance)
        invert_objs = rs.InvertSelectedObjects()
        rs.HideObjects(invert_objs)
        rs.ZoomExtents()



        #self.viewport = Rhino.UI.Controls.ViewportControl(Size = Eto.Drawing.Size(500, 500))
        self.viewport.Refresh()
        #print "refresh"
        self.viewport.Size = Eto.Drawing.Size(500, 500)
        #print "change size"
        new_viewport = Rhino.UI.Controls.ViewportControl(Size = Eto.Drawing.Size(500, 500))
        #print self.Content.Items
        self.Content.Items[1] = new_viewport


    # update button click handler
    def OnUpdateButtonClick(self, sender, e):
        """
        main body of update

        self.m_gridview.SelectedItems to access select item to update the viewport
        Grid.OnCellEdited event and method----> check blockname allowed
        Grid.CellDoubleClick event and method----> isolate and refresh viewport
        """
        #print 123
        for data in self.m_gridview.DataStore:

            #print data
            new_name = data[1]
            if new_name == data[0]:
                continue

            while True:
                if new_name not in rs.BlockNames():
                    break
                new_name += "_Name Conflict"

            rs.RenameBlock( data[0], new_name )

        self.pre_closing_check()
        self.Close(True)

    # Create button control
    def CloseButton(self):
        # Create the default button
        self.DefaultButton = Eto.Forms.Button(Text = 'Close')
        self.DefaultButton.Click += self.OnCloseButtonClick
        return self.DefaultButton

    def update_names(self):
        # Create the update button, change text and bind action
        self.update_button = Eto.Forms.Button(Text = 'Update Block Names')
        self.update_button.Click += self.OnUpdateButtonClick
        return self.update_button



