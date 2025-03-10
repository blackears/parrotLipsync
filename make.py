#!/usr/bin/env python

# This file is part of the Kitfox Normal Brush distribution (https://github.com/blackears/blenderEasyFly).
# Copyright (c) 2021 Mark McKay
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import getopt
import platform
import subprocess
import pip
import sys
import os
import shutil

#projectName = 'parrotLipsync'

platforms = ["macosx_11_0_arm64", "manylinux_2_28_x86_64", "win_amd64", "manylinux_2_17_x86_64"]
#platforms = ["macosx_11_0_arm64", "manylinux_2_17_x86_64", "win_amd64"]

python_modules = [
"allosaurus",

]

# wheels_no_deps = [
    # "allosaurus", "resampy", "panphon", "requests", "tqdm",    
    # "filelock", "fsspec", "jinja2", "mpmath", "munkres", "networkx", "panphon", 
# ]

# wheels_bin = [
    # "scipy", "torch", "editdistance", 
    # "editdistance", "llvmlite", "MarkupSafe", "numba", 
# ]

# wheels_bin = [
    # ["allosaurus", "--no-deps", "macosx_14_0_arm64"],
    # ["scipy", "--only-binary=:all:", "macosx_14_0_arm64"],
# ]

#https://files.pythonhosted.org/packages/07/85/3ef1d2f70736bef5650c7fedbf4d4e01efe728f10bad0294a9a8d396ff00/allosaurus-1.0.2-py3-none-any.whl

#pip download scipy --dest ./wheels-extra-mac --only-binary=:all: --platform=macosx_14_0_arm64
#pip download scipy --dest ./wheels-extra-mac --only-binary=:all: --platform=macosx_14_0_x86_64

#pip download torch --dest ./wheels-extra-mac --only-binary=:all: --platform=macosx_11_0_arm64
#pip download editdistance --dest ./wheels-extra-mac --only-binary=:all: --platform=macosx_11_0_arm64

def print_wheel_list():
    for f in os.listdir("source/wheels"):
        filename = os.fsdecode(f)
        print("    \"./wheels/" + filename.strip() + "\",")

def build_wheels():
    if True:
        #Currently not working
        #https://projects.blender.org/blender/blender/issues/127632
        return
    
    curPath = os.getcwd()
    if os.path.exists('source/wheels'):
        shutil.rmtree('source/wheels')
    os.mkdir('source/wheels')
    
    for plat in platforms:
        for module in python_modules:
            #pip.main(["download", module, "--dest", "source/wheels", "--only-binary=:all:", "--python-version=3.11", "--platform=" + plat])

            subprocess.call(["pip", module, "numba", "-w", "source/wheels2"])
#            subprocess.call(["python", "-m", "pip", "wheel", "--wheel-dir", "source/wheels", "--only-binary=:all:", module])
            

def build_extension():
    curPath = os.getcwd()
    if os.path.exists('extension'):
        shutil.rmtree('extension')
    os.mkdir('extension')
    
    subprocess.call(["blender", "--command", "extension", "build", "--split-platforms", "--source-dir", "source", "--output-dir", "extension"])
 
#pip wheel numba -w .
#pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_11_0_arm64
#pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_28_x86_64
#pip download pillow --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64 --platform=macosx_11_0_arm64

#blender --command extension build --split-platforms

def install_extension():
    subprocess.call(["blender", "--command", "extension", "install-file", "--enable", "--repo", "user_default",  "extension/parrot_lipsync-1.1.1-windows_x64.zip"])


if __name__ == '__main__':
    copyToBlenderAddons = False
    createArchive = False

    for arg in sys.argv[1:]:
        if arg == "-w":
            build_wheels()
        if arg == "-l":
            print_wheel_list()
        if arg == "-e":
            build_extension()
        if arg == "-i":
            install_extension()

            
