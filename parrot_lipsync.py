import subprocess
import sys
import os
 
#PS C:\Program Files\Blender Foundation\Blender 4.0\4.0\python\bin> .\python.exe -m pip install --upgrade whisper_timestamped
#PS C:\Program Files\Blender Foundation\Blender 4.0\4.0\python\bin> .\python.exe -m pip install --upgrade phonemizer
 
def install_whisper():
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    target = os.path.join(sys.prefix, 'lib', 'site-packages')
     
    subprocess.call([python_exe, '-m', 'ensurepip'])
    subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])

    #example package to install (SciPy):
    #subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'scipy', '-t', target])
    subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'whisper-timestamped', '-t', target])
    
    
    
path = "D:\\dev\\video\\blenderTutorials\\2023-11-30-terrainShaderGameEngine\\recordings\\audio\\00_intro.ogg"
    
import whisper_timestamped as whisper

from phonemizer.backend import EspeakBackend
from phonemizer.punctuation import Punctuation
from phonemizer.separator import Separator

#audio = whisper.load_audio("AUDIO.wav")
audio = whisper.load_audio(path)

model = whisper.load_model("tiny", device="cpu")
#model = whisper.load_model("facebook/wav2vec2-large-960h-lv60-self", device="cpu")

result = whisper.transcribe(model, audio, language="en")

import json
print(json.dumps(result, indent = 2, ensure_ascii = False))

#import scipy

#PHONEMIZER_ESPEAK_LIBRARY = C:\Program Files\eSpeak NG\libespeak-ng.dll
#PHONEMIZER_ESPEAK_PATH = C:\Program Files\eSpeak NG

from phonemizer.backend.espeak.wrapper import EspeakWrapper
_ESPEAK_LIBRARY = 'C:\Program Files\eSpeak NG\libespeak-ng.dll'
EspeakWrapper.set_library(_ESPEAK_LIBRARY)

# initialize the espeak backend for English
backend = EspeakBackend('en-us')

# separate phones by a space and ignoring words boundaries
separator = Separator(phone=' ', word=None)

result = backend.phonemize(["alpha beta gamma blender"], separator=separator, strip=True)
     
print(result)
print('DONE')