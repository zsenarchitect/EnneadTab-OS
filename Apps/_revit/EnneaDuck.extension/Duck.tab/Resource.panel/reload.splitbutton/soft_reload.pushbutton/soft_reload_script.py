#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Soft\nReload"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore 

from Duckitect import ERROR_HANDLE, LOG, VERSION_CONTROL



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def soft_reload():
    VERSION_CONTROL.update_EA_dist()


################## main code below #####################
if __name__ == "__main__":
    soft_reload()







