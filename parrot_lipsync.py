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
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Export > Mesh Exporter",
    "description": "Generate lipsync tracks from audio files using Whisper AI.",
    #"warning": "",
    "doc_url": "https://github.com/blackears/parrotLipsync",
#    "category": "Import/Export",
    "category": "View 3D"
}



import subprocess
import sys
import os
import bpy

import whisper_timestamped as whisper

from phonemizer.backend import EspeakBackend
from phonemizer.punctuation import Punctuation
from phonemizer.separator import Separator
import json


def install_whisper():
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    target = os.path.join(sys.prefix, 'lib', 'site-packages')
     
    subprocess.call([python_exe, '-m', 'ensurepip'])
    subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])

    #example package to install (SciPy):
    #subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'scipy', '-t', target])
    subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'whisper-timestamped', '-t', target])
    
#------------------------------------------
# Properties

class ParrotLipsyncProps(bpy.types.PropertyGroup):
    espeak_path: bpy.props.StringProperty(
        name="eSpeak library file",
        default='C:\\Program Files\\eSpeak NG\\libespeak-ng.dll',
        subtype='FILE_PATH',
    )
    whisper_library_model: bpy.props.EnumProperty(
        name="Whisper library",
        items= [('tiny', 'tiny', 'vram ~1GB, speed 32x'),
               ('base', 'base', 'vram ~1GB, speed 16x'),
               ('small', 'small', 'vram ~2GB, speed 6x'),
               ('medium', 'medium', 'vram ~5GB, speed 2x'),
               ('large', 'large', 'vram ~10GB, speed 1x'),
               ('tiny.en', 'tiny.en', 'english only - vram ~1GB, speed 32x'),
               ('base.en', 'base.en', 'english only - vram ~1GB, speed 16x'),
               ('small.en', 'small.en', 'english only - vram ~2GB, speed 6x'),
               ('medium.en', 'medium.en', 'english only - vram ~5GB, speed 2x'),],
        default='tiny'
    )
    autodetect_language: bpy.props.BoolProperty(
        name="Auto detect language",
        description="If checked, will automatically determine language being spoken.",
        default=False,
    )
    language_code: bpy.props.StringProperty(
        name="Language code",
        description="Language code of the audio being translated.  (Such as: en, fr, es, de, ja, ko, zh)",
        default="en"
    )

 
#------------------------------------------
# Panel

class PLUGIN_PT_ParrotLipsyncPanel(bpy.types.Panel):
    bl_label = "Parrot Lipsync Panel"
    bl_idname = "PLUGIN_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Parrot Lipsync"

    def draw(self, context):
        manage_props = context.scene.manage_props
        layout = self.layout

        system_setting_column = layout.column()

        system_setting_column.prop(manage_props, "espeak_path")
        system_setting_column.prop(manage_props, "whisper_library_model")
        system_setting_column.prop(manage_props, "autodetect_language")
        system_setting_column.prop(manage_props, "language_code")

        system_setting_column.operator("plugin.parrot_lipsync_generator")


#------------------------------------------
# Render objects

class PLUGIN_OT_ParrotLipsyncGenerator(bpy.types.Operator):
    """
    Parrot Lipsync Generator
    """
    bl_label = "Parrot Lipsync Generator"
    bl_idname = "plugin.parrot_lipsync_generator"
    
    def execute(self, context):
        manage_props = context.scene.manage_props
        
        whisper_library_model = manage_props.whisper_library_model
        autodetect_language = manage_props.autodetect_language
        language_code = manage_props.language_code
        
        model = whisper.load_model(whisper_library_model)
            
        for seq in context.scene.sequence_editor.sequences_all:
            if seq.type != 'SOUND' or not seq.select:
                continue
                
            path = bpy.path.abspath(seq.sound.filepath)
#            print("Processing ", path)
            
            audio = whisper.load_audio(path)
            audio = whisper.pad_or_trim(audio)
            
            final_language_code = language_code
            
            if autodetect_language:
                # make log-Mel spectrogram and move to the same device as the model
                mel = whisper.log_mel_spectrogram(audio).to(model.device)

                # detect the spoken language
                _, probs = model.detect_language(mel)
                print(f"Detected language: {max(probs, key=probs.get)}")
                final_language_code = max(probs, key=probs.get)

            
            result = whisper.transcribe(model, audio, language=final_language_code)

            print(json.dumps(result, indent = 2, ensure_ascii = False))
            
            #_, probs = model.detect_language(mel)
            #print(f"Detected language: {max(probs, key=probs.get)}")
 
####
 
            print("Processing ", seq.name)
            print("Processing ", seq.sound.filepath)
            
            #bpy.data.sounds
            
            seq.frame_duration
            #Timeline position
            seq.frame_final_start
            seq.frame_final_end

            #Frames in track being rendered
            seq.frame_offset_start
            seq.frame_offset_end
            
            #bpy.type.Sound
            seq.sound.filepath
            
            
        
        return {'FINISHED'}




### REGISTRATION ###

classes=[
    ParrotLipsyncProps,
    PLUGIN_PT_ParrotLipsyncPanel,
    PLUGIN_OT_ParrotLipsyncGenerator,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.manage_props = bpy.props.PointerProperty(type=ParrotLipsyncProps)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)       
        bpy.types.Scene.manage_props = None

if __name__ == "__main__":
    register()