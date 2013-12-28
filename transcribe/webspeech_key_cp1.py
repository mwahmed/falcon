import sys
import requests
import random
import urllib2

from threading import Thread
from Queue import Queue, Empty
from time import sleep

import json

#Source https://gist.github.com/offlinehacker/5780124

class google_stt_stream(object):
    def __init__(self, filename, rate="44100", key="AIzaSyDjc6ZctgLju0LyWXQCH9yiEPHg2ehk_RY"):
        self.write_queue = Queue()
        self.keep_streaming = True
        self.audiofile = filename 	

        self.upstream_url = "https://www.google.com/speech-api/full-duplex/v1/up?key=%(key)s&pair=%(pair)s&lang=en-US&maxAlternatives=20&client=chromium&continuous&interim"
        self.upstream_headers = {'content-type': 'audio/x-flac; rate={}'.format(rate)}
        self.downstream_url = "https://www.google.com/speech-api/full-duplex/v1/down?pair=%(pair)s"
        self.api_key = key 
        self.output=[]

    def generate_request_key(self):
        return hex(random.getrandbits(64))[2:-1]
 
    def start(self):
        pair = self.generate_request_key()
        upstream_url = self.upstream_url % {"pair": pair, "key": self.api_key}
        downstream_url = self.downstream_url % {"pair": pair, "key": self.api_key}
 
        self.session = requests.Session()
        self.upstream_thread = Thread(target=self.upstream, args=(upstream_url,))
        self.downstream_thread = Thread(target=self.downstream, args=(downstream_url,))
 
        self.downstream_thread.start()
        self.upstream_thread.start()
 
    def stop(self):
        #print "Waiting write_queue to write all data"
        self.write_queue.join()
        #print "Queue empty"
        sleep(30)
 
        self.keep_streaming=False
        self.upstream_thread.join()
        self.downstream_thread.join()
 
    def write_data(self, data):
        self.write_queue.put(data)
 
    def upstream(self, url):
        #print 
	self.session.post(url, headers=self.upstream_headers, files={self.audiofile: open(self.audiofile, 'rb')})
 
    def downstream(self, url):
        r = self.session.get(url, stream=True)
        while self.keep_streaming:
            try:
                for line in r.iter_content():
                    if not self.keep_streaming:
                        break
                    if line:
                        self.output.append(line)
		        sys.stdout.write(line)
			#print line
            except Exception as e:
                print "Exception %s, restarting" %e
                self.keep_streaming = False
                self.upstream_thread.join()
                self.keep_streaming = True
                self.start()
                return
 
        print "end"

    def format_output(self):
        #Gets json objects
     	json_strings=''.join(self.output).split("\n")
	#Gets python objects
	py_objs =  [json.loads(j)['result'] for j in json_strings if j ]
	#get non-empty lists
	contain_data = filter(lambda lst: len(lst)>0, py_objs)        
	#flat contain_data list
        flat = [ item for lst in contain_data for item in lst ] 
	#Return map of confidence level to transcription
	formatted = [ self.format_helper(resp) for resp in flat ]
        #Flatten formatted
	self.output = []
	for f in formatted:
	    if type(f) == list:
	         self.output += f
            else:
	         self.output.append(f)

    def format_helper(self,resp):
        #Treats stability and confidence as identical
        conf = -1
	alt =[]
	if resp.has_key('stability'): 
	    conf = resp['stability']
	elif resp.has_key('confidence'):
	    conf= resp['confidence']
        if resp.has_key('transcript'):
	    return (conf, resp['transcript'])
        elif resp.has_key('alternative'):
	    alt = resp['alternative']
            if len(alt) == 0 : 
	        return None
	    elif len(alt) == 1:
	        type(alt)
	        if alt[0].has_key('transcript'):
	            return (conf,alt[0]['transcript'])
		else:
		    return None
	    else:
	        return [ self.format_helper(a) for a in alt ] 
        else:
	        return None

if __name__ == "__main__":
    filename=sys.argv[1]
    stt = google_stt_stream(filename)
    stt.start()
    stt.stop()
    stt.format_output()
    #print stt.output
