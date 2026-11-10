"""Build the shipped, independently editable model sources. Does not read any other project."""
import sys
from pathlib import Path
from assets import build, ROOT
def main():
    for name in ("Starter","Deployment","TripleTurret"):
        build(ROOT/"Authoring"/(name+".json"),ROOT/"Examples"/"Mechanisms",name)
if __name__=="__main__": main()

