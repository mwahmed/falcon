import sys
import requests
import random
import urllib2
from threading import Thread
from time import sleep
import json
import utils as ut

DEBUG = ut.get_debug()

#Adapted from https://gist.github.com/offlinehacker/5780124

class google_stt(object):
    #def __init__(self, key="AIzaSyCOteUtC16xSVT7AJEsXmmR_l8nvn4RF80"): #Ayush's key
    def __init__(self, key="AIzaSyDjc6ZctgLju0LyWXQCH9yiEPHg2ehk_RY"): #Spandan's key                  
        self.api_key = key 

        base_url= "https://www.google.com/speech-api/full-duplex/v1/" 
        #Upstream URL - @Mike Pultz
        self.up_url1_param = "{}up?lang=%(lang)s&lm=dictation&client=chromium&pair=%(pair)s&key=%(key)s".format(base_url)
        #Upstream URL - @Offline Hacker
        self.up_url2_param = "{}up?key=%(key)s&pair=%(pair)s&lang=%(lang)s&maxAlternatives=%(max)s&client=chromium&continuous".format(base_url)
        #Downstream URL
        self.dn_url_param = "{}down?pair=%(pair)s".format(base_url)
    
    """
    Generate random sequence to be used as request key
    @ret- key     
    """
    def generate_request_key(self):
        return hex(random.getrandbits(64))[2:-1]

    """
    Sets Google API key
    @params
        newkey- new API key
    @ret- old API key 
    """
    def set_key(self, newkey):
    	oldkey = self.api_key
    	self.api_key = newkey
    	return oldkey

    """
    Starts speech processing, including thread initialization
    @params- 
        filename: file path
        run (1|2)- mode to run in, i.e. upstream URL to use
            mode 1- runs in dictation mode
                returns contiguous transcriptions of 
                entire submitted file
            mode 2- runs in chunked mode
                returns alternatives for each chunks,
                where each chunk is roughly one uninterrupted
                speech block  
    """
    #run should be 1 or 2, indicating which upstream url should be used
    #In general, run 2 should be better
    def start(self, filename, run=2):
        self.audiofile = filename 
        pair = self.generate_request_key()
        rate = ut.file_sampfreq(filename)
        self.output=[]
                
        up_headers = {'content-type': 'audio/x-flac; rate={}'.format(rate)}
        up_params = {"pair": pair, "key": self.api_key, "lang" : "en-US", "max": "5"}
        up_url = (self.up_url1_param if run==1 else self.up_url2_param) % up_params       
        dn_url = self.dn_url_param % {"pair": pair, "key": self.api_key}
 
        self.session = requests.Session()
        self.upstream_thread = Thread(target=self.upstream, args=(up_url, up_headers))
        self.downstream_thread = Thread(target=self.downstream, args=(dn_url,))

        self.upstream_thread.start()
        self.downstream_thread.start()
 
    """
    Joins upstream and downstream threads
    """
    def stop(self):
        #TODO: Check if the following is even needed
        sleep(30) 
        #self.keep_streaming=False
        self.upstream_thread.join()
        self.downstream_thread.join()
 
    """
    Posts audio file to url, with given headers
    @params 
        url- url to post to
        headers- HTTP headers of POST
    """
    def upstream(self, url, headers):
        self.session.post(url, headers=headers, files={self.audiofile: open(self.audiofile, 'rb')})
 
    """
    Merges all non-empty elem into list
    @param
        arr- the list to append to
        elem- the list or scalar element to 
            be added to the list
        flat (True|False)- if elem is a list,
            indicates whether elem appended to
            arr as a list or element by element 
    """
    def merge(self, arr, elem, flat=True):        
        if flat and isinstance(elem, list):
            for e in elem:
                if e : arr.append(e)
        else:
            if elem: arr.append(elem)
    """
    Returns a list of transcriptions after 
        parsing JSON
    @params
        arg- the json
    """
    def parse_json(self, arg):
       ret = []
       if isinstance(arg, list):
           for a in arg:          
               self.merge(ret, self.parse_json(a))             
       elif isinstance(arg, dict):
          if "alternative" in arg: 
              self.merge(ret, self.parse_json(arg["alternative"]) )
          elif "transcript" in arg:          
              if "confidence" in arg: 
                  self.merge(ret, (arg["transcript"], arg["confidence"]) )
              else:    
                  self.merge(ret, arg["transcript"])               
       return ret 

    """
    GETs the reply to POST of audio file
        and appends to self.output
    @parms
        url- the downstream URL 
    """
    def downstream(self, url):
        r = self.session.get(url, stream=True)        
        if r.status_code != 200:
            return 
        try:
            for line in r.iter_lines():
                if line:                                               
                    self.merge(self.output, self.parse_json(json.loads(line)["result"]), flat=False) 
        except TypeError as e:
            self.upstream_thread.join()
            return

#TODO: Perhaps, merge the following into google_stt class
#TODO: Come up with better methods
"""
Picks best transcription
@params
    trans- list of lists of strings
"""
def pick_best(trans):
    ret = []
    for t in trans: 
        elem = t[0]
        if isinstance(elem, tuple):
            elem=elem[0]
        ret.append(elem)
    return ret

#TODO:Pass all segments of one file in one shot                    
#   to get best CPU utilization by saving object creation overhead
"""
@params-list of files  
"""                    
def google_transcribe(files):
    #af_list = ["orange2.flac", "chan3_0_30.flac", "wasi1_conv.flac"]
    #filename="../sample_audio/" + af_list[1]  
    
    stt = google_stt()
    trans_list = []
    for filename in files:    
        if DEBUG: print "Processing {}".format(filename)
        stt.start(filename)
        stt.stop()
        if DEBUG: print "stt.output is: \n{}".format(stt.output)
        #TODO: try stt.start(filename, run=1) if stt.output not adequate
        ret = pick_best(stt.output)
        if DEBUG: print "ret is: \n{}".format(ret) 
        stt.merge(trans_list, ret)
    
    return trans_list  
          

if __name__ == "__main__":
    google_transcribe("")
    """
    Now need to pick between a and b
    Some things to try
        1) Google search
        2) Grammatical Analysis (NLPTK- Named Entity Recognition)
        3) Pick first one
        
        Also, the two return different number of chunks
            Guess number of words, based on:
                1) length of audio file
                2) number of peaks in waveform
        
    """
