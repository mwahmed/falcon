from xml.dom import minidom
import sys
import os
import random 
import nltk as n
import nltk.corpus as nc


europarl = nc.util.LazyCorpusLoader('europarl_raw/english', n.corpus.EuroparlCorpusReader, r'ep-.*\.en', encoding='utf-8') 

"""
Prints each element of array on a separate line
"""
def linpr(array):
    for a in array:
        print a

"""
returns a list of text in segment nodes
@params
    filepath: of input file
@ret- returns list of texts 
"""
def ldcTextHelper(filepath):
    textlist = []
    xmldoc = minidom.parse(filepath)
    segments = xmldoc.getElementsByTagName('Segment') #list of segments
    for s in segments:
        
        text = s.firstChild.nodeValue.strip()
        participant = None
        if s.attributes.has_key("Participant"):
            participant = s.attributes["Participant"].value 
        if text:
            textlist.append(text)
            #print "{}: {}".format(participant, text)           
    return textlist

#Returns a list of sentences
def getLdcText(filepath):
    text = ldcTextHelper(filepath)
    return text

#Returns a list of all available files
def getLdcFiles():
    dirname = "../ldc_data/trans/icsi_mr_transcr/transcripts"
    #list of all files
    files = filter(lambda filename: filename[0]=="B", os.listdir(dirname))
    return map(lambda file:  dirname + "/" + file, files)

#Returns a list of sentences
def ldcFile(fidx=0):
    return getLdcText(getLdcFiles()[fidx])
    
#Returns list of sentences     
def getEuroParlText(fileidx=0):     
    fileid = europarl.fileids()[fileidx]
    sents = europarl.sents(fileid)
    return sents

#Returs a list of all available ids of europarl
def getEuroParlFileIDs():
    return europarl.fileids()
    
if __name__ == '__main__':
    text = ldcFile(20)
    #To use LDC text
    #choose index idx, such that: 0 <= idx < len(getLdcFiles)   
    #conv = ldcFile(idx)

    #To use europarl:
    #choose index idx, such that: 0 <= idx < len(getEuroParlFileIDs)
    #sents = getEuroParlText(idx)
    
    