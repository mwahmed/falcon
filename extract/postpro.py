import re

"""
Checks if argument string contains a month 
@params
    string-input string to be scanned for matches    
@ret- returns matching string or None, if no match
"""
def has_month(string):
    pattern = re.compile("(january|february|march|april|may|june|july|august|september|october|november|december)", re.I)
    match = pattern.search(string)
    if match: 
        return match.group(0)
    else:  
        return None


def has_day(string):
    pattern = re.compile("(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", re.I)
    match = pattern.search(string)
    if match: 
        return match.group(0)
    else:  
        return None
        
def has_number(string):
    pattern = re.compile("(1|2|3|4|5|6|7|8|9|10|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)", re.I)
    match = pattern.search(string)
    if match: 
        return match.group(0)
    else:  
        return None    


        
"""
Check if string has imperative verb-
   may indicate an action to be done
"""
def has_imperative(string):        
    ret = []
    for word in string:
        if isverb(word) and isimperative(word):
            ret.append(word)
    return list(set(ret))

"""
@params
    arg can be a string or a list of string
"""
def postpro(arg):
    if isinstance(arg, basestring):
        ret = has_month(arg)        
        if ret: 
            idx = arg.index(ret)
            #Now look around this index for 
            #   a matching task    
                        
        ret = has_day(arg)
        if ret:
            idx = arg.index(ret)
            # See above comment
