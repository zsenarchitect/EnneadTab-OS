
__title__ = "InspectEnscapeSetting"
__doc__ = "This button does InspectEnscapeSetting when left click"


import rhinoscriptsyntax as rs

import json
from EnneadTab import FOLDER

def inspect_setting_file(path):
    OUT = []
    with open(path) as f:
        data = json.load(f)
        
        #print(json.dumps(data, indent = 4, sort_keys = True))
        #print(json.dumps(data))
        for key in sorted(data.keys()):

            #print key
            if isinstance(data[key], int):
                #print data[key]
                OUT.append((key, data[key]))
                continue
            
            if len(data[key].values()) == 0 :
                OUT.append((key, "???"))
                continue
            
            for inner_key in sorted(data[key].keys()):
                #print inner_key
                #print data[key][inner_key]["Value"]
                OUT.append((inner_key, data[key][inner_key]["Value"]))

    return OUT



def inspect_enscape_setting():
  
    path_1 = r"I:\2135\0_3D\00_3D Resources\Enscape\AXO DIAGRAM.json"
    path_2 = r"I:\2135\0_3D\00_3D Resources\Enscape\Columbia Audubon_edit.json"
    detail_1 = inspect_setting_file(path_1)
    detail_2 = inspect_setting_file(path_2)
    
    file_collection = [[1,2,3], [1, "B", "C"], [1,22,33]]
    
    file_collection = [detail_1, detail_2]
    file_collection = list(rs.OpenFileNames(filter = "Enscape setting file|*.json"))
    detail_collection = [inspect_setting_file(x) for x in file_collection]
    file_names = [FOLDER.get_file_name_from_path(x).replace(".json", "") for x in file_collection]
    for i, temp in enumerate(detail_collection):
        #print "*" * 50
        if "???" in str(temp):
            rs.MessageBox("<{}> has some invalid or empty setting. You can check by open .json with notepad.".format(file_names[i]))
            return
    #print file_collection
    #return
    
    #print file_names
    #print "%" * 20
    #print detail_1
    #print "%" * 20
    #print zip(*file_collection)
    OUT = ""
    for item in zip(*detail_collection):
        
        if all(x == item[0] for x in item):
            continue
        print("\n\nThere are difference setting detected in <{}>".format(item[0][0]))
        OUT += "\n\nThere are difference setting detected in <{}>".format(item[0][0])
        for i, content in enumerate(item):
            
            print("[ " + file_names[i] + " ]: " + str(content))
            OUT += "\n\t\t[ {} ]: {}".format(file_names[i], content[1])
    
    rs.TextOut(OUT)