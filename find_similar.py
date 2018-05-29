#!/usr/bin/env python3

import os
import sys
import gemmi

TOP_DIR=sys.argv[1]
WANTED_SIZE=247493093

selected_file = None
min_diff = sys.maxsize
for (dirpath, dirnames, filenames) in os.walk(TOP_DIR):
    for name in filenames:
        if name.endswith('.gz'):
            path = os.path.join(dirpath, name)
            size = gemmi.estimate_uncompressed_size(path)
            diff = abs(size - WANTED_SIZE)
            if diff < min_diff:
                min_diff = diff
                selected_file = path
print(selected_file)
print('Differs from %d by %d bytes' % (WANTED_SIZE, min_diff))
