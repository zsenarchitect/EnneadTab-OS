#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Go get a drink!"
__title__ = "Beer\nTab"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore

from EnneadTab import ERROR_HANDLE, LOG


@ERROR_HANDLE.try_catch_error()
@LOG.log_revit
def beer_tab():


    print ("ok beer")

################## main code below #####################


if __name__ == "__main__":
    beer_tab()
