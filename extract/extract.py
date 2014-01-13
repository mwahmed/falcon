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

numerical=re.compile("^(CD)$", re.I)

month = re.compile("(january|february|march|april|may|june|july|august|september|october|november|december)", re.I)
dayProper = re.compile("(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", re.I)
day = re.compile("(today|tomorrow|yesterday)", re.I)
time = re.compile("(now|then|O`clock)", re.I) 

def findfirst(array, tag):
    if isinstance(tag, str):        
        ret = filter(lambda x: tag==x[1], array)
        if ret:
            return ret[0]
        else:
            return None
    else: #tag is a regex
        for i in range(len(array)):
            ret = tag.search(array[i][1])
            if ret:
                return array[i]
        return None


def has_time(tagged):
    match = []
    ret = None
    for t in tagged:
        word = t[0]
        ret = month.search(word)
        if ret: match.append(ret.group(0))
        ret = dayProper.search(word)
        if ret: match.append(ret.group(0))
        ret = day.search(word)
        if ret: match.append(ret.group(0))
        ret = time.search(word)
        if ret: match.append(ret.group(0))
    return match    

"""
Returns list of list of tuples of words conforming to pattern
Matches patters of the form I <will> <complete> the <task> tomorrow.
@params-
    tagged- single list of tagged words
"""
def future_deliverable(tagged):
    match_future=[]
    tmp = []
    ret = None
    
    for i in range(len(tagged)):        
        tmp = []
        ret = None
        try:             
            #Identify patterns of future deliverables
            if tagged[i][1] == "MD":
                tmp.append(tagged[i])    
                ret = findfirst(tagged[i+1:], "VB")
                if ret:
                    tmp.append(ret)    
                    #Identify relevant noun
                    ret = findfirst(tagged[i+2:], noun)
                    if ret:
                        tmp.append(ret)
                    
        except Exception as e:
            pass
        if tmp: match_future.append(tmp)
        
    return match_future

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

"""
sent can be a single sentence as a string
    or a list of tagged words
"""
def deliverables(sent):
        
    tagged = sent
    if isinstance(sent, str):
        tagged = n.pos_tag(n.word_tokenize(sent))            
    elif isinstance(sent, list):
        if isinstance(sent[0], basestring):
            tagged=n.pos_tag( sent )

    match_future=future_deliverable(tagged)
    match_time = has_time(tagged) 
    match_present=current_deliverables(tagged)
    match_past=[]
    match_noun=[]
    
    #Next identify dates, and task
    #Then things in the past
    
    if match_present: return match_present        
    
            
if __name__ == "__main__":
    
    """
    filename = "./samp.txt"
    if len(sys.argv) > 1: filename = sys.argv[1]
    if not os.path.exists(filename): sys.exit(1)
    f = open(filename, "r")
    lines=f.readlines()
    for line in lines:
        ret = deliverables(line)
        if ret: print "Analyzing line: {}Ret is {}".format(line, ret)
    """
    europarl = nc.util.LazyCorpusLoader('europarl_raw/english', n.corpus.EuroparlCorpusReader, r'ep-.*\.en', encoding='utf-8')     
    fileid = europarl.fileids()[0]
    sents = europarl.sents(fileid)
    try:
        for s in sents[:10]:
            ret = deliverables(s)
            if ret:
                print "Sentence is: {}\n Ret is: {}\n\n".format(" ".join(s), ret)
    except Exception:
        pass