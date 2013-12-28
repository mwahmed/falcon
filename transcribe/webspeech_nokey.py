#!/bin/python

import httplib
import json
import sys
import random
import urllib2

#Source http://www.athoughtabroad.com/2013/05/22/using-google-s-speech-recognition-web-service-with-python
def speech_to_text(audio,rate='44100'):
     url = "www.google.com"
     path = "/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en"
     headers = { "Content-type": "audio/x-flac;rate="+rate };
     params = {"xjerr": "1", "client": "chromium"}
     conn = httplib.HTTPSConnection(url)
     conn.request("POST", path, audio, headers)
     response = conn.getresponse()
     ret = []
     while True:
         data = response.read()
	 if not data: break
         jsdata = json.loads(data)
         ret.append(jsdata)
     return ret
     #return jsdata["hypotheses"][0]["utterance"]

def generate_pair(length):
    c = '0123456789'
    s = []

    for i in range(length):
        s.append(c[random.randint(0, len(c)-1)])
    return ''.join(s)

def speech_to_text2(audio,rate='44100', lang='en-US', key='AIzaSyDjc6ZctgLju0LyWXQCH9yiEPHg2ehk_RY'):
     #Attempt at using full duplex api with key, failed
     url = "www.google.com"
     
     pair=generate_pair(16)
     
     path2 = '/speech-api/full-duplex/v1/'    
     up = path2 + 'up?lang=' + lang + '&lm=dictation&client=chromium&pair=' +  pair + '&key=' + key
     down = path2 + "down?pair="+pair

     path = "/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en"
     headers = { "Content-type": "audio/x-flac;rate="+rate }
     params = {"xjerr": "1", "client": "chromium"}
     conn = httplib.HTTPSConnection(url)
     conn.request("POST", path2, audio, headers)
     response = conn.getresponse()
     while True:
         data = response.read()
	 if not data: break
         jsdata = json.loads(data)
         print jsdata
     
     return True 

def speech_to_text3(audio, rate="44100"):
	try:
		filename = sys.argv[1]
	except IndexError:
		print "Invalid argument"
		sys.exit(1)

	f = open(audio)
	data = f.read()
	f.close()

	req = urllib2.Request('https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US', data=audio, headers={'Content-type': 'audio/x-flac; rate='+rate })

	try:
		ret = urllib2.urlopen(req)
	except urllib2.URLError:
		print "Error Transcribing Voicemail"
		sys.exit(1)
	
	rr = ret.read()
	print rr
	
	text = json.loads(rr)['hypotheses'][0]['utterance']
	print text


if __name__ == "__main__":
     if len(sys.argv) != 2 or "--help" in sys.argv:
         print "Usage: webspeech_nokey <flac-audio-file>"
         sys.exit(1)
     else:
         filename = sys.argv[1]
         with open(filename, "r") as f:
             speech = f.read()
         text = speech_to_text(speech)
         f.close()
         print text
