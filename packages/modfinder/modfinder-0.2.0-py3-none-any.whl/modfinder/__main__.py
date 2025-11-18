import sys
from . import install

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "install":
        install(sys.argv[2])
    else:
        print("Usage: modfinder install <package>")