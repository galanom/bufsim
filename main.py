#!/usr/bin/env python
from gui import get_params
from checkerboard import Checkerboard
params = get_params()
if params:
    Checkerboard(**params)
else:
    print("Aborted")

