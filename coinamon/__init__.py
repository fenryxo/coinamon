# coding: utf-8

import sys
if sys.hexversion < 0x030400F0:
    raise Exception("Python >= 3.4 required")


def hello():
    print("Hello, world!")
