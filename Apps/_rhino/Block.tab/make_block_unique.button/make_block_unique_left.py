__alias__ = ["MakeBlockUnique",
             "MBU"]
__doc__ = "Make a block unique on spot. Each unique original block become new unique block."


import rhinoscriptsyntax as rs

from EnneadTab.RHINO import RHINO_OBJ_DATA
from EnneadTab import SOUNDS
from EnneadTab import NOTIFICATION

def make_block_unique(add_name_tag = True, original_blocks = None, treat_nesting = False):
    

    #will_explode_nesting = rs.ListBox(items = [True, False], 
    #                                   message =  "Explode nesting block?", 
    #                                   title = "Make Block Unique", 
    #                                    default = False)
    will_explode_nesting = False

    if not original_blocks:
        original_blocks = rs.GetObjects("Select block instances to make unique, all nesting blocks are kept", filter = 4096, preselect = True)
        if not original_blocks:
            return
    
    selected_block_names = list(set([rs.BlockInstanceName(x) for x in original_blocks]))
    if len(selected_block_names) != 1:
        rs.MessageBox("Need to select single block, or a few block of same defination.")
        return
    rs.EnableRedraw(False)
    
    play_sound()
    new_block_name = create_unique_block(original_blocks[0], will_explode_nesting, add_name_tag, treat_nesting)
    map(lambda x:replace_original_blocks(new_block_name, x), original_blocks)
    NOTIFICATION.messenger("New block created: {}".format(new_block_name), print_note = True)


def create_unique_block(orginal_block, will_explode_nesting, add_name_tag, treat_nesting):
    old_block_name = rs.BlockInstanceName(orginal_block)

    user_new_block_name = rs.StringBox("What is the new name of the block after making unique?",
                                  default_value = old_block_name + "_new",
                                  title = "EnneadTab Make Block Unique")
    if user_new_block_name in rs.BlockNames():
        new_block_name = old_block_name + "_new"
        while True:
            if new_block_name not in rs.BlockNames():
                break
            new_block_name += "_new"
        NOTIFICATION.messenger("The name you entered <{}> already exist in this file.\nWill use <{}> instead.".format(user_new_block_name, new_block_name))
    else:
        new_block_name = user_new_block_name




    temp_block = rs.InsertBlock(old_block_name, (0,0,0))
    bounding_box_center = RHINO_OBJ_DATA.get_center(temp_block)
    temp_objs = rs.ExplodeBlockInstance(temp_block, explode_nested_instances = will_explode_nesting)

    if treat_nesting:
        temp_new_contents = []
        for content_obj in temp_objs:
            #### dont unique same obj twice!!!!!!!
            if rs.IsBlockInstance(content_obj):
                temp_new_name = create_unique_block(content_obj, will_explode_nesting, add_name_tag, treat_nesting)
                temp_new_contents.append(replace_original_blocks(temp_new_name, content_obj))
            else:
                temp_new_contents.append(content_obj)
        temp_objs = temp_new_contents



    block_contents = list(temp_objs)
    if add_name_tag:
        dot_text = new_block_name
        dot = rs.AddTextDot(dot_text, bounding_box_center)
        block_contents.append(dot)
    new_block_name = rs.AddBlock(block_contents, (0,0,0), name = new_block_name, delete_input = True)
    return new_block_name



def replace_original_blocks(new_block_name, original_block):
    transform = rs.BlockInstanceXform(original_block)
    layer = rs.ObjectLayer(original_block)
    new_block = rs.InsertBlock2(new_block_name, transform)
    rs.ObjectLayer(new_block, layer = layer)
    rs.DeleteObject(original_block)
    return new_block

def play_sound():

    file = "sound effect_popup msg1.wav"
    SOUNDS.play_sound(file)