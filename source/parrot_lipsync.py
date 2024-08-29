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

import subprocess
import sys
import os
import bpy
import site
import hashlib
import importlib
import itertools
import mathutils
import numpy as np

# import whisper_timestamped as whisper

# from phonemizer.backend import EspeakBackend
# from phonemizer.punctuation import Punctuation
# from phonemizer.separator import Separator
# from phonemizer.backend.espeak.wrapper import EspeakWrapper

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
#        print("phoneme_table: ", phoneme_table)
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
        default='base'
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
    key_interpolation: bpy.props.EnumProperty(
        name="Key Interpolation",
        items= [('constant', 'constant', 'constant interpolation'),
               ('linear', 'linear', 'linaer interpolation'),
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

#        main_column.prop(props, "espeak_path")
        main_column.prop(props, "whisper_library_model")
        main_column.prop(props, "phoneme_table_path")
        main_column.prop(props, "key_interpolation")
        main_column.prop(props, "silence_cutoff")
        main_column.prop(props, "word_pad_frames")
        main_column.prop(props, "attenuation")
        main_column.prop(props, "attenuate_volume")

        main_column.prop(props, "autodetect_language")        
        row = main_column.row()
        row.enabled = not props.autodetect_language
        row.prop(props, "language_code")

        main_column.prop(props, "limit_pps")
        row = main_column.row()
        row.enabled = props.limit_pps
        row.prop(props, "phonemes_per_second")
        

        # main_column.prop(props, "override_espeak_language_code")
        # row = main_column.row()
        # row.enabled = props.override_espeak_language_code
        # row.prop(props, "espeak_language_code")


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
            
            box.prop(pose_props, "pose")
        
            
class PLUGIN_PT_ParrotLipsyncSetupPanel(bpy.types.Panel):
    bl_label = "Setup"
    bl_idname = "PLUGIN_PT_lipsync_setup"
    bl_parent_id = "PLUGIN_PT_lipsync"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        props = context.scene.props
        layout = self.layout

        main_column = layout.column()
        
        main_column.operator("parrot.install_whisper")
        main_column.operator("parrot.install_gruut")


# valid_espeak_codes = ['af', 'am', 'an', 'as', 'az', 'ba', 'be', 'bg', 'bn', 'bpy', 'bs', 'ca', 'chr-US-Qaaa-x-west', 'cmn', 'cmn-latn-pinyin', 'cv', 'cy', 'da', 'de', 'en-us', 'en-029', 'en-gb', 'en-gb-scotland', 'en-gb-x-gbclan', 'en-gb-x-gbcwmd', 'en-gb-x-rp', 'en-us-nyc', 'eo', 'es', 'es-419', 'et', 'eu', 'fa', 'fa-latn', 'fi', 'fr-fr', 'fr-be', 'fr-ch', 'ga', 'gd', 'gn', 'grc', 'gu', 'hak', 'haw', 'he', 'hr', 'ht', 'hu', 'hy', 'hyw', 'ia', 'id', 'io', 'is', 'it', 'jbo', 'ka', 'kk', 'kl', 'kn', 'ko', 'kok', 'ku', 'ky', 'la', 'lb', 'lfn', 'lt', 'ltg', 'lv', 'mi', 'mk', 'ml', 'mr', 'mt', 'my', 'nb', 'nci', 'ne', 'nl', 'nog', 'om', 'or', 'pa', 'pap', 'piqd', 'pl', 'pt', 'pt-br', 'py', 'qdb', 'qu', 'quc', 'qya', 'ro', 'ru', 'ru-lv', 'sd', 'shn', 'si', 'sjn', 'sk', 'sl', 'smj', 'sq', 'sr', 'sv', 'sw', 'ta', 'te', 'th', 'tk', 'tn', 'tr', 'tt', 'ug', 'uk', 'ur', 'uz', 'vi', 'vi-vn-x-central', 'vi-vn-x-south', 'yue']

# def get_espeak_lang_code(context, lang_code):
    # props = context.scene.props
    
    # if props.override_espeak_language_code:
        # return props.espeak_language_code

    # codes = [code for code in valid_espeak_codes if code.startswith(lang_code)]
    # if len(codes) > 0:
        # return codes[0]

    # return "en-us"

        
        
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

use_cached_dialog = True

def get_phonemes_from_file(context, seq):
    #Putting imports here to avoid these libraries slowing down Blender loading addons
    import whisper_timestamped as whisper

    from gruut import sentences
    
    props = context.scene.props
    
    whisper_library_model = props.whisper_library_model
    autodetect_language = props.autodetect_language
    language_code = props.language_code

    path = bpy.path.abspath(seq.sound.filepath)

    md5_hash = md5(path)
    # if use_cached_dialog and md5_hash in phoneme_cache:
    #     return (word_list_info_cache[md5_hash], phoneme_cache[md5_hash], sound_profile_cache[md5_hash])
    
    model = whisper.load_model(whisper_library_model)

    audio = whisper.load_audio(path)
    audio_shaped = whisper.pad_or_trim(audio)
    
    #Find audio volume per frame
    audio_data = np.array(audio) * seq.volume
    volume_per_frame = max_values_in_partitions(audio_data, seq.frame_duration)
    

    final_language_code = language_code
    
    if autodetect_language:
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio_shaped).to(model.device)

        # detect the spoken language
        _, probs = model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")
        final_language_code = max(probs, key=probs.get)

    
    whisper_result = whisper.transcribe(model, audio, language=final_language_code)

    #print(json.dumps(whisper_result, indent = 2, ensure_ascii = False))
    
#    print("Audio source: ", path)
    print("Text: ", whisper_result["text"])

    word_list = []
    word_list_info = []
    for seg in whisper_result["segments"]:
        if "words" in seg:
            for word in seg["words"]:
                word_list.append(word["text"])
                word_list_info.append(word)
                
            #print("word %s %f %f" % (word["text"], word["start"], word["end"]))
        else:
            #https://jrgraphix.net/r/Unicode/
            #2E80 — 2EFF  	CJK Radicals Supplement
            #3000 — 303F  	CJK Symbols and Punctuation
            #3300 — 33FF  	CJK Compatibility
            #3400 — 4DBF  	CJK Unified Ideographs Extension A
            #4E00 — 9FFF  	CJK Unified Ideographs

            #regex.search(r'\p{Han}', ipath)
            #regex.findall(r'\p{Han}+', ipath)
            #re.search(u'[\u4e00-\u9fff]', x)

            # for ch in seg["text"]:
            #      print(ch, " ", hex(ord(ch)))
            #      pass
            
            # seg["text"]
            # seg["start"]
            # seg["end"]
            pass


    
    
    phoneme_word_list = []
    for word_src in word_list:
        for sent in sentences(word_src, lang=final_language_code):
            phonemes = []
            for word in sent:
                if word.phonemes:
                    phonemes += word.phonemes

            phoneme_word_list.append(phonemes)


    word_list_info_cache[md5_hash] = word_list_info
    phoneme_cache[md5_hash] = phoneme_word_list
    sound_profile_cache[md5_hash] = volume_per_frame
    
    return (word_list_info, phoneme_word_list, volume_per_frame)


def set_target_keyframe(tgt_curve, frame, value, interp_type):
    tgt_kf = tgt_curve.keyframe_points.insert(frame = frame, value = value)

    match interp_type:
        case "constant":
            tgt_kf.interpolation = 'CONSTANT'
        case "linear":
            tgt_kf.interpolation = 'LINEAR'
        case _:
        #case "bezier":
            tgt_kf.interpolation = 'BEZIER'
        # case _:
        #     tgt_kf.interpolation = src_kf.interpolation
        
    # tgt_kf.easing = src_kf.easing
    # tgt_kf.handle_left = src_kf.handle_left
    # tgt_kf.handle_right = src_kf.handle_right
    # tgt_kf.period = src_kf.period

    return tgt_kf

def get_or_create_fcurve(tgt_action, data_path, array_index, group):
    tgt_curve = tgt_action.fcurves.find(data_path, index = array_index)
    if not tgt_curve:
        tgt_curve = tgt_action.fcurves.new(data_path, index = array_index)
        if group and group.name in tgt_action.groups:
            tgt_curve.group = tgt_action.groups[group.name]

    return tgt_curve

def render_lipsync_to_action(context, tgt_action, seq):

    props = context.scene.props
    
    
    key_interpolation = props.key_interpolation
    attenuation = props.attenuation
    attenuate_volume = props.attenuate_volume
    word_pad_frames = props.word_pad_frames
    silence_cutoff = props.silence_cutoff
    limit_pps = props.limit_pps
    phonemes_per_second = props.phonemes_per_second

    fps = context.scene.render.fps

    #path = bpy.path.abspath(seq.sound.filepath)
    #print("Processing audio file ", path)
    #print("Parsing track: ", seq.name)        
    
    phoneme_timings = []
    word_list_info, phoneme_word_list, sound_profile = get_phonemes_from_file(context, seq)

    update_phoneme_group_pose_list(context)
    
    tgt_action.fcurves.clear()
    for marker in tgt_action.pose_markers.values():
        tgt_action.pose_markers.remove(marker)

    phoneme_table = load_phoneme_table(context)

    phoneme_hash = {}
    for info in phoneme_table["phonemes"]:
        #print("Adding phoneme ", info)
        phoneme_hash[info["code"]] = info

    #Map group names to pose actions
    group_pose_hash = {}
    for pose_props in props.phoneme_poses:
        group_pose_hash[pose_props.group] = pose_props.pose

    seq_time_start = seq.frame_offset_start / fps
    seq_time_end = (seq.frame_offset_start + seq.frame_final_duration) / fps

    #print("seq_time_start ", seq_time_start, " seq_time_end ", seq_time_end)
    #final_word = None
    
    for pw_idx, pw_word in enumerate(phoneme_word_list):
        word = word_list_info[pw_idx]
        #print("word ", word)
        #print("pw_word", pw_word)
        
        word_start_time = word["start"]
        word_end_time = word["end"]

        #Adjust start frame to skip silence
        word_start_frame = int(word_start_time * fps)
        word_end_frame = int(word_end_time * fps)
        while sound_profile[word_start_frame] < silence_cutoff and word_start_frame < word_end_frame:
            word_start_frame += 1
            word_start_time = word_start_frame / float(fps)
        

        word_time_span = word_end_time - word_start_time

        if word_end_time < seq_time_start or word_start_time > seq_time_end:
            #print("skip")
            continue
        
        #final_word = word
        
        phonemes = pw_word
        #phonemes = pw_word.split(' ')
        #num_keys = len(phonemes)

        if pw_idx == 0:
            phoneme_timings.append({"group": "rest", "frame": int(word_start_time * fps) - word_pad_frames})
        else:
            prev_word = word_list_info[pw_idx - 1]
            prev_word_end_time = prev_word["end"]

            prev_end_frame = int(prev_word_end_time * fps)
            cur_start_frame = int(word_start_time * fps)
            if cur_start_frame > prev_end_frame + word_pad_frames:
                phoneme_timings.append({"group": "rest", "frame": prev_end_frame})
                phoneme_timings.append({"group": "rest", "frame": cur_start_frame - word_pad_frames})
            elif cur_start_frame > prev_end_frame + 1:
                phoneme_timings.append({"group": "rest", "frame": int((cur_start_frame + prev_end_frame) / 2)})
        
        for p_idx, ele in enumerate(phonemes):
            ele = ele.replace("ˈ", "")
            ele = ele.replace("ˌ", "")
            
            if not ele in phoneme_hash:
                print("Missing phoneme: \"%s\"" % ele)
                continue
            
            group_name = phoneme_hash[ele]["group"]
            #print("group_name " , group_name)
            if not group_name in group_pose_hash:
                continue

            src_action = group_pose_hash[group_name]
            if not src_action:
                continue
            
            phone_time = word_start_time + word_time_span * (float(p_idx) / len(phonemes))
            #print("p_time ", p_time, " time_start ", time_start, " time_end ", time_end)
                
            phoneme_timings.append({"group": group_name, "time": phone_time, "frame": int(phone_time * fps)})

    if len(phoneme_timings) == 0:
        #No phonemes - skip
        return

    #Add final rest after final word
    if len(word_list_info) > 0:
        end_time = word_list_info[-1]["end"]
        phoneme_timings.append({"group": "rest", "frame": int(end_time * fps)})

    #print("phoneme_timings ", phoneme_timings)
    
    # Reduce phonemes
    if limit_pps:
        
        last_phoneme_time = 0
        last_group = None
        new_timings = []
        
        for pt in phoneme_timings:
            if pt["group"] == "rest":
                new_timings.append(pt)
                last_group = pt
            elif last_group and last_group["group"] == pt["group"]:
                continue
            else:
                if pt["time"] - last_phoneme_time >= 1.0 / phonemes_per_second:
                    new_timings.append(pt)
                    last_phoneme_time = pt["time"]
                    last_group = pt
        
        phoneme_timings = new_timings
        
    
    # Write phoneme keyframes
    for idx, phone_timing in enumerate(phoneme_timings):
        #print(phone_timing)
                        
        group_name = phone_timing["group"]
        #print("group_name " , group_name)
        if not group_name in group_pose_hash:
            continue
        
        src_action = group_pose_hash[group_name]
        if not src_action:
            continue
            
        marker = tgt_action.pose_markers.new(group_name)
        # if phone_timing["time"] > 2:
        #     pass
        #frame = int(phone_timing["time"] * context.scene.render.fps)
        marker.frame = phone_timing["frame"]
        #print("phoneme ", phone_timing)
        #print("src_action.name " + src_action.name)
        
        #Ensure groups are present
        for src_group in src_action.groups:
            if not src_group.name in tgt_action.groups:
                tgt_action.groups.new(src_group.name)
        
        #Attenuation interp
        grouped_fcurves = [[k, list(g)] for k, g in itertools.groupby(src_action.fcurves, lambda fc: fc.data_path.rsplit(".", 1)[1])]
        for fcurve_group in grouped_fcurves:
            match fcurve_group[0]:
                case 'location':
                    # if len(fcurve_group[1]) <= 2:
                    #     pass
                    for src_curve in fcurve_group[1]:

                        tgt_curve = get_or_create_fcurve(tgt_action, src_curve.data_path, src_curve.array_index, src_curve.group)

                        range = src_action.curve_frame_range
                        #print("range ", range)

                        src_frames = [k.co[0] for k in src_curve.keyframe_points]

                        for frame in src_frames:
                            x = src_curve.evaluate(frame)
                            if x > 0.1:
                                pass

                            tgt_frame = frame - range[0] + phone_timing["frame"]

                            # if tgt_frame > 1350:
                            #     pass

                            atten = attenuation
                            if attenuate_volume:
                                index = int(min(max(tgt_frame, 0), len(sound_profile) - 1))
                                vol_atten = sound_profile[index]
                                atten *= vol_atten

                            set_target_keyframe(tgt_curve, tgt_frame, x * atten, key_interpolation)

                case 'rotation_euler':
                    for src_curve in fcurve_group[1]:

                        tgt_curve = get_or_create_fcurve(tgt_action, src_curve.data_path, src_curve.array_index, src_curve.group)

                        range = src_action.curve_frame_range

                        src_frames = [k.co[0] for k in src_curve.keyframe_points]

                        for frame in src_frames:
                            x = src_curve.evaluate(frame)
                            

                            tgt_frame = frame - range[0] + phone_timing["frame"]
                            atten = attenuation

                            set_target_keyframe(tgt_curve, tgt_frame, x * atten, key_interpolation)

                case 'rotation_quaternion':
                    if len(fcurve_group[1]) < 3:
                        for src_curve in fcurve_group[1]:

                            tgt_curve = get_or_create_fcurve(tgt_action, src_curve.data_path, src_curve.array_index, src_curve.group)
                            range = src_action.curve_frame_range

                            src_frames = [k.co[0] for k in src_curve.keyframe_points]

                            for frame in src_frames:
                                tgt_frame = frame - range[0] + phone_timing["frame"]

                                value = src_curve.evaluate(frame)

                                src_vec = value
                                
                                set_target_keyframe(tgt_curve, tgt_frame, value, key_interpolation)
                    else:
                        src_curve_w = fcurve_group[1][0]
                        src_curve_x = fcurve_group[1][1]
                        src_curve_y = fcurve_group[1][2]
                        src_curve_z = fcurve_group[1][3]

                        tgt_curve_w = get_or_create_fcurve(tgt_action, src_curve_w.data_path, src_curve_w.array_index, src_curve_w.group)
                        tgt_curve_x = get_or_create_fcurve(tgt_action, src_curve_x.data_path, src_curve_x.array_index, src_curve_x.group)
                        tgt_curve_y = get_or_create_fcurve(tgt_action, src_curve_y.data_path, src_curve_y.array_index, src_curve_y.group)
                        tgt_curve_z = get_or_create_fcurve(tgt_action, src_curve_z.data_path, src_curve_z.array_index, src_curve_z.group)

                        range = src_action.curve_frame_range

                        src_frames = sorted(list(set([k.co[0] for k in src_curve_w.keyframe_points] \
                                            + [k.co[0] for k in src_curve_x.keyframe_points] \
                                            + [k.co[0] for k in src_curve_y.keyframe_points] \
                                            + [k.co[0] for k in src_curve_z.keyframe_points])))

                        for frame in src_frames:
                            w = src_curve_w.evaluate(frame)
                            x = src_curve_x.evaluate(frame)
                            y = src_curve_y.evaluate(frame)
                            z = src_curve_z.evaluate(frame)

                            tgt_frame = frame - range[0] + phone_timing["frame"]
                            atten = attenuation
                            if attenuate_volume:
                                index = int(min(max(tgt_frame, 0), len(sound_profile) - 1))
                                vol_atten = sound_profile[index]
                                atten *= vol_atten
                            atten = min(max(atten, 0), 1)

                            identity_quat = mathutils.Quaternion()
                            src_quat = mathutils.Quaternion([w, x, y, z])
                            eval_quat = identity_quat.slerp(src_quat, atten)
                            
                            set_target_keyframe(tgt_curve_w, tgt_frame, eval_quat.w, key_interpolation)
                            set_target_keyframe(tgt_curve_x, tgt_frame, eval_quat.x, key_interpolation)
                            set_target_keyframe(tgt_curve_y, tgt_frame, eval_quat.y, key_interpolation)
                            set_target_keyframe(tgt_curve_z, tgt_frame, eval_quat.z, key_interpolation)
                case 'scale':
                    for src_curve in fcurve_group[1]:
                        tgt_curve = get_or_create_fcurve(tgt_action, src_curve.data_path, src_curve.array_index, src_curve.group)

                        range = src_action.curve_frame_range

                        src_frames = [k.co[0] for k in src_curve.keyframe_points]

                        for frame in src_frames:
                            x = src_curve.evaluate(frame)

                            tgt_frame = frame - range[0] + phone_timing["frame"]
                            atten = attenuation
                            if attenuate_volume:
                                index = int(min(max(tgt_frame, 0), len(sound_profile) - 1))
                                vol_atten = sound_profile[index]
                                atten *= vol_atten

#                            identity = mathutils.Vector([1, 1, 1])
#                            src_vec = mathutils.Vector([x, y, z])
                        
#                            eval_vec = identity.lerp(src_vec, atten)
                            eval_vec = atten + (1 - atten) * x
                            
                            set_target_keyframe(tgt_curve, tgt_frame, eval_vec, key_interpolation)

                case _:
                    for src_curve in fcurve_group[1]:

                        tgt_curve = get_or_create_fcurve(tgt_action, src_curve.data_path, src_curve.array_index, src_curve.group)
                        range = src_action.curve_frame_range

                        src_frames = [k.co[0] for k in src_curve.keyframe_points]

                        for frame in src_frames:
                            tgt_frame = frame - range[0] + phone_timing["frame"]

                            value = src_curve.evaluate(frame)

                            src_vec = value
                            
                            set_target_keyframe(tgt_curve, tgt_frame, value, key_interpolation)





#------------------------------------------
# Lipsync to rig NLA

class PLUGIN_OT_ParrotRenderLipsyncToRigNla(bpy.types.Operator):
    """
    Parrot Lipsync To Nla
    """
    bl_label = "Render Lipsync to Object NLA"
    bl_idname = "parrot.render_lipsync_to_object_nla"
    
    def execute(self, context):
        for mod in ['whisper_timestamped', 'gruut']:
            if not is_library_installed(mod):
#            if not importlib.machinery.PathFinder().find_spec(mod):
            #if not importlib.util.find_spec(mod):
                self.report({"ERROR"}, mod + " not installed")
                return {'CANCELLED'}
            

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
        for mod in ['whisper_timestamped', 'gruut']:
            if not is_library_installed(mod):
                self.report({"ERROR"}, mod + " not installed")
                return {'CANCELLED'}
            
    
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

        ##############
        
            # seq.frame_duration
            # #Timeline position
            # seq.frame_final_start
            # seq.frame_final_end

            # #Frames in track being rendered
            # seq.frame_offset_start
            # seq.frame_offset_end
            
            # #bpy.type.Sound
            # seq.sound.filepath
            
            
        
        return {'FINISHED'}


class PLUGIN_OT_ParrotReloadPhonemeTable(bpy.types.Operator):
    """
    Install Whisper
    """
    bl_label = "Reload Phoneme Table"
    bl_idname = "parrot.reload_phoneme_table"
    
    def execute(self, context):
        update_phoneme_group_pose_list(context)

        return {'FINISHED'}





class ParrotAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__


    def add_installer_button(self, context, layout, lib_name):
        if is_library_installed(lib_name):
            op_props = layout.operator(LibraryUninstaller.bl_idname, text="Uninstall " + lib_name)
            op_props.lib_name = lib_name
        else:
            op_props = layout.operator(LibraryInstaller.bl_idname, text="Install " + lib_name)
            op_props.lib_name = lib_name

    def draw(self, context):
    
        layout = self.layout
        layout.use_property_split = True
        #layout.prop(self, 'port')
          
        self.add_installer_button(context, layout, "whisper_timestamped")
#        self.add_installer_button(context, layout, "phonemizer")
#        self.add_installer_button(context, layout, "espeak_phonemizer")
        self.add_installer_button(context, layout, "gruut")

#        self.add_installer_button(context, layout, "jphones")
        
        box_gruut = layout.box()
        box_gruut.label(text="Gruut language packs:")

        gruut_lang_packs = [
            ["Arabic", "gruut-lang-ar"],
            ["Czech", "gruut-lang-cs"],
            ["German", "gruut-lang-de"],
            ["English", "gruut-lang-en"],
            ["Spanish", "gruut-lang-es"],
            ["Farsi/Persian", "gruut-lang-fa"],
            ["French", "gruut-lang-fr"],
            ["Italian", "gruut-lang-it"],
            ["Luxembourgish", "gruut-lang-lb"],
            ["Dutch", "gruut-lang-nl"],
            ["Portuguese", "gruut-lang-pt"],
            ["Russian", "gruut-lang-ru"],
            ["Sweedish", "gruut-lang-sv"],
            ["Swahili", "gruut-lang-sw"],
        ]

        for tuple in gruut_lang_packs:
            row = box_gruut.row()
            row.label(text=tuple[0])
            self.add_installer_button(context, row, tuple[1])

        # box_other = layout.box()
        # box_other.label(text="Other languages:")

        # other_lang_packs = [
        #     ["Japanese", "jphones"],
        # ]

        # for tuple in other_lang_packs:
        #     row = box_other.row()
        #     row.label(text=tuple[0])
        #     self.add_installer_button(context, row, tuple[1])
        

class LibraryInstaller(bpy.types.Operator):
    bl_idname = "parrot.library_installer"
    bl_label = "Install python library"

    lib_name: bpy.props.StringProperty(
            name="Library name",
            description="Name of library to be installed",
            default="whisper_timestamped"
        )

    def execute(self, context):
        python = os.path.abspath(sys.executable)
        
        self.report({'INFO'}, "Installing '" + str(self.lib_name) + "' package.")
        # Verify 'pip' package manager is installed.
        try:
            context.window.cursor_set('WAIT')
            subprocess.call([python, "-m", "ensurepip"])
            # Upgrade 'pip'. This shouldn't be needed.
            # subprocess.call([python, "-m", "pip", "install", "--upgrade", "pip", "--yes"])
        except Exception:
            self.report({'ERROR'}, "Failed to verify 'pip' package manager installation.")
            return {'FINISHED'}
        finally:
            context.window.cursor_set('DEFAULT')
        
        # Install 'whisper_timestamped' package.
        try:
            context.window.cursor_set('WAIT')
            subprocess.call([python, "-m", "pip", "install", str(self.lib_name)])
        except Exception:
            self.report({'ERROR'}, "Failed to install '" + str(self.lib_name) + "' package.")
            return {'FINISHED'}
        finally:
            context.window.cursor_set('DEFAULT')
        
        self.report({'INFO'}, "Successfully installed '" + str(self.lib_name) + "' package.")
        return {'FINISHED'}
        
class LibraryUninstaller(bpy.types.Operator):
    bl_idname = "parrot.library_uninstaller"
    bl_label = "Uninstall python library"

    lib_name: bpy.props.StringProperty(
            name="Library name",
            description="Name of library to be installed",
            default="whisper_timestamped"
        )

    def execute(self, context):
        python = os.path.abspath(sys.executable)
        self.report({'INFO'}, "Uninstalling '" + self.lib_name + "' package.")
        
        # Uninstall package.
        try:
            context.window.cursor_set('WAIT')
            subprocess.call([python, "-m", "pip", "uninstall", self.lib_name, "--yes"])
        except Exception:
            self.report({'ERROR'}, "Failed to uninstall '" + self.lib_name + "' package.")
            return {'FINISHED'}
        finally:
            context.window.cursor_set('DEFAULT')
        
        self.report({'INFO'}, "Successfully uninstalled '" + self.lib_name + "' package.")
        return {'FINISHED'}

