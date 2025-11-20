import os
import sys

root = "C:\\MyRepos\\Python\\mindrove"

print("Searching for shadowing names (axis, graphics, plot)…\n")
for dirpath, dirnames, filenames in os.walk(root):
    for name in dirnames + filenames:
        lowered = name.lower()
        if any(key in lowered for key in [
            "axis", "axisitem", 
            "graphics", "graphicsitem", 
            "plot", "plotitem",
        ]):
            print(os.path.join(dirpath, name))
