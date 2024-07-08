
__title__ = "ExternalTrimmer"
__doc__ = "This button does ExternalTrimmer when left click"

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
from scriptcontext import doc
import sys
sys.path.append("..\lib")

from EnneadTab import EXE, NOTIFICATION, FOLDER
from EnneadTab import LOG, ERROR_HANDLE

BLOCK_NAME = "EA_EXTERNAL_LINK"




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def update_or_insert_external_link(block_name):

    if not rs.IsBlock(block_name):
        insert_block(block_name)
        return

    update_link(block_name)
    if not rs.IsBlockInUse(block_name):
        rs.InsertBlock(block_name, (0,0,0))
        return


    return


def insert_block(block_name):

    external_block_filepath = get_external_filepath()

    dummyInitialObjects = [Rhino.Geometry.Point(Rhino.Geometry.Plane.WorldXY.Origin)]
    dummyInitialAttributes = [Rhino.DocObjects.ObjectAttributes()]
    indexOfAddedBlock = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.Add(block_name,
                                                                        "",
                                                                        Rhino.Geometry.Plane.WorldXY.Origin,
                                                                        dummyInitialObjects ,
                                                                        dummyInitialAttributes)


    modified = Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.ModifySourceArchive(indexOfAddedBlock,
                                                                                Rhino.FileIO.FileReference.CreateFromFullPath(external_block_filepath),
                                                                                Rhino.DocObjects.InstanceDefinitionUpdateType.	Linked,
                                                                                True)# bool for quite mode, no error msg shown
    Rhino.RhinoDoc.ActiveDoc.Objects.AddInstanceObject(indexOfAddedBlock,Rhino.Geometry.Transform.Identity)

def update_link(block_name):
    for name in rs.BlockNames():
        #print name
        if block_name not in name:
            continue
        definition = doc.InstanceDefinitions.Find(name)
        #print definition
        try:
            Rhino.RhinoDoc.ActiveDoc.InstanceDefinitions.RefreshLinkedBlock (definition)
        except:
            pass

def get_external_filepath():
    EA_export_folder = FOLDER.get_EA_local_dump_folder()
    if doc.Name is None:
        doc_name = "Untitled"
    else:
        doc_name = doc.Name.replace(".3dm", "")
    doc_name = "EA_EXTERNAL TRIMMER_" + doc_name
    extension = "3dm"
    filepath = "{}\{}.{}".format(EA_export_folder, doc_name, extension)
    return filepath


def process_link():

    filepath = get_external_filepath()


    # read file
    read_options = Rhino.FileIO.FileReadOptions()
    #read_options.InsertMode = False
    #read_options.NewMode = False
    #read_options.ImportMode = False
    read_options.OpenMode = True
    external_doc = Rhino.RhinoDoc.ReadFile(filepath, read_options)



    # explode all blocks

    # for objs outside EA_TRIMMER layer, bool off trimmer

    # save
    pass



def process_and_export_selected():
    # copy selection to trash objs
    temp_trash_objs = rs.CopyObjects(rs.SelectedObjects())

    # explode blocks in trash objs, extend list
    trash_objs = []
    for obj in temp_trash_objs:
        if rs.IsBlockInstance(obj):
            temp = rs.ExplodeBlockInstance(obj, explode_nested_instances = True)
            trash_objs.extend(temp)
            continue
        trash_objs.append(obj)

    # for objs outside EA_TRIMMER layer, bool off trimmer
    action_objs = filter(lambda x: rs.ObjectLayer(x) != "EA_TRIMMER", trash_objs)
    trimmers = filter(lambda x: rs.ObjectLayer(x) == "EA_TRIMMER", trash_objs)
    print(len(action_objs))

    #rs.Command(" -BooleanDifference {} _Enter {} _Enter ".format(action_objs, trimmers))
    #final_objs = rs.LastCreatedObjects()

    #final_objs = rs.BooleanDifference(action_objs, trimmers, delete_input = True)

    final_objs = []
    for x in action_objs:
        try:
            layer = rs.ObjectLayer(x)
            temp_objs = rs.BooleanDifference(x, trimmers, delete_input = False)
            rs.ObjectLayer(temp_objs, layer = layer)
            final_objs.extend(temp_objs)
        except:
            final_objs.append(x)


    # select and export
    rs.UnselectAllObjects()
    rs.SelectObjects(final_objs)
    filepath = get_external_filepath()
    doc.ExportSelected (filepath)

    # deletee trash objs
    rs.DeleteObjects(final_objs)
    rs.DeleteObjects(trash_objs)





def external_trimmer():
    print(doc.Name)
    if len(rs.SelectedObjects()) == 0:
        NOTIFICATION.toast(main_text = "Need to select at least one obj")
        return

    opts = ["Yes(for simple file)", "No(for complex file, trimming manually)"]
    result = rs.ListBox(opts, "Pre process? Objs will be trimmed by layer 'EA_TRIMMER'")
    print(result)

    if result == opts[0]:
        process_and_export_selected()
    else:
        filepath = get_external_filepath()
        doc.ExportSelected (filepath)
        EXE.open_file_in_default_application(filepath)
        NOTIFICATION.toast(main_text = "Opening External link file now.")

    #process_link()



    block_name = BLOCK_NAME
    update_or_insert_external_link(block_name)
    block = rs.BlockInstances(block_name)[0]


    rs.SelectObject(block)
    invert_objs = rs.InvertSelectedObjects(include_lights = True)
    rs.HideObjects(invert_objs)
    rs.UnselectObjects(block)
    rs.ShowObject(block)

    """
    file3dm = Rhino.FileIO.File3dm()
    file3md_options = Rhino.FileIO.File3dmWriteOptions()
    file3md_options.Version = 7


    for obj in doc.Objects:
        if obj.Id in rs.SelectedObjects():
            file3dm.Objects.Add(obj)
    file3dm.Write(filepath, file3md_options)
    print("Tool Done")
    """

if __name__ == "__main__":
    external_trimmer()