#Returns an accuracy of the generated summary

"""
Compares 2 sentences are returns true if they 
    are resonably alike
@params
    line1- first line 
    line2- second line
@ret- (True|False)
"""
def aresame(line1, line2):
    return line1 == line2

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
@return- a percent of similarity
"""
def similarity(machine, human):
    machine.sort()
    human.sort()
    
    score = 100.0
    #Each line corresponds to the total score by del
    del = score/len(human)
    for m in machine:
        if m not in human:
            #TODO: This is not semantically correct
            score -= del
            
    return score
