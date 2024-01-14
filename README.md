# Parrot Lipsync

This is an addon for Blender that lets you automically generate lipsync data from audio tracks.  It uses the Whisper AI library to turn audio into words, and then Espeak to turn words into phonemes.


## Installation

You will need to have eSpeak installed on your system for Parrot Lipsync to work.  You can download it form its website:

https://github.com/espeak-ng/espeak-ng/blob/master/docs/guide.md

The addon should automatically install Whisper if it is not already installed - however, if you wish to install Whisper manually, open a terminal window and go into your Blender installation's python directory (on Windows it should be something like `C:\Program Files\Blender Foundation\Blender 4.0\4.0\python\bin`).  Then issue the following commands:

```
./python.exe -m pip install --upgrade whisper_timestamped
./python.exe -m pip install --upgrade phonemizer
./python.exe -m pip install --upgrade gruut
```

You can install the addon by opening Blender's Edit/Preferences menu, opening the Addons section, clicking the Install button and then browsing to the parrot_lipsync.py file.  Once installed, make sure that you check the box to enable it.  It should now appear in the viewport right hand tab menu.

Before you can use the addon, you need to set the path where it can find the eSpeak library file.  On windows this will be the `libespeak-ng.dll` file which has a default install location of `C:\Program Files\eSpeak NG\libespeak-ng.dll`.

## Acknowledgements

Whisper AI
https://github.com/openai/whisper

eSpeak
https://github.com/espeak-ng/espeak-ng

Blender Base Meshes:
https://studio.blender.org/training/stylized-character-workflow/base-meshes/


## Support

If you found this software useful, please consider buying me a coffee on Kofi.  Every contribution helps me to make more software:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y43J6OB)

