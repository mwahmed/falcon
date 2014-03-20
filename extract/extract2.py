import re
import nltk as n
import nltk.corpus as nc
import sys
import os

from bson.objectid import ObjectId
from pymongo import MongoClient

DEBUG = 0

#Look for modal auxiliary + baseform, i.e. will eat etc.
future = re.compile("^(MD|VB)$", re.I )       
present = re.compile("^(VBG|VBP|VBZ)$", re.I )
past = re.compile("^(VBD|VBG)$", re.I )
noun =  re.compile("^(NN|NNP|NNPS|NNS)$", re.I )
verb =  re.compile("^(VB|VBD|VBG|VBN|VBP|VBZ|)$", re.I )
pronoun = re.compile("^(PRP|WP|WP$)$", re.I)

numerical=re.compile("^(CD)$", re.I)

month = re.compile("(january|february|march|april|may|june|july|august|september|october|november|december)", re.I)
dayProper = re.compile("(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", re.I)
day = re.compile("(today|tomorrow|yesterday)", re.I)
time = re.compile("(now|then|O`clock)", re.I) 
question_re = re.compile("^(who|what|when|where|why|how)$", re.I)

class ptr:
    def __init__(self, obj): self.obj = obj
    def get(self):    return self.obj
    def set(self, obj):      self.obj = obj

"""
Matches term or regex, and return matching term index or -1
    if no match
@params
    tagged- list of tagged words, 2-tuple
    tag, "term" or regex obj being matched
    srcidx, whether to look in first or second
        element of 2-tuple, in most cases, you
        want to match the tag(1), but in some cases
        you may want to match the content
    exact- exact(True) or substring match(False)
@ret- (matching term index|-1)
"""
def findfirst(tagged, tag, srcidx=1, exact=True):
    if isinstance(tag, str):
        for idx in range(len(tagged)):
            if exact:
                if tag == tagged[idx][srcidx]:
                    return idx
            else:
                if tag in tagged[idx][srcidx]:
                    return idx
    else: #is regular expression
        for idx in range(len(tagged)):
            if tag.search(tagged[idx][srcidx]):
                return idx     
    return -1 #No match  

"""
Finds the phrase that refers to the semantic object in the sentence 
@ret-returns subset of param tagged
"""
def object_phrase(tagged):
    for i in range(1,len(tagged)):
        if verb.search(tagged[i][1]):
            return tagged[:i]
    return tagged

"""
set value of expression, i.e. exprval to idx[0]
"""
def set_and_cond(idx, exprval):
    idx.set(exprval)
    return exprval

"""
Returns list of list of tuples of words conforming to pattern
Matches patters of the form I <will> <complete> the <task> tomorrow.
@params-
    tagged- single list of tagged words
"""
def future_deliverable(tagged):
    dlvr = [] #list of all matches
    i = 0    
    while i < len(tagged):                 
        #Identify patterns of future deliverables
        match = []
        try:
            if tagged[i][1] == "MD":
                verbidx = findfirst(tagged[i+1:], "VB")
                if verbidx != -1:                    
                    verbidx += (i+1) #Normalize verb idx  
                    match.append(tagged[i])
                    match.append(tagged[verbidx])
                    
                    obj = object_phrase(tagged[verbidx+1:])
                    if obj:
                        match.append(obj)
                        if DEBUG: print "obj is {}".format(obj)
                                    
        except IndexError:
            print "IndexError"
        if match: dlvr.append(match)
        i+= 1    
    return dlvr

"""
Subject Verb (I am sitting) is typically a statment
Inversion (Am I ...) is typically question
"""
"""
Parses sentences based on increasingly selective rules
"""
def question(tagged):
    ret = [] 
    idx = ptr(0)  
    #Check if sentence has question mark
    #will work best for manually transcribed text 
    if set_and_cond(idx, findfirst(tagged, "?", srcidx=0, exact=False)) != -1:
        ret.append(tagged)
    
    #Search for question indicating words    
    elif set_and_cond(idx, findfirst(tagged, question_re, srcidx=0)) != -1:        
        i = idx.get()
        i = findfirst(tagged[i+1:i+2], verb)
        if i != -1:
            ret.append(tagged[i:])
    #Matches questions of the form <should we go ahead
    elif set_and_cond(idx, findfirst(tagged, "MD")) != -1:
        i = idx.get()
        if pronoun.search(tagged[i+1][1]) or noun.search(tagged[i+1][1]):
                ret.append(tagged[i:i+2])
    return ret
    
def current_deliverables(tagged):
    match_present = []
    tmp = []
    ret = None
    for i in range(len(tagged)):
        tmp = []
        ret = None
        try:  
            #Verb in present tense found
            ret = present.search(tagged[i][1])    
            if ret:
                tmp.append(tagged[i])
                tmp.append(tagged[i+1])
                tmp.append(tagged[i+2])
                #ret = findfirst(tagged[i+1:], noun)
                #if ret:
                #    tmp.append(ret)
        except Exception:
            pass
        if tmp and len(tmp) > 1: match_present.append(tmp)
    return match_present


def changeFormat(sent):
    if isinstance(sent, basestring):
        return sent.split(" ")
    elif isinstance(sent, list):
        if len(sent)>0:
            if isinstance(sent[0], basestring):
                return sent
    else:
        print "Unknown format"
    
"""
resp = (p|f|q) ; present, future, question
"""
def deliverables(sent, resp=None):
    
    sent = changeFormat(sent)
    tagged=n.pos_tag( sent ) #sent should be a list of words

    ret = None
    if resp == "f": 
        ret=future_deliverable(tagged)
    elif resp == "p":
        ret = current_deliverables(tagged)
    elif resp == "p":
        ret = question(tagged)
    else:
        pass
    
    return ret
    
    """
    match_future=future_deliverable(tagged)
    if match_future: return match_future
    match_question=question(tagged)
    if match_question: return match_question 
    match_present = current_deliverables(tagged)
    if match_present: return match_present
    
    return {"future":match_future, "question":match_question, "present":match_present}
    """
    

"""
Extracts for a list of sents
params-
    sents is a list of list of strings
    i.e. a list of sentences, where each
    sentence is a list of words
"""
def extract(sents, tasktype,  pr=False, ):
    ret = []
    for s in sents:
        try:
            r = deliverables(s)[tasktype]
            if r:
                ret.append(r)
                if pr:            
                    if isinstance(s, basestring):
                        print "Sentence is: {}".format("".join(s))
                    elif isinstance(s, list):
                        print "Sentence is: {}".format(" ".join(s))
                    print "Ret is: {}\n".format(r)
        except UnicodeEncodeError:
            pass
        except IndexError:
            pass

    return ret

def euro():
    europarl = nc.util.LazyCorpusLoader('europarl_raw/english', n.corpus.EuroparlCorpusReader, r'ep-.*\.en', encoding='utf-8')     
    fileid = europarl.fileids()[0]
    sents = europarl.sents(fileid)
    return sents
    
if __name__ == "__main__":
    if len(sys.argv) > 0:
        postid = sys.argv[1]
        tasktype = sys.argv[2] #"present", "future"
        
        client = MongoClient('localhost', 27017)
        db =  client.ahks_development
        transcriptions = db.transcriptions
        document = transcriptions.find_one({'_id': ObjectId(post_id)})
        transcriptionText = document['text']
        sents = transcriptionText.split("\n")
        
        ret = extract(sents, tasktype)
        for line in ret:
                print line
    else:
        sents = euro()
        for s in sents:
            #TODO: If s is a line and not a sentence
            #Use other features to delineate sentences
            #print "Sentence is: {}".format(s, " ".join(s))
            try:
                ret = deliverables(s)
                if ret:
                    print "Sentence is: {}".format(" ".join(s))
                    print "Ret is: {}\n".format(ret)
            except UnicodeEncodeError:
                pass
