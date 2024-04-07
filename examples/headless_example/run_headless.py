# To run from command line:
#   blender -b headless_demo.blend -P run_headless.py

import bpy

print("++++++++++++Test parrot headless")

# Set Parrot operator properties
bpy.context.scene.props.target_object = bpy.data.objects['rig']

# Generate the lipsync
bpy.ops.parrot.render_lipsync_to_object_nla()

# Save the result
bpy.ops.wm.save_as_mainfile(filepath="//headless_result.blend")

print("------------Test parrot headless")