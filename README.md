# Parrot Lipsync

This is an addon for Blender that lets you automically generate lipsync data from audio tracks.  It uses the Whisper AI library to turn audio into words, and then Espeak to turn words into phonemes.


## Installation

Parrot Lipsync relies on you having some other applicatiions already installed on your computer.

### Install Ffmpeg

Ffmpeg is a popular library that lets you read and write many popular media files.  It needs to be accessible from the command line.

Open a command prompt and type the following to see if it is already installed:

```
ffmpeg -version
```

If ffmpeg has not been found, you will need to install it.

#### Windows Installation

Download the latest binary from

https://github.com/BtbN/FFmpeg-Builds/releases

Unzip it and add the path of its `/bin` directory to your system's PATH environment variable.

#### Mac Installation

You can install and update ffmpeg using Homebrew

```
brew update
brew upgrade
brew install ffmpeg
```

### Install Whisper and Gruut

You will need to install some Python extensions to your Blender distribution of Python.  Blender uses its own copy of Python, so you will need to install these packages there even if you already have Python installed elsewhere on your system.

Open a terminal window and go into your Blender installation's python directory (on Windows it should be something like `C:\Program Files\Blender Foundation\Blender 4.0\4.0\python\bin`).  Then issue the following commands:

```
./python.exe -m pip install --upgrade numpy
./python.exe -m pip install --upgrade whisper_timestamped
./python.exe -m pip install --upgrade gruut
```

### Indstalling the ParrotLipsync addon

You can install the addon by 
* opening Blender's `Edit/Preferences` menu
* opening the Addons section
* clicking the Install button 
* browsing to the `parrot_lipsync.zip` file

Once installed, make sure that you check the box to enable it.  A new tab will appear in the viewport right hand tab menu.


## Acknowledgements

Whisper AI
https://github.com/openai/whisper

Gruut
https://rhasspy.github.io/gruut/index.html

Blender Base Meshes:
https://studio.blender.org/training/stylized-character-workflow/base-meshes/


## Support

If you found this software useful, please consider buying me a coffee on Kofi.  Every contribution helps me to make more software:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y43J6OB)

