import sys
import requests
import random
import urllib2
from threading import Thread
from Queue import Queue, Empty
from time import sleep
import json
import utils as ut

DEBUG =1 

#Source https://gist.github.com/offlinehacker/5780124

class google_stt_stream(object):
    def __init__(self, filename, key="AIzaSyDjc6ZctgLju0LyWXQCH9yiEPHg2ehk_RY"):
        self.write_queue = Queue()
        self.keep_streaming = True
        self.audiofile = filename
        self.rate = ut.file_sampfreq(filename) 	

        #self.upstream_url = "https://www.google.com/speech-api/full-duplex/v1/up?key={}s&pair={}s&lang=en-US&maxAlternatives={}&client=chromium&continuous&interim".format(key, pair, "en-US", 10)  
        self.upstream_url = "https://www.google.com/speech-api/full-duplex/v1/up?key=%(key)s&pair=%(pair)s&lang=en-US&maxAlternatives=20&client=chromium&continuous&interim" 
        self.upstream_headers = {'content-type': 'audio/x-flac; rate={}'.format(self.rate)}
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
                for line in r.iter_lines():
                    if not self.keep_streaming:
                        break
                    if line:
                        self.output.append(line)
		        #sys.stdout.write(line)
			#print line
            except Exception as e:
                #print "Exception %s, restarting" %e
                self.keep_streaming = False
                self.upstream_thread.join()
                self.keep_streaming = True
                self.start()
                return
 
        #print "end"

    def format_output(self):
        #Gets python objects
        try:
            py_objs =  [json.loads(j)['result'] for j in self.output if j ]
            #get non-empty lists
            contain_data = filter(lambda lst: len(lst)>0, py_objs)        
            #flat contain_data list
            #TODO: Fix, this may have performance issue if 
            #	each line is being processed
            #	since some lines will be certainly unneccessary
            flat = [ item for lst in contain_data for item in lst ]

            #Get list of unique/feasible transcriptions
            #conf is the confidence value
            conf = -1
            #prim is the primary transcription
            prim = ""
            trans = set() 
            for f in flat:
	            #May not need to go into every value without stability, i.e. if conf is the same
	            if "stability" not in f:
		            alternatives = f['alternative']
		            for alt in alternatives:
			            #This only tracks the last confidence level
			            if "confidence" in alt : 
				            conf = alt["confidence"] 
				            prim = alt["transcript"]
			            trans.add(alt["transcript"])
            #Fix: instead of returning prim, run all trans values through  
            self.output = prim
        except Exception as e:
		    if DEBUG: print "Exception e is {}. Output is {}".format(e, self.output)
		    self.output = ""

if __name__ == "__main__":
    filename=sys.argv[1] #"../sample_audio/orange2.flac" 
    stt = google_stt_stream(filename)
    stt.start()
    stt.stop()
    stt.format_output()
    print stt.output
