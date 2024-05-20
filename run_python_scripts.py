#!/usr/bin/env python3

import os
import sys

# this will execute code directly, make sure the scripts or code are trusted
for arg in sys.argv[1:]:
    if os.path.isfile(arg):
        exec(open(arg).read())
    else:
        exec(arg)
