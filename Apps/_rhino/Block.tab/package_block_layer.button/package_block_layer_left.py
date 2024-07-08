
__title__ = "PackageBlockLayer"
__doc__ = "Package blocks content layer under a single parent layer. This is very helpful if you want to test totally new material for the layers."

import rhinoscriptsyntax as rs

from EnneadTab import NOTIFICATION, LOG, ERROR_HANDLE


def process_block(block_name, flatten_layer = False):
    contents = rs.BlockObjects(block_name)
    key_word = "Block Package_"
    parent_layer = key_word + block_name

    for content in contents:
        if rs.IsBlockInstance(content):
            process_block(rs.BlockInstanceName(content), flatten_layer)
        current_layer = rs.ObjectLayer(content)
        if key_word in current_layer:
            layer_strings = current_layer.split("::")
            updated_strings = []
            for string in layer_strings:
                if key_word in string:
                    string = key_word + block_name
                updated_strings.append(string)
            updated_layer_name = "::".join(updated_strings)

            """
            print("_".join(["1", "q"]) ---> 1_q)
            print("_".join(["1"]) -----> 1)
            """


            new_layer = updated_layer_name

        else:
            #new_layer = rs.ParentLayer(current_layer, parent = parent_layer)
            new_layer = "{}::{}".format(parent_layer, current_layer)

        if flatten_layer:
            layer_strings = new_layer.split("::")
            new_layer = layer_strings[0] + "::" + layer_strings[-1]

        if not rs.IsLayer(new_layer):
            rs.AddLayer(new_layer)
        rs.ObjectLayer(content, layer = new_layer)
        rs.LayerColor(new_layer, color = rs.LayerColor(current_layer))
        rs.LayerMaterialIndex(new_layer, index = rs.LayerMaterialIndex(current_layer))
        rs.DeleteLayer(current_layer)
    rs.DeleteLayer(parent_layer)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def package_block_layer(blocks = None, flatten_layer = None):
    if blocks == None:
        blocks = rs.GetObjects(message = "pick blocks", custom_filter = rs.filter.instance)
        if not blocks:
            return
    if flatten_layer == None:
        flatten_layer = rs.ListBox(items = [True, False], message =  "Flatten block layers?", title = "Packaging block layers", default = True)


    rs.EnableRedraw(False)
    block_names = [rs.BlockInstanceName(x) for x in blocks]
    block_names = list(set(block_names))
    map(lambda x: process_block(x, flatten_layer), block_names)

    NOTIFICATION.messenger("The block(s) has been fully detached.")


if __name__ == "__main__":
    package_block_layer()