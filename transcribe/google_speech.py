import webspeech_nokey as speech
import webspeech_key as speech_key
import sys
import os 
import glob
import subprocess

"""
Helper function- prints list
@params
    lst - list to be printed
"""
def print_list(lst):
    for l in lst: print l

"""
Performs transcription of audio file
    Does not require API key. Only works
    for files less than 5s
@params 
    filename- path to input audio file  
@ret= transcription
"""
def keyless_trans(filename):
    audiofile = filename 
    transcript1=None
    with open(audiofile, "r") as audio:
        try: 
            transcript = speech.speech_to_text(audio, ut.file_sampfreq(audio))
        except:
            print "error processing above file (keyless transcription)"
            return None
    return transcript 


"""
Performs transcription of audio file
    Requires API key. 
@params 
    filename- path to input audio file  
@ret= transcription
"""
def key_trans(filepath): 
    speech_obj = speech_key.google_stt_stream(filepath)
    speech_obj.start()
    speech_obj.stop()
    speech_obj.format_output()
    return speech_obj.output 

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print key_trans(sys.argv[1])
    else:
        print "Invalid number of arguments passed"
        raise Exception       

