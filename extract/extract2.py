import re
import nltk as n
import nltk.corpus as nc
import sys
import os

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
question_re = re.compile("(who|what|when|where|why|how)", re.I)

def findfirst(tagged, tag, srcidx=1):
    if isinstance(tag, str):
        for idx in range(len(tagged)):
            if tagged[idx][srcidx] == tag:
                return idx    
    else: #is regular expression
        for idx in range(len(tagged)):
            if tag.search(tagged[idx][srcidx]):
                return idx     
    return -1 #No match  

def findall(tagged, tag):
    ret=[]
    if isinstance(tag, str):
        for idx in range(len(tagged)):
            if tagged[idx][1] == tag:
                ret.append(idx)    
    else: #is regular expression
        for idx in range(len(tagged)):
            if tag.search(tagged[idx][1]):
                ret.append(idx)     
    return ret   


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
                        print "obj is {}".format(obj)
                                    
        except IndexError:
            print "IndexError"
        if match: dlvr.append(match)
        i+= 1    
    return dlvr

"""
Subject Verb (I am sitting) is typically a statment
Inversion (Am I ...) is typically question
"""
#TODO: Finish
def question(tagged):
    #print tagged
    ret = [] #list of all questions in this line
    mdidx = findfirst(tagged, "MD")
    if mdidx != -1:
        i = mdidx
        if pronoun.search(tagged[i+1][1]) or noun.search(tagged[i+1][1]):
                ret.append(tagged[i:i+2])
    else:
        qidx = findfirst(tagged, question_re, srcidx=0)
        if qidx != -1:
            ret.append(tagged[qidx:])
    
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
        if tmp: match_present.append(tmp)
    return match_present


def changeFormat(sent):
    if isinstance(sent, str):
        return sent.split(" ")
    elif isinstance(sent, list):
        if len(sent)>0:
            if instance(sent[0], str):
                return sent
    else:
        print "Unknown format"

def deliverables(sent):
    
    sent = changeFormat(sent)
    tagged=n.pos_tag( sent ) #sent should be a list of words

    match_future=future_deliverable(tagged)
    #if match_future: return match_future
    match_question=questions(tagged)
    #if match_question: return match_question 
    match_present = current_deliverables(tagged)
    #if match_present: return match_present
    
    return {"future":match_future, "question":match_question, "present":match_present} 

def extract(sents):
    ret = []
    for s in sents:
        ret.append(deliverables(s))
    return ret
    
if __name__ == "__main__":
    
    europarl = nc.util.LazyCorpusLoader('europarl_raw/english', n.corpus.EuroparlCorpusReader, r'ep-.*\.en', encoding='utf-8')     
    fileid = europarl.fileids()[0]
    sents = europarl.sents(fileid)
    
    
    for s in sents[15:30]:
        #TODO: If s is a line and not a sentence
        #Use other features to delineate sentences
        
        ret = deliverables(s)
        if ret:
            print "Sentence is: {}".format(" ".join(s))
            print "Ret is: {}\n".format(ret)

