import sys
from cx_Freeze import setup, Executable
import os
import argparse
import sys
from PIL import Image
import pyzbar
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
import winsound


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "console"


setup(  name = "bc_Audit",
    version = "0.2",
    description = "Barcode Auditor",
    options = {"build_exe": build_exe_options},
    executables = [Executable("bcAudit.py", base = base)])
