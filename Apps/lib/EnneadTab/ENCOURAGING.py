#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

import FOLDER


def random_warming_quote():
    with open('{}\_warming_quotes.txt'.format(FOLDER.get_folder_path_from_path(__file__)), "r") as f:
        lines = f.readlines()
    random.shuffle(lines)
    return lines[0].replace("\n", "")
