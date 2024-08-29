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

import os
import shutil
import sys
import getopt
import platform

projectName = 'parrotLipsync'

def copytree(src, dst):
    for item in os.listdir(src):
    
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            os.mkdir(d)
            copytree(s, d)
        else:
            filename, extn = os.path.splitext(item)
            print ("file " + filename + " extn  " + extn)
            if (extn != ".py" and extn != ".png" and extn != ".json" and extn != ".toml"):
                continue
                
            shutil.copy(s, d)

def make(copyToBlenderAddons = False, createArchive = False):
    
    blenderAddons = None


    blenderAddons = os.getenv('BLENDER_ADDONS')

    #Create build directory
    curPath = os.getcwd()
    if os.path.exists('build'):
        shutil.rmtree('build')
    os.mkdir('build')
    os.mkdir('build/' + projectName)

    copytree("source", "build/" + projectName);

    
    #Build addon zip file
    if createArchive: 
        if os.path.exists('deploy'):
            shutil.rmtree('deploy')
        os.mkdir('deploy')

        shutil.make_archive("deploy/" + projectName, "zip", "build")


    if copyToBlenderAddons: 
        if blenderAddons == None:
            print("Error: BLENDER_ADDONS not set.  Files not copied to <BLENDER_ADDONS>.")
            return
        
        #addonPath = os.path.join(blenderHome, "scripts/addons")
        destPath = os.path.join(blenderAddons, projectName)

        print("Copying to blender addons: " + destPath)
        if os.path.exists(destPath):
            shutil.rmtree(destPath)
        copytree("build", blenderAddons);


if __name__ == '__main__':
    copyToBlenderAddons = False
    createArchive = False

    for arg in sys.argv[1:]:
        if arg == "-a":
            createArchive = True
        if arg == "-b":
            copyToBlenderAddons = True

    make(copyToBlenderAddons, createArchive)
            
