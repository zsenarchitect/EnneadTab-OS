
__alias__ = "ExternalTrimmer"
__doc__ = "This button does ExternalTrimmer when right click"


import external_trimmer_left as ET

def external_trimmer():
    ET.update_link(ET.BLOCK_NAME)

