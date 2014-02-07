#Returns an accuracy of the generated summary
import re
import numpy as np

"""
Remove irrelevant words from line, e.g. articles
"""
def filter_garbage(line):
    #Garbage
    pattern = re.compile("^(the|a|an|it|he|she|him|her)$", re.I)
    retline = []
    words = line.split(" ")
    for word in words:
        if not pattern.search(word): retline.append(word)
    return " ".join(retline)        

"""
Returns similarity of two lines
@params
	line1- first line
	line2- second line
@ret- number between 0,1 indicating 
	fraction of similarity 
"""
#TODO: The following reasoning can be
#   extended to words, i.e. verbs in different
#   forms are considered identical    
def line_similarity(line1, line2):    
    #filter articles from lines
    f1 = filter_garbage(line1)
    f2 = filter_garbage(line2)

    nscore = len(f1) + len(f2)
    score = nscore
    for f in f1:
        if f not in f2: score-=1
    for f in f2:
        if f not in f1: score-=1

    return score/float(nscore)

"""
Checks whether the line or a line approprimately
    equivalent to line exists in the summary
@params
    line- line to be searched
    summary- list of lines, that constitute the summary
@ret- (True|False)
"""
def insummary(line, summary):

    for s in summary: 
        sim=line_similarity(line, s) 
        #if sim < 1:
        #    print line
        #    print s
        if sim>0.95:
            return True 
    return False

"""
Computes accuracy of machine generated summary
This assumes that both summaries are generated 
    from the same transcribed source
TODO: Relax following assumption
This also assumes that identical and complete 
    sentences are used    
@params
    machine- list of lines (str) in machine generated summary
    human- list of lines in human generated summary
@return- a number between 0 and 1, representing
    the similarity percentage 
"""
def similarity(machine, human_unparsed):
    machine.sort()
    human_unparsed.sort()
    human = []
    for line in human_unparsed:
        line = line.replace(",", "")
        line = line.replace("-", " ")
        human.append(line)
    
    #The non-normalized score
    nscore = len(human) + len(machine)
    score = nscore
    for m in machine:
        if m not in human:
            score -= 1
            
    for h in human:
        if h not in machine:
            score -= 1

    return (score/float(nscore))

"""
More permissive version of similarity
"""
#TODO: Maybe too permissive, should not exceed
#score of similarity if identical sentences used
#See test results
def similarity2(machine, human): 
    nscore = len(human) + len(machine)
    score = nscore
    for m in machine:
        if not insummary(m, human):
            score -= 1
            
    for h in human:
        if not insummary(h, machine):
            score -= 1

    return (score/float(nscore))

"""
Same problems as similarity 2
"""
def similarity3(machine, human):
    mbag = [word for sent in machine for word in sent.split()]
    hbag = [word for sent in human for word in sent.split()]
    
    mbag.sort()
    hbag.sort()
    
    words = list(set(mbag + hbag)) #list of unique words
    mvect = [0]* len(words)
    hvect = [0]* len(words)
    
    for idx in range(len(words)):
        w = words[idx]
        mvect[idx] = mbag.count(w)
        hvect[idx] = hbag.count(w)
    #Now do the eulidean distance of these 2 vectors

    hvect = np.array(hvect)
    hvect = hvect/np.sqrt(np.sum(hvect * hvect)) #Normalize
    mvect = np.array(mvect)
    mvect = mvect/np.sqrt(np.sum(mvect * mvect)) #Normalize

    dist = np.linalg.norm(hvect - mvect)
    return dist
