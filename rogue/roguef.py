#Functional implementation of rouge module
import functools as ft

"""
Functional implementation of insummary
"""
def insummary(line, summary):

    #Creates a partially applied function
    #   that only requires second arg to line_similarity
    line_cmp = ft.partial(line_similarity, line)
    #We consider it in summary if greater than 90% similarity 
    return 0.9 < max(map(line_cmp, summary)) 

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



