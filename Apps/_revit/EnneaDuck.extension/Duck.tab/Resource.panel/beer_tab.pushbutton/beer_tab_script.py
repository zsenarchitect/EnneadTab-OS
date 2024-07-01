#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Go get a drink!"
__title__ = "Beer\nTab"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore

from EnneadTab import UNIT_TEST, USER, ERROR_HANDLE, LOG


@ERROR_HANDLE.try_catch_error
@LOG.log
def beer_tab():
    print (USER.USER_NAME)
    UNIT_TEST.test_core_module()

    print ("ok")

################## main code below #####################


if __name__ == "__main__":
    beer_tab()
