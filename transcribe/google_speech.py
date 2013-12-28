import webspeech_nokey as speech
import webspeech_key as speech_key
import sys
import os 
import glob
import subprocess

def print_list(arr):
     for a in arr:
         print a

def keyless_trans(filename):
    #Test keyless google speech api
    audiofile = filename #sys.argv[1]
    transcript1=None
    with open(audiofile, "r") as audio:
          try: 
	      transcript1 = speech.speech_to_text(audio, '44100')
	  except:
	      print "error processing above file (keyless transcription)"
	      return None
    return transcript1 


def key_trans(filepath): 
    #Test keyless google speech api
    speech_obj = speech_key.google_stt_stream(filepath)
    speech_obj.start()
    speech_obj.stop()
    speech_obj.format_output()
    return speech_obj.output 

if __name__ == "__main__":
    #path_to_audio="../../audiosamples/"
    #for f in os.listdir(path_to_audio):
    if len(sys.argv) == 2:
        print key_trans(sys.argv[1])
        print_list(keyless_trans(sys.argv[1]))
    else:
        lst =  glob.glob("*flac")
        for f in lst:
        	print key_trans(sys.argv[1])
        	print_list(keyless_trans(sys.argv[1]))
