"""
HOW TO RUN:
When ready to generate new RUI, run me in VScode


WHY THIS:
Rhino rui file is locked to one editor. When closing Rhino it generate new GUID for the macros
so it is not possible to track change with GIT.(Always changing) And hard to collabrate...

HOW IS THIS STURCTURED:
prepare the toolbar system in a folder system
Top levels are '.tab' and '.menu' folder. Note for simplity, there should be only ONE .menu folder

under tab/menu folder you can have:
    - many '.button' folders
    - one icon for the tab/menu 
    - one yaml file for the ordering of buttons, in the yaml file:
        - under the layout header, write name of the .button folder in order
        - use --- to add divder in UI
        - mispelled name or undefined order button will be append to the end of the tolbar

inside .button folder you have all the contents to make a button.
    - button icon
    - xxx_left.py
    - xxxx_right.py(optional)
    - any_other_helper_script.py(optional)

inside the left/right script, you need:
    - a primary function called 'xxx' or 'xxx_left' or 'xxx_right'. Without this primary function the parser cannot find it to call.
    - define __alias__ that become the name of the button, as well as command alias in the future
    - define __doc__ that describe what it does



Configer the source folder and output rui file in the 'constants.py'




!!!!!!!!
As the migration of old script to new structure. DELETE converted python from old system.



TO-DO:
make a folder type "xxx.link". This will run the alias of the link.
The python script will have a LINK_ID that is NEVER change no matter who script rename.
example:
source file, this expect other to run it: ID = 'sample_id_123'
other file, this expect to run source file as alias: LINK_ID = 'sample_id_123'

during compile xml file,if LINK_ID is found, it look for file with ID, and use data there for its name, doc, func_name, icon
"""


import RuiWriter



if __name__ == "__main__":
    RuiWriter.run()

