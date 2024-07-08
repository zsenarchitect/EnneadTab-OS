
__title__ = "SaveSmallAndClose"
__doc__ = "Save small file and close document. You dont need to wait."
import rhinoscriptsyntax as rs
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def save_small_and_close():
    rs.Command("_NoEcho _Purge _Pause _Materials=_Yes _BlockDefinitions=_Yes _AnnotationStyles=_Yes _Groups=_Yes _HatchPatterns=_Yes _Layers=_Yes _Linetypes=_Yes _Textures=_Yes Environments=_Yes _Bitmaps=_Yes _Enter")
    rs.Command("savesmall")
    rs.Exit()


if __name__ == "__main__":
    save_small_and_close()