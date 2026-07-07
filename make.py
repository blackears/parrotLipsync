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

import platform
import os
import sys
import subprocess
import urllib.request
import zipfile
import tarfile

platform_sys = platform.system()

wheels_dir = "build/source/wheels"
build_dir = "build/source"
BLENDER_ARCHIVE = "blender-5.1.2-linux-x64.tar.gz"

if platform_sys == 'Windows':
    pass
elif platform_sys == 'Linux':
    if not os.path.exists("build"):
        os.makedirs("build")
    os.chdir("build")

    if not os.path.exists(wheels_dir):
        os.makedirs(wheels_dir)
    
    #Download wheels
    command = [
            sys.executable, "-m", "pip", "download",
            #"--only-binary=:all:",  # Force downloading wheels only (.whl)
            "--dest", wheels_dir,   # Specify target directory
            "allosaurus"
        ]    

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while downloading: {e.stderr}")

    #Build manifest
    os.chdir("source")

    manifest_text = ""
    with open("../blender_manifest_template_linux.toml", "r") as file:
        for line in file:
            if line.startswith("numpy"):
                continue
            
            manifest_text += line

    with open("blender_manifest.toml", "w", encoding="utf-8") as file:
        file.write(manifest_text)

    #Download blender
    if not os.path.exists("blender"):
        os.makedirs("blender")

    urllib.request.urlretrieve("https://download.blender.org/release/Blender5.1/${BLENDER_ARCHIVE}", "blender/blender.tar.gz")

    #Unzip Blender
    # with zipfile.ZipFile("blender.tar.gz", 'r') as zip_ref:
    #     zip_ref.extractall("blender_dir")

    with tarfile.open("blender.tar.gz", "r:gz") as tar:
        # Extract all contents into the current directory
        tar.extractall(path="blender_dir")

    if not os.path.exists("extension"):
        os.makedirs("extension")
    
    #Build extension
    command = [
            "blender_dir/blender", 
            "--command", "extension", 
            "build",
            "--source-dir", "source",
            "--output-filepath", "extension/parrotLipsync.zip",
        ]    

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while downloading: {e.stderr}")


    pass

elif platform_sys == 'Darwin':
    #Macintosh
    pass


    
    
 