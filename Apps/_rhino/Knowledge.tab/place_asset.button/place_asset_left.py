
__alias__ = "PlaceAsset"
__doc__ = "This button does PlaceAsset when left click"


import sys
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs

from EnneadTab import FOLDER
import asset_UI as ui


def insert_ref_block(block_name, is_ref_block_method):
    if rs.IsBlock(block_name):
        rs.InsertBlock(block_name, (0,0,0))
        return

    external_block_filepath = get_external_filepath(block_name)

    dummyInitialObjects = [Rhino.Geometry.Point(Rhino.Geometry.Plane.WorldXY.Origin)]
    dummyInitialAttributes = [Rhino.DocObjects.ObjectAttributes()]
    indexOfAddedBlock = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Add(block_name,
                                                                        "",
                                                                        Rhino.Geometry.Plane.WorldXY.Origin,
                                                                        dummyInitialObjects ,
                                                                        dummyInitialAttributes)


    if is_ref_block_method:
        block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Linked

    else:
        block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.LinkedAndEmbedded
        #block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Static
        #block_method = Rhino.DocObjects.InstanceDefinitionUpdateType.Embedded

    modified = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.ModifySourceArchive(indexOfAddedBlock,
                                                                                Rhino.FileIO.FileReference.CreateFromFullPath(external_block_filepath),
                                                                                block_method,
                                                                                True)# bool for quite mode, no error msg shown
    obj = Rhino.RhinoDoc.ActiveDoc.Objects.AddInstanceObject(indexOfAddedBlock,Rhino.Geometry.Transform.Identity)

    if not is_ref_block_method:
        sys.path.append('L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Source Codes\\Blocks')
        import block_layer_packaging
        block_layer_packaging.pack_block_layers(blocks = [obj], flatten_layer = True)



        import imp
        MAKE_BLOCK_UNIQUE = imp.load_source('make block unique', 
                                            'L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Source Codes\\Blocks\\make block unique.py')

        MAKE_BLOCK_UNIQUE.make_block_unique(add_name_tag = False, original_blocks = [obj], treat_nesting = True)
        rs.DeleteBlock(block_name)
        rs.RenameBlock( "{}_new".format(block_name), block_name )



def get_external_filepath(block_name):

    folder = "L:\\4b_Applied Computing\\00_Asset Library"
    if folder in block_name:
        return block_name


    files = FOLDER.get_filenames_in_folder(folder)
    for file_name in files:
        if block_name in  file_name:
            return "{}\{}".format(folder, file_name)

def place_asset():
    folder = "L:\\4b_Applied Computing\\00_Asset Library"
    files = FOLDER.get_filenames_in_folder(folder)

    def is_good_file(name):
        if name.endswith(".3dm"):
            return True
        return False

    files = filter(is_good_file, files)


    block_names =  [("{}\{}".format(folder, file), file) for file in files]

    block_name, is_ref_block_method = ui.ShowImageSelectionDialog(block_names)

    if block_name is None or is_ref_block_method is None or block_name == []:
        return
    block_name = block_name[0]
    print("########", is_ref_block_method)
    insert_ref_block(block_name, is_ref_block_method)
