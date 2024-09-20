from pocketsphinx import AudioFile

for phrase in AudioFile("result.wav"): 
#for phrase in AudioFile("goforward.raw"): 
    print(phrase)



# from os import path 
# from pydub import AudioSegment 
  
# # assign files 
# input_file = "amores_17_lawrence_128kb.mp3"
# output_file = "result.wav"
  
# # convert mp3 file to wav file 
# sound = AudioSegment.from_mp3(input_file) 
# sound.export(output_file, format="wav") 

