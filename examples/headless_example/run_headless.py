# To run Blender in headless mode from the command line:
#   blender -b headless_demo.blend -P run_headless.py
#
# (If running on Windows, run in Windows Terminal.  PowerShell does not work.)

import bpy

print("++++++++++++Test parrot headless")

# Set Parrot operator properties
bpy.context.scene.props.target_object = bpy.data.objects['rig']

# Generate the lipsync
bpy.ops.parrot.render_lipsync_to_object_nla()

# Save the result
bpy.ops.wm.save_as_mainfile(filepath="//headless_result.blend")

print("------------Test parrot headless")