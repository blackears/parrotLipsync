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

#projectName = 'kitfoxQuadRemesher'

platforms = ["macosx_11_0_arm64", "manylinux_2_28_x86_64", "win_amd64", "manylinux_2_17_x86_64"]
#platforms = ["macosx_11_0_arm64", "manylinux_2_17_x86_64", "win_amd64"]

python_modules = [
#"pocketsphinx",
"allosaurus",
#"whisper_timestamped-1.15.4",
#"whisper_timestamped", 

# "gruut", 
# "gruut-lang-ar",
# "gruut-lang-cs",
# "gruut-lang-de",
# "gruut-lang-en",
# "gruut-lang-es",
# "gruut-lang-fa",
# "gruut-lang-fr",
# "gruut-lang-it",
# "gruut-lang-lb",
# "gruut-lang-nl",
# "gruut-lang-pt",
# "gruut-lang-ru",
# "gruut-lang-sv",
# "gruut-lang-sw",
]

def build_wheels():
    curPath = os.getcwd()
    if os.path.exists('source/wheels'):
        shutil.rmtree('source/wheels')
    os.mkdir('source/wheels')
    
    for plat in platforms:
        for module in python_modules:
            #pip.main(["download", module, "--dest", "source/wheels", "--only-binary=:all:", "--python-version=3.11", "--platform=" + plat])

#            subprocess.call(["pip", "wheel", "numba", "-w", "source/wheels2"])
            subprocess.call(["python", "-m", "pip", "wheel", "--wheel-dir", "source/wheels", "--only-binary=:all:", module])
            

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
    subprocess.call(["blender", "--command", "extension", "install-file", "--enable", "--repo", "user_default",  "extension/kitfox_quad_remesher-1.0.0-windows_x64.zip"])


if __name__ == '__main__':
    copyToBlenderAddons = False
    createArchive = False

    for arg in sys.argv[1:]:
        if arg == "-w":
            build_wheels()
        if arg == "-e":
            build_extension()
        if arg == "-i":
            install_extension()

            
