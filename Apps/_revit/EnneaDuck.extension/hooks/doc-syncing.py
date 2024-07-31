import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import VERSION_CONTROL, ERROR_HANDLE, LOG


__title__ = "Doc Syncing Hook"

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def doc_syncing():
    VERSION_CONTROL.update_EA_dist()

#################################################################

if __name__ == "__main__":
    doc_syncing()