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
    "category": "View 3D"
}



import subprocess
import sys
import os
import bpy

# import whisper_timestamped as whisper

# from phonemizer.backend import EspeakBackend
# from phonemizer.punctuation import Punctuation
# from phonemizer.separator import Separator
# from phonemizer.backend.espeak.wrapper import EspeakWrapper

import json


# def install_whisper():
    # python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    # target = os.path.join(sys.prefix, 'lib', 'site-packages')
     
    # subprocess.call([python_exe, '-m', 'ensurepip'])
    # subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])

    # #example package to install (SciPy):
    # #subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'scipy', '-t', target])
    # subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'whisper-timestamped', '-t', target])
    
def update_phoneme_table_path(self, context):
    print("--update_phoneme_table_path")
    update_phoneme_group_pose_list(context)
    pass
 
def update_phoneme_group_pose_list(context):
    print("--update_phoneme_group_pose_list")
    phoneme_table = load_phoneme_table(context)
    
    group_list = [info["group"] for info in phoneme_table["phonemes"]]
    group_list = list(dict.fromkeys(group_list))
    group_list.sort()
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
    override_espeak_language_code: bpy.props.BoolProperty(
        name="Specify Espeak Language Code",
        description="If checked, Espeak will use the given code for phonemization.",
        default=False,
    )
    espeak_language_code: bpy.props.StringProperty(
        name="Language code",
        description="Use this to override the language used by the Espeak phonemizer.  'en-us' will work for all languages, although using a more language specific code will give better results for non-english languages.",
        default="en-us"
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
    armature: bpy.props.PointerProperty(
        name = "Armature",
        description = "Armature you wish to apply lipsync to.",
        type=bpy.types.Object
    )
    lipsync_action: bpy.props.PointerProperty(
        name = "Lipsync Action",
        description = "Action lipsync data will be written to.",
        type=bpy.types.Action
    )
    rest_cooldown_time: bpy.props.FloatProperty(
        name="Rest cooldown time",
        default=.5,
    )
    rig_action_suffix: bpy.props.StringProperty(
        name="Action Name Suffix",
        default='_parrot',
    )
    

#------------------------------------------
# Panel

class PLUGIN_PT_ParrotLipsyncPanel(bpy.types.Panel):
    bl_label = "Parrot Lipsync"
    bl_idname = "PLUGIN_PT_parrot_lipsync"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Parrot Lipsync"

    def draw(self, context):
        props = context.scene.props
        
        layout = self.layout

        main_column = layout.column()

        main_column.prop(props, "espeak_path")
        main_column.prop(props, "whisper_library_model")
        main_column.prop(props, "phoneme_table_path")

        main_column.prop(props, "autodetect_language")        
        row = main_column.row()
        row.enabled = not props.autodetect_language
        row.prop(props, "language_code")

        main_column.prop(props, "override_espeak_language_code")
        row = main_column.row()
        row.enabled = props.override_espeak_language_code
        row.prop(props, "espeak_language_code")

        box_single = main_column.box()
        box_single.prop(props, "lipsync_action")
        box_single.operator("plugin.parrot_lipsync_to_action")

        box_create_tracks = main_column.box()
        box_create_tracks.prop(props, "armature")
        box_create_tracks.prop(props, "rig_action_suffix")
        box_create_tracks.operator("plugin.parrot_render_lipsync_to_rig_nla")
        
        main_column.operator("plugin.parrot_reload_phoneme_table")


class PLUGIN_PT_ParrotLipsyncPhonemeGroupPanel(bpy.types.Panel):
    bl_label = "Phoneme Groups"
    bl_idname = "PLUGIN_PT_parrot_lipsync_phoneme_groups"
    bl_parent_id = "PLUGIN_PT_parrot_lipsync"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        props = context.scene.props
        layout = self.layout

        #update_phoneme_group_pose_list(context)
        
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
    bl_idname = "PLUGIN_PT_parrot_lipsync_setup"
    bl_parent_id = "PLUGIN_PT_parrot_lipsync"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        props = context.scene.props
        layout = self.layout

        main_column = layout.column()
        
        main_column.operator("plugin.parrot_install_whisper")
        main_column.operator("plugin.parrot_install_gruut")


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

def render_lipsync_to_action(context, tgt_action, seq):
    #Putting imports here to avoid these libraries slowing down Blender loading addons
    import whisper_timestamped as whisper

    from gruut import sentences

    props = context.scene.props
    
    update_phoneme_group_pose_list(context)
    
    
    whisper_library_model = props.whisper_library_model
    autodetect_language = props.autodetect_language
    language_code = props.language_code
    armature = props.armature
    rest_cooldown_time = props.rest_cooldown_time

    

    tgt_action.fcurves.clear()
    for marker in tgt_action.pose_markers.values():
        tgt_action.pose_markers.remove(marker)

    phoneme_table = load_phoneme_table(context)

    phoneme_hash = {}
    for info in phoneme_table["phonemes"]:
        print("Adding phoneme ", info)
        phoneme_hash[info["code"]] = info

    group_pose_hash = {}
    for pose_props in props.phoneme_poses:
        group_pose_hash[pose_props.group] = pose_props.pose
        
#        print(phoneme_hash)
    
    model = whisper.load_model(whisper_library_model)
            
    path = bpy.path.abspath(seq.sound.filepath)
#            print("Processing ", path)
    
    audio = whisper.load_audio(path)
    audio_shaped = whisper.pad_or_trim(audio)
    
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
    
    print("Parsing track: ", seq.name)
    print("Audio source: ", path)
    print("Text: ", whisper_result["text"])

    #TODO: Need to figure out how to choose proper language library
#            espeak_backend = EspeakBackend(final_language_code)
    
    word_list = []
    word_list_info = []
    for seg in whisper_result["segments"]:
        for word in seg["words"]:
            word_list.append(word["text"])
            word_list_info.append(word)
            
            #print("word %s %f %f" % (word["text"], word["start"], word["end"]))
            #word["text"]
            #word["start"]
            #word["end"]
    
    phoneme_word_list = []
    for word in word_list:
        
        for sent in sentences(word, lang="en-us"):
            phoneme_word_list.append(sent[0].phonemes)
        
    phoneme_timings = []

    seq_time_start = seq.frame_offset_start / context.scene.render.fps
    seq_time_end = (seq.frame_offset_start + seq.frame_final_duration) / context.scene.render.fps

    #print("seq_time_start ", seq_time_start, " seq_time_end ", seq_time_end)

    for pw_idx, pw_word in enumerate(phoneme_word_list):
        word = word_list_info[pw_idx]
        print(word)
        print(pw_word)
        
        word_time_start = word["start"]
        word_time_end = word["end"]
        word_time_span = word_time_end - word_time_start

        if word_time_end < seq_time_start or word_time_start > seq_time_end:
            #print("skip")
            continue
        
        phonemes = pw_word
        #phonemes = pw_word.split(' ')
        num_keys = len(phonemes) + 1

        phoneme_timings.append({"group": "rest", "time": word_time_start})
        
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
            
            p_time = word_time_start + word_time_span * (float(p_idx + 1) / num_keys)
            #print("p_time ", p_time, " time_start ", time_start, " time_end ", time_end)
                
            phoneme_timings.append({"group": group_name, "time": p_time})
#                    phoneme_timings.append([group_name, p_time * context.scene.render.fps])
        
        if pw_idx < len(word_list_info) - 1:
            next_word_start_time = word_list_info[pw_idx + 1]["start"]
            if next_word_start_time - word_time_end > rest_cooldown_time:
        
                phoneme_timings.append({"group": "rest", "time": word_time_end + rest_cooldown_time})
    
    if len(phoneme_timings) == 0:
        #No phonemes - skip
        return

    #Add final rest after final word
    phoneme_timings.append({"group": "rest", "time": word_time_end + rest_cooldown_time})
                
    for idx, p_timing in enumerate(phoneme_timings):
        #print(p_timing)
                        
        group_name = p_timing["group"]
        #print("group_name " , group_name)
        if not group_name in group_pose_hash:
            continue
        
        src_action = group_pose_hash[group_name]
        if not src_action:
            continue
            
        marker = tgt_action.pose_markers.new(group_name)
        marker.frame = int(p_timing["time"] * context.scene.render.fps)
        #print("src_action.name " + src_action.name)
        
        
        group_map = {}
        
        for src_group in src_action.groups:
            if not src_group.name in tgt_action.groups:
                tgt_group = tgt_action.groups.new(src_group.name)
            else:
                tgt_group = tgt_action.groups[src_group.name]
            
            group_map[src_group.name] = tgt_group
        
        for src_curve in src_action.fcurves:
            #print("src_curve.data_path ", src_curve.data_path, src_curve.array_index)
            
            if src_curve.is_empty:
                continue

            tgt_curve = tgt_action.fcurves.find(src_curve.data_path, index = src_curve.array_index)
            if not tgt_curve:
                tgt_curve = tgt_action.fcurves.new(src_curve.data_path, index = src_curve.array_index)
                tgt_curve.group = group_map[src_curve.group.name]
            
            #start_co = curve.keyframe_points[0]
            range = src_action.curve_frame_range
            #print("range ", range)
            for src_kf in src_curve.keyframe_points:
                #co = kf.co
                tgt_kf = tgt_curve.keyframe_points.insert(frame = (src_kf.co[0] - range[0] + int(p_timing["time"] * context.scene.render.fps)), value = src_kf.co[1])
                
                tgt_kf.interpolation = src_kf.interpolation
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
    bl_label = "Render Lipsync to Rig NLA"
    bl_idname = "plugin.parrot_render_lipsync_to_rig_nla"
    
    def execute(self, context):

        props = context.scene.props
        
        armature = props.armature
        rig_action_suffix = props.rig_action_suffix
        
        if not armature:
            self.report({"WARNING"}, "Armature is not set")
            return {'CANCELLED'}

        if not armature.animation_data:
            armature.animation_data_create()
        
        armature.animation_data.use_nla = True
        
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
            
            # if len(armature.animation_data.nla_tracks) == 0:
                # #First track is not used
                # track = armature.animation_data.nla_tracks.new()

            track = armature.animation_data.nla_tracks.new()
            track.strips.new(tgt_action.name, int(seq.frame_start + tgt_action.frame_range[0]), tgt_action)
        
        armature.animation_data.action = None
        
        return {'FINISHED'}


#------------------------------------------
# Lipsync to action

class PLUGIN_OT_ParrotRenderLipsyncToAction(bpy.types.Operator):
    """
    Parrot Lipsync To Action
    """
    bl_label = "Render Lipsync to Action"
    bl_idname = "plugin.parrot_lipsync_to_action"
    
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
    bl_idname = "plugin.parrot_reload_phoneme_table"
    
    def execute(self, context):
        update_phoneme_group_pose_list(context)

        return {'FINISHED'}


class PLUGIN_OT_ParrotInstallWhisper(bpy.types.Operator):
    """
    Install Whisper
    """
    bl_label = "Install/Update Whisper"
    bl_idname = "plugin.parrot_install_whisper"
    
    def execute(self, context):
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        target = os.path.join(sys.prefix, 'lib', 'site-packages')
         
        subprocess.call([python_exe, '-m', 'ensurepip'])
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])

        #example package to install (SciPy):
        #subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'scipy', '-t', target])
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'whisper-timestamped', '-t', target])

        return {'FINISHED'}


class PLUGIN_OT_ParrotInstallGruut(bpy.types.Operator):
    """
    Install Gruut
    """
    bl_label = "Install/Update Gruut"
    bl_idname = "plugin.parrot_install_gruut"
    
    def execute(self, context):
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        target = os.path.join(sys.prefix, 'lib', 'site-packages')
         
        subprocess.call([python_exe, '-m', 'ensurepip'])
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])

        #example package to install (SciPy):
        #subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'scipy', '-t', target])
        subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'gruut', '-t', target])

        return {'FINISHED'}

