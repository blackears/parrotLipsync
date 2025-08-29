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

import bpy
import subprocess
import sys
import os
import site
import hashlib
import importlib
import itertools
import mathutils
import numpy as np
from allosaurus.app import read_recognizer
import random
import base64
import json


    
def is_library_installed(lib_name) -> bool:
    try:
        # Blender does not add the user's site-packages/ directory by default.
        sys.path.append(site.getusersitepackages())
        return importlib.util.find_spec(lib_name.replace("-", "_")) is not None
#        return importlib.util.find_spec(lib_name) is not None
    finally:
        sys.path.remove(site.getusersitepackages())
            
def update_phoneme_table_path(self, context):
    print("--update_phoneme_table_path")
    update_phoneme_group_pose_list(context)
    pass
 
def update_phoneme_group_pose_list(context):
    #print("--update_phoneme_group_pose_list")
    phoneme_table = load_phoneme_table(context)
    
    group_list = [info["group"] for info in phoneme_table["phonemes"]]
    group_list = list(dict.fromkeys(group_list))
    group_list.sort()
    if not "rest" in group_list:
        group_list.insert(0, "rest")
    
    groups_already_listed = [p.group for p in context.scene.props.phoneme_poses]
    #context.scene.props.phoneme_poses.clear()
    
    remove_indices = []
    for idx, item in enumerate(context.scene.props.phoneme_poses):
        if not item.group in group_list:
            remove_indices.append(idx)
    
    remove_indices.reverse()
    for idx in remove_indices:
        context.scene.props.phoneme_poses.remove(idx)
    
    for group_name in group_list:
        if not group_name in groups_already_listed:
            pose_props = context.scene.props.phoneme_poses.add()
            pose_props.group = group_name



def load_phoneme_table(context):
    props = context.scene.props
    phoneme_table_path = props.phoneme_table_path
    abs_path = bpy.path.abspath(phoneme_table_path)
    
    #print("Checking path ", abs_path)
    if not os.path.isfile(abs_path):
        addon_path = os.path.dirname(__file__) # for addon
        #addon_path = os.path.dirname(bpy.data.filepath)  # for standalone file
        #print("--addon_path : ", addon_path)
        abs_path = os.path.join(addon_path, "phoneme_table_en.json")
        abs_path = bpy.path.abspath(abs_path)
        #print("--Default table: ", str(abs_path))

    with open(abs_path) as f:
        phoneme_table = json.load(f)
        #print("phoneme_table: ", phoneme_table)
        return phoneme_table

#------------------------------------------
# Properties

class ParrotPoseProps(bpy.types.PropertyGroup):
    group: bpy.props.StringProperty(
        name="Group name",
    )
    # pose: bpy.props.StringProperty(
        # name="Pose name",
    # )
    pose: bpy.props.PointerProperty(
        name = "Pose Action",
        description = "Armature pose for this lipsync group.",
        type=bpy.types.Action
    )

class ParrotLipsyncProps(bpy.types.PropertyGroup):
    # espeak_path: bpy.props.StringProperty(
        # name="eSpeak library file",
        # default='C:\\Program Files\\eSpeak NG\\libespeak-ng.dll',
        # subtype='FILE_PATH',
    # )
    # whisper_library_model: bpy.props.EnumProperty(
        # name="Whisper library",
        # items= [('tiny', 'tiny', 'vram ~1GB, speed 32x'),
               # ('base', 'base', 'vram ~1GB, speed 16x'),
               # ('small', 'small', 'vram ~2GB, speed 6x'),
               # ('medium', 'medium', 'vram ~5GB, speed 2x'),
               # ('large', 'large', 'vram ~10GB, speed 1x'),
               # ('tiny.en', 'tiny.en', 'english only - vram ~1GB, speed 32x'),
               # ('base.en', 'base.en', 'english only - vram ~1GB, speed 16x'),
               # ('small.en', 'small.en', 'english only - vram ~2GB, speed 6x'),
               # ('medium.en', 'medium.en', 'english only - vram ~5GB, speed 2x'),],
        # default='base'
    # )
    # autodetect_language: bpy.props.BoolProperty(
        # name="Auto detect language",
        # description="If checked, will automatically determine language being spoken.",
        # default=False,
    # )
    # language_code: bpy.props.StringProperty(
        # name="Language code",
        # description="Language code of the audio being translated.  (Such as: en, fr, es, de, ja, ko, zh)",
        # default="en"
    # )
    key_interpolation: bpy.props.EnumProperty(
        name="Key Interpolation",
        items= [('constant', 'constant', 'constant interpolation'),
               ('linear', 'linear', 'linear interpolation'),
               ('bezier', 'bezier', 'bezier interpolation'),],
        default='bezier'
    )
    phoneme_table_path: bpy.props.StringProperty(
        name="Phoneme table file",
        default='//phoneme_table_en.json',
        subtype='FILE_PATH',
        update=update_phoneme_table_path,
    )
    phoneme_poses: bpy.props.CollectionProperty(
        name="Phoneme poses",
        description="Mouth poses",
        type=ParrotPoseProps
    )
    target_object: bpy.props.PointerProperty(
        name = "Target Object",
        description = "Object you wish to apply lipsync to.",
        type=bpy.types.Object
    )
    lipsync_action: bpy.props.PointerProperty(
        name = "Lipsync Action",
        description = "Action lipsync data will be written to.",
        type=bpy.types.Action
    )
    word_pad_frames: bpy.props.IntProperty(
        name="Word pad frames",
        description="Number of frames surrounding a word to place rests",
        default=2,
        min=1,
        soft_max=10
    )
    rig_action_suffix: bpy.props.StringProperty(
        name="Action Name Suffix",
        default='_parrot',
    )
    attenuation: bpy.props.FloatProperty(
        name="Strength multiplier",
        description="Attenuate all key poses by a constant amount.",
        default=1,
        min=0,
        soft_max=1
    ) 
    attenuate_volume: bpy.props.BoolProperty(
        name="Track volume multiplier",
        description="Attenuate the strength of the keyframe based on the loudness of the vocal track.",
        default=False,
    ) 
    silence_cutoff: bpy.props.FloatProperty(
        name="Silence cutoff",
        description="If a track frame's audio lies below this value, the frame is considered to be silent.  This is used to adjust the start times of words.",
        default=.05,
        min=0,
        max=1,
    ) 
    limit_pps: bpy.props.BoolProperty(
        name="Limit phonemes per second",
        description="Drop extra phonemes if the go over the speed limit.",
        default=False,
    ) 
    phonemes_per_second: bpy.props.FloatProperty(
        name="Phonemes per second",
        description="Drop extra phonemes when the phoneme rate goes over this limit.",
        default=14,
        min=0,
        soft_max=10,
    ) 
    rest_gap: bpy.props.FloatProperty(
        name="Rest gap",
        description="Pauses between phonemes greater than this many seconds will cause the rest pose to be used.",
        default=.2,
        min=0,
        soft_max=2,
    ) 

#------------------------------------------
# Tooltip operator

class PLUGIN_OT_TooltipOperator(bpy.types.Operator):
    bl_idname = "parrot.tooltip_operator"
    bl_label = "Operator"
    
    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return operator.tooltip
    
#------------------------------------------
# Panel

class PLUGIN_PT_ParrotLipsyncPanel(bpy.types.Panel):
    bl_label = "Parrot Lipsync"
    bl_idname = "PLUGIN_PT_lipsync"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Parrot Lipsync"

    def draw(self, context):
        props = context.scene.props
        
        layout = self.layout

        main_column = layout.column()

        main_column.prop(props, "phoneme_table_path")
        main_column.prop(props, "key_interpolation")

        main_column.prop(props, "rest_gap")
        
        main_column.prop(props, "limit_pps")
        row = main_column.row()
        row.enabled = props.limit_pps
        row.prop(props, "phonemes_per_second")

        box_single = main_column.box()
        box_single.prop(props, "lipsync_action")
        box_single.operator("parrot.lipsync_to_action")

        box_create_tracks = main_column.box()
        box_create_tracks.prop(props, "target_object")
        box_create_tracks.prop(props, "rig_action_suffix")
        box_create_tracks.operator("parrot.render_lipsync_to_object_nla")
        
        main_column.operator("parrot.reload_phoneme_table")


class PLUGIN_PT_ParrotLipsyncPhonemeGroupPanel(bpy.types.Panel):
    bl_label = "Phoneme Groups"
    bl_idname = "PLUGIN_PT_lipsync_phoneme_groups"
    bl_parent_id = "PLUGIN_PT_lipsync"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        props = context.scene.props
        layout = self.layout
        
        phoneme_table = load_phoneme_table(context)
        
        #print("drawing phoneme panel")
        #print(phoneme_table)
        
        group_hash = {}
        for group_info in phoneme_table["groups"]:
            name = group_info["name"]
            group_hash[name] = group_info
                    
        
        #print(group_hash)
        main_column = layout.column()
        
        for pose_props in props.phoneme_poses:
            box = main_column.box()
            row = box.row()
            group = str(pose_props.group)
            #print("group ", group)
            row.label(text = group)
            #print(group_hash)
            desc_text = group_hash[group]["description"] if group in group_hash else ""
            row.label(text = desc_text)

            info_text = ""
            for phoneme in phoneme_table["phonemes"]:
                if phoneme["group"] == group:
                    info_text += phoneme["code"] + ": " + phoneme["example"] + "\n"

            #op = layout.operator("parrot.tooltip_operator")
            #op.tooltip = info_text
            #row.operator("parrot.tooltip_operator").tooltip = info_text
            op = row.operator("parrot.tooltip_operator", text="Hint")
            op.tooltip = info_text

            box.prop(pose_props, "pose")
        
            
# class PLUGIN_PT_ParrotLipsyncSetupPanel(bpy.types.Panel):
    # bl_label = "Setup"
    # bl_idname = "PLUGIN_PT_lipsync_setup"
    # bl_parent_id = "PLUGIN_PT_lipsync"
    # bl_space_type = 'VIEW_3D'
    # bl_region_type = 'UI'
    # bl_options = {"DEFAULT_CLOSED"}

    # def draw(self, context):
        # props = context.scene.props
        # layout = self.layout

        # main_column = layout.column()
        
        # main_column.operator("parrot.install_whisper")
        # main_column.operator("parrot.install_gruut")


        
        
#------------------------------------------
# Lipsync to action

phoneme_cache = {}
word_list_info_cache = {}
sound_profile_cache = {}

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            
    return hash_md5.hexdigest()


def max_values_in_partitions(arr, n):
    # Calculate the length of each partition
    partition_length = len(arr) // n
    
    # Reshape the input array into a 2D array with 'n' rows and 'partition_length' columns
    partitions = np.reshape(arr[:n * partition_length], (n, partition_length))
    
    # Calculate the maximum value along each row (axis=1) and return the result
    return np.max(partitions, axis=1)


allosaurus_model = None

#Parse audio track to phonemes
def get_phonemes_from_audio(context, seq):
    props = context.scene.props

    global allosaurus_model
    if not allosaurus_model:
        allosaurus_model = read_recognizer("latest")
    
    sourcepath = bpy.path.abspath(seq.sound.filepath)
    filepath_wav = sourcepath
    
    temp_file = None
    
    if not filepath_wav.endswith(".wav"):
        filename, extn = os.path.splitext(filepath_wav)

        key = base64.urlsafe_b64encode(random.randbytes(16)).decode("utf-8")[:-2]
        newpath = filename + "_" + key + '.wav'
        temp_file = newpath
        
        subprocess.call(['ffmpeg', '-y', '-i', filepath_wav, newpath])
        filepath_wav = newpath
    
    token = allosaurus_model.recognize(filepath_wav, timestamp=True)

    if temp_file:
        os.remove(temp_file)

    #token now has the parsed phoneme data
    print(token)
    
    phone_list = []
    for t in token.splitlines():
        time, dur, phone = t.split(" ")
        phone_list.append({
            "time": float(time), 
            "dur": float(dur), 
            "phone": phone
        })

    return phone_list



def render_lipsync_to_action(context, tgt_action, seq):
    props = context.scene.props
    
    key_interpolation = props.key_interpolation
    limit_pps:bool = props.limit_pps
    phonemes_per_second:float = props.phonemes_per_second
    rest_gap:float = props.rest_gap

    fps = context.scene.render.fps
    
    phone_list = get_phonemes_from_audio(context, seq)
    if len(phone_list) == 0:
        return

    #Throw out extra phonemes
    if limit_pps:
        sec_per_phone = 1 / phonemes_per_second
        new_phone_list = []
        last_phone_time:float = 0
        
        for phone in phone_list:
            if not new_phone_list:
                new_phone_list.append(phone)
                last_phone_time = phone["time"]
            elif phone["time"] - last_phone_time > sec_per_phone:
                new_phone_list.append(phone)
                last_phone_time = phone["time"]
        
        phone_list = new_phone_list

    #Make sure phone table is up to date
    update_phoneme_group_pose_list(context)
    

    phoneme_table = load_phoneme_table(context)

    #Map phone codes to phoneme table entries
    phoneme_hash:dict[str, dict] = {}
    for info in phoneme_table["phonemes"]:
        #print("Adding phoneme ", info)
        phoneme_hash[info["code"]] = info

    #Map group names to pose actions
    group_pose_hash:dict[str, bpy.props.PointerProperty] = {}
    for pose_props in props.phoneme_poses:
        group_pose_hash[pose_props.group] = pose_props.pose

    seq_time_start = seq.frame_offset_start / fps
    seq_time_end = (seq.frame_offset_start + seq.frame_final_duration) / fps

    #Convert phonemes to phone groups and add rests
    groups_seq:[dict] = []

    groups_seq.append(["rest", phone_list[0]["time"] - rest_gap])
    
    list_size = len(phone_list) - 2
    for phone_idx in range(len(phone_list) - 2):
        p0 = phone_list[phone_idx]
        p1 = phone_list[phone_idx + 1]
        
        phone = p0["phone"]
        if phone in phoneme_hash:
            groups_seq.append([phoneme_hash[phone]["group"], p0["time"]])
        else:
            print("missing phoneme:", phone)
        
        gap = p1["time"] - p0["time"]
        
        if gap > rest_gap * 2:
            groups_seq.append(["rest", p0["time"] + rest_gap])
            groups_seq.append(["rest", p1["time"] - rest_gap])
        elif gap > rest_gap:
            groups_seq.append(["rest", (p0["time"] + p1["time"]) / 2])
            
    phone = phone_list[-1]["phone"]
    if phone in phoneme_hash:
        groups_seq.append([phoneme_hash[phone]["group"], phone_list[-1]["time"]])
    else:
        print("missing phoneme:", phone)
    groups_seq.append({"rest", phone_list[-1]["time"] + rest_gap})
            
    #print("---Group seq")
    #print(groups_seq)
    

    #Clear existing animation
    tgt_action.fcurves.clear()
    for marker in tgt_action.pose_markers.values():
        tgt_action.pose_markers.remove(marker)

    #Write tracks
    for idx, phone_timing in enumerate(groups_seq):
        #print(phone_timing)
                        
        group_name, time = phone_timing
        #print("group_name " , group_name)
        if not group_name in group_pose_hash:
            continue
        
        src_action = group_pose_hash[group_name]
        if not src_action:
            continue

        marker = tgt_action.pose_markers.new(group_name)
        marker.frame = int(time * fps)
        
        #Ensure groups are present
        for src_group in src_action.groups:
            if not src_group.name in tgt_action.groups:
                tgt_action.groups.new(src_group.name)


        for src_curve in src_action.fcurves:
            #print("src_curve.data_path ", src_curve.data_path, src_curve.array_index)
            
            if src_curve.is_empty:
                continue

            tgt_curve = tgt_action.fcurves.find(src_curve.data_path, index = src_curve.array_index)
            if not tgt_curve:
                tgt_curve = tgt_action.fcurves.new(src_curve.data_path, index = src_curve.array_index)
                if src_curve.group:
                    tgt_curve.group = tgt_action.groups[src_curve.group.name]
            
            frame_range = src_action.curve_frame_range
            #print("range ", range)
            for src_kf in src_curve.keyframe_points:

                tgt_kf = tgt_curve.keyframe_points.insert(frame = (src_kf.co[0] - frame_range[0] + int(time * fps)), value = src_kf.co[1])
                
                tgt_kf.interpolation = src_kf.interpolation
                if key_interpolation == "constant":
                    tgt_kf.interpolation = 'CONSTANT'
                elif key_interpolation == "linear":
                    tgt_kf.interpolation = 'LINEAR'
                elif key_interpolation == "bezier":
                    tgt_kf.interpolation = 'BEZIER'
                    
                tgt_kf.easing = src_kf.easing
                tgt_kf.handle_left = src_kf.handle_left
                tgt_kf.handle_right = src_kf.handle_right
                tgt_kf.period = src_kf.period




#------------------------------------------
# Lipsync to rig NLA

class PLUGIN_OT_ParrotRenderLipsyncToRigNla(bpy.types.Operator):
    """
    Parrot Lipsync To Nla
    """
    bl_label = "Render Lipsync to Object NLA"
    bl_idname = "parrot.render_lipsync_to_object_nla"
    
    def execute(self, context):
            

        props = context.scene.props
        
        target_object = props.target_object
        rig_action_suffix = props.rig_action_suffix
        
        if not target_object:
            self.report({"WARNING"}, "Target object is not set")
            return {'CANCELLED'}

        if not target_object.animation_data:
            target_object.animation_data_create()
        
        target_object.animation_data.use_nla = True
        
        track_cache = {}
        
        for seq in context.scene.sequence_editor.sequences_all:
            if seq.type != 'SOUND' or not seq.select:
                continue
            
            action_name = seq.name + rig_action_suffix
            if action_name in bpy.data.actions:
                tgt_action = bpy.data.actions[action_name]
            else:
                tgt_action = bpy.data.actions.new(action_name)
            
            #print("render to seq ", seq.name)
            #print("render to action ", tgt_action.name)
            render_lipsync_to_action(context, tgt_action, seq)
            
            track = None
            if seq.channel in track_cache:
                #print("reusing track ", seq.channel)
                track = track_cache[seq.channel]
            else:
                track = target_object.animation_data.nla_tracks.new()

                track_cache[seq.channel] = track
                #print("creating track ", track.name, " on object ", target_object.name)
                
            strip = track.strips.new(tgt_action.name, int(seq.frame_start + tgt_action.frame_range[0]), tgt_action)
            strip.extrapolation = 'NOTHING'
            strip.blend_type = 'REPLACE'
            #print("adding strip ", strip.name)
        
        if not track_cache:
            self.report({"WARNING"}, "No sound tracks selected")
            return {'CANCELLED'}
        
        target_object.animation_data.action = None
        
        return {'FINISHED'}


#------------------------------------------
# Lipsync to action

class PLUGIN_OT_ParrotRenderLipsyncToAction(bpy.types.Operator):
    """
    Parrot Lipsync To Action
    """
    bl_label = "Render Lipsync to Action"
    bl_idname = "parrot.lipsync_to_action"
    
    def execute(self, context):
    
        props = context.scene.props
        
        tgt_action = props.lipsync_action
        
        if not tgt_action:
            tgt_action = bpy.data.actions.new("lipsync")
            
            props.lipsync_action = tgt_action

        seq = context.scene.sequence_editor.active_strip

        if not seq or seq.type != 'SOUND':
            self.report({"WARNING"}, "You must select an audio track in the sequencer.")
            return {'CANCELLED'}
                
        render_lipsync_to_action(context, tgt_action, seq)

            
        
        return {'FINISHED'}


class PLUGIN_OT_ParrotReloadPhonemeTable(bpy.types.Operator):
    """
    Reload Phoneme Table
    """
    bl_label = "Reload Phoneme Table"
    bl_idname = "parrot.reload_phoneme_table"
    
    def execute(self, context):
        update_phoneme_group_pose_list(context)

        return {'FINISHED'}


