import os


import shutil
import xml.etree.ElementTree as ET
import xml.dom.minidom



from constants import SAMPLE_JSON_DATA_REAL, SAMPLE_JSON_DATA_SIMPLE
from constants import SPECIAL_KEYS, SPECIAL_LIST_KEY

def get_tree(parent_element, json_data):


    for key, value in json_data.items():
        if key in SPECIAL_KEYS:
       
            # Create the locale_1033 element
            local_tree = ET.Element(key)
            local_tree.text = json_data[key]

            # Append the locale_1033 element to the root
            parent_element.append(local_tree)
           
        elif key == SPECIAL_LIST_KEY:
            for i,item in enumerate(value):
                get_tree(parent_element, item)
            
        else:# handle other cases
   
            #this part make the index list for bitmap works better and macro_item list in macros
            if isinstance(value, list):
       
                child_element = ET.SubElement(parent_element, key)
                for i,item in enumerate(value):
                    # print (i, item)
                    # print (parent_element.tag, child_element.tag)
                    get_tree(child_element, item)
                
                
                
            elif isinstance(value, dict):
                child_element = ET.SubElement(parent_element, key)
                get_tree(child_element, value)
                    
            else:
                # print (key)
                parent_element.set(key.replace("@", ""), value)
    return parent_element



##################################################################################
def write_rui(json_data, final_file):
    


    # Create the root element
    root_element = ET.Element("RhinoUI")
    root_element = get_tree(root_element, json_data)




    # Output the XML to a file

    with open(final_file, "wb") as xml_file:
        # Get the string representation of the XML
        xml_string = ET.tostring(root_element, encoding="utf-8")
        # print (xml_string)

        # Use minidom to pretty print the XML string
        dom = xml.dom.minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="  ")  # You can adjust the indentation as needed

        # Write the pretty XML to the file
        xml_file.write(pretty_xml.encode("utf-8"))






############### this can work, noce! ###############


if __name__ == '__main__':

    main_data = SAMPLE_JSON_DATA_REAL# the web converted json will flatten some macro_item and bitmap_iteam objects,,,, so i try to recreate rui only based on simple rui
    main_data = SAMPLE_JSON_DATA_SIMPLE
    write_rui(main_data)