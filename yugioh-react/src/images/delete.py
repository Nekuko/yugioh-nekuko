import os
from os import listdir
from os.path import isfile, join
import time
onlyfiles = [f for f in listdir("./") if isfile(join("./", f))]

for f in onlyfiles:
    if "cropped" in f:
        os.remove(f)
