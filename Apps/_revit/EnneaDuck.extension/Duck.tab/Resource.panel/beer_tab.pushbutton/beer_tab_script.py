#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Go get a drink!"
__title__ = "Beer\nTab"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore

from Duckitect import ERROR_HANDLE, LOG


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def beer_tab():

   
    print ("ok beer")

################## main code below #####################


if __name__ == "__main__":
    beer_tab()
