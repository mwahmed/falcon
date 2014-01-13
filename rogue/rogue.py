#Returns an accuracy of the generated summary
import functools as ft
import re

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

    #Creates a partially applied function
    #   that only requires second arg to line_similarity
    line_cmp = ft.partial(line_similarity, line)
    #We consider it in summary if greater than 90% similarity 
    return 0.9 < max(map(line_cmp, summary)) 

"""
Computes accuracy of machine generated summary
This assumes that both summaries are generated 
    from the same transcribed source
TODO: Relax following assumption
This also assumes that identical and complete 
    sentences are used    
@params
    machine- list of lines in machine generated summary
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
Functional implementation of similarity2
"""
def similarity2f(machine, human):
    nscore = len(human) + len(machine)
    #Argument reversed version of insummary
    #So we can create partial applied function
    arg_rev_insum = lambda summary, line: insummary(line, summary)
    #A partial function that accepts line from
    # human summary; return true if line in summary
    h_summ = ft.partial(arg_rev_insum, human) 
    m_summ = ft.partial(arg_rev_insum, machine) 
    #Predicate that negates input
    not_pred = lambda arg: not arg
    s1=len(filter(not_pred, map(m_summ, machine))) 
    s2=len(filter(not_pred, map(h_summ, human)))
    return (nscore - s1-s2)/float(nscore)
