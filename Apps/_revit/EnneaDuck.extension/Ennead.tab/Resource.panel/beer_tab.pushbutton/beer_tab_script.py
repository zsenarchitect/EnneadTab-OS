#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Go get a drink!"
__title__ = "Beer\nTab"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore

from EnneadTab import ERROR_HANDLE, LOG, UNIT_TEST


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def beer_tab():

    UNIT_TEST.test_core_module()
    print ("ok beer")
    

################## main code below #####################


if __name__ == "__main__":
    beer_tab()
