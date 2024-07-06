
__alias__ = "ChangeObjectDisplaySource"
__doc__ = "This button does ChangeObjectDisplaySource when left click"


import rhinoscriptsyntax as rs
import scriptcontext as sc

class ChangeObjectDisplaySource:
    def change_objs_display(self, objs):
        if self.is_color_by_layer:
            rs.ObjectColorSource(objs, source = 0)
        if self.is_material_by_layer:
            rs.ObjectMaterialSource(objs, source = 0)


    def update_block_display(self, block_name):
        block_definition = sc.doc.InstanceDefinitions.Find(block_name)
        objs = block_definition.GetObjects()
        self.change_objs_display(objs)


    def change_source(self):
        option_list = [["Make all object color defined by layer", True], ["Make all object material defined by layer", True]]
        res = rs.CheckListBox(items = option_list,
                                message= "This will affect all objects in the file!\nThis will also affect contents inside blocks",
                                title="Duckitect")
        if not res:
            return
        for option, state in res:
            if option == option_list[0][0]:
                self.is_color_by_layer = state
            if option == option_list[1][0]:
                self.is_material_by_layer = state

        # change for general obj display
        objs = rs.AllObjects()
        self.change_objs_display(objs)

        #change for objs inside blocks
        block_names = rs.BlockNames(sort = True)
        map(self.update_block_display, block_names)


def change_object_display_source():
    ChangeObjectDisplaySource().change_source()

