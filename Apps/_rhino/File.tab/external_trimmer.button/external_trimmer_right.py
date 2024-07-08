
__title__ = "ExternalTrimmer"
__doc__ = "This button does ExternalTrimmer when right click"


import external_trimmer_left as ET
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def external_trimmer():
    ET.update_link(ET.BLOCK_NAME)




if __name__ == "__main__":
    external_trimmer()