# Parrot Lipsync (https://github.com/blackears/parrotLipsync).
# Copyright (c) 2024 Mark McKay
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


bl_info = {
    "name": "Parrot Lipsync",
    "author": "Mark McKay",
    "version": (1, 0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Export > Mesh Exporter",
    "description": "Generate lipsync tracks from audio files using Whisper AI.",
    #"warning": "",
    "doc_url": "https://github.com/blackears/parrotLipsync",
    "category": "View 3D"
}

import bpy
from .parrot_lipsync import ParrotPoseProps
from .parrot_lipsync import ParrotLipsyncProps
from .parrot_lipsync import PLUGIN_PT_ParrotLipsyncPanel
from .parrot_lipsync import PLUGIN_PT_ParrotLipsyncPhonemeGroupPanel
from .parrot_lipsync import PLUGIN_PT_ParrotLipsyncSetupPanel
from .parrot_lipsync import PLUGIN_OT_ParrotRenderLipsyncToAction
from .parrot_lipsync import PLUGIN_OT_ParrotRenderLipsyncToRigNla
from .parrot_lipsync import PLUGIN_OT_ParrotInstallWhisper
from .parrot_lipsync import PLUGIN_OT_ParrotInstallGruut
from .parrot_lipsync import PLUGIN_OT_ParrotReloadPhonemeTable


### REGISTRATION ###

classes=[
    ParrotPoseProps,
    ParrotLipsyncProps,
    PLUGIN_PT_ParrotLipsyncPanel,
    PLUGIN_PT_ParrotLipsyncPhonemeGroupPanel,
#    PLUGIN_PT_ParrotLipsyncSetupPanel,
    PLUGIN_OT_ParrotRenderLipsyncToAction,
    PLUGIN_OT_ParrotRenderLipsyncToRigNla,
#    PLUGIN_OT_ParrotInstallWhisper,
#    PLUGIN_OT_ParrotInstallGruut,
    PLUGIN_OT_ParrotReloadPhonemeTable,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.props = bpy.props.PointerProperty(type=ParrotLipsyncProps)
 #   update_phoneme_group_pose_list(bpy.types.Scene)
    
    # addon_path =  os.path.dirname(__file__)
    # icons_dir = os.path.join(addon_path, "icons")    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    bpy.types.Scene.props = None

if __name__ == "__main__":
    register()
