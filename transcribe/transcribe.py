#!/bin/python

#import webspeech_key as gt
import webspeech_key_multi as gt
import prepro as pp
import sys
import re
import os
import glob
import utils as ut
import argparse as ap
import time 
import requests
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
t_id = sys.argv[2]
client = MongoClient()
db = client.ahks_development
transcriptions = db.transcriptions
DEBUG = ut.get_debug()

"""
Parses command line args and returns 
    list of parameters
@params
    fpath-input filepath 
        Useful, if called via module import  
    idr- input directory
        directory containing input file
    dbg- debug flag
    spath- summary path
        either the summary file name or path to store summary in
    sgdr- segment dir
        dir that stores temporary audio file segments
@ret= List of paths to input file,
    output summary file, and segment directory
"""
def parse_args(fpath=None, trans_id=None, idr=None, dbg=None, spath=None, sgdr=None):    
    global DEBUG
    parser = ap.ArgumentParser()
    
    if not fpath:
        parser.add_argument("filepath", help="path to input audio file")
    if not trans_id:
        parser.add_argument("trans_id", help="id in the database")
    if not idr:
        parser.add_argument("-i", "--indir", help="directory containing input audio file, if filepath does not contain path")
    if not dbg:
        parser.add_argument("-d", "--debug", help="enble debugging output", type=bool)
    if not spath:
        parser.add_argument("-s", "--sumpath", help="path to summary file. Can either be file or dir. If dir, summary file stored in dir/basefilename.txt")
    if not sgdr:    
        parser.add_argument("-f", "--segdir", help="directory to store temporary audio seg/frag-ment files")
    args = parser.parse_args()
    
    cfg_params = ut.get_cfg_params()
    
    filepath=""
    sumpath=""
    segdir=""

    directory=""

    #Get the input file path
    if fpath and os.path.isfile(fpath):    
        filepath = fpath
    else:    
        drct, fl = ut.split_path(fpath if fpath else args.filepath)
        if not fl:
            print "Invalid input file: '{}'".format(drct+"/"+fl)
            raise Exception
        if not drct:
            directory = idr or args.indir or cfg_params["in_dir"]
            if not os.path.isdir(directory):
                print "Invalid input directory '{}'".format(directory)
                raise Exception
            filepath = ut.dir_path(directory) + fl
        else:
            filepath = ut.dir_path(drct) + fl
            
        if not os.path.exists(filepath):
            print "Input file not found. Filepath is {}".format(filepath)
            raise Exception    
    
    #Get summary file path
    sumpath = spath or args.sumpath  
    if sumpath:
        drct, fl = ut.split_path(sumpath)
        directory = drct
        if drct and fl:
            pass
        elif drct:
            sumpath = ut.dir_path(drct) + ut.base_filename(filepath)
        elif fl: 
            directory=ut.dir_path(cfg_params["summary_dir"])
            sumpath = directory + fl
        else:
            #TODO: Check if this is necessary
            print "Invalid summary path {}".format(sumpath)
            raise Exception
    else:
       directory = ut.dir_path(cfg_params["summary_dir"])
       sumpath = directory + ut.base_filename(filepath)
    #Append extension
    if sumpath[-5:] != ".smry" : sumpath += ".smry"
    #If dir does not exist, create it
    if not os.path.exists(directory):
        if DEBUG: print "Creating dir {}".format(directory)
        os.makedirs(directory)
            
    #Get segment directory path           
    segdir = sgdr or args.segdir or cfg_params["seg_file_dir"]
    if not os.path.exists(segdir):
        if DEBUG: print "Creating dir {}".format(segdir)
        os.makedirs(segdir)
  
    #Set Debug flag
    if args.debug:
        DEBUG = args.debug 
    
    return (filepath, sumpath, segdir)

"""
Transcribes the audio at filepatha
@params
    filepath - the path to the audio file
        to be transcribed
    sumpath - path to file to write summary in
    segdir - directory to store temporary segment files
@ret = list of transcribed lines
"""    
def transcribe(filepath, sumpath, segdir):
    if DEBUG: print "filepath= {}, sumpath= {}, segdir= {}".format(filepath, sumpath, segdir)
    if DEBUG: print "File length = {}".format(ut.file_length(filepath))     
    
    #Writes all segment files to segdir
    #print time.time() - start_time, "seconds; starting prepro"
    seg_count = pp.prepro2(filepath, segdir)           
    #print time.time() - start_time, "seconds; ending prepro"
    
    basefile = ut.base_filename(filepath)       
    if DEBUG: print "basefile is {}".format(basefile)
    
    sf = open(sumpath, "w")
    #Consider using #while os.path.exists(opath): 
    segfiles = (ut.dir_path(segdir) + basefile + "__" + str(i) + ".flac" for i in range(seg_count))    
    #print time.time() - start_time, "seconds; starting transcribe"
    trans_list = gt.google_transcribe(segfiles)
    #print time.time() - start_time, "seconds; ending transcribe"
    if DEBUG: print trans_list
    db_data = ""
    for t in trans_list:
        sf.write(t + "\n")
	db_data += str(t) + "\n"
    """
    for seg in segfiles:     
        if DEBUG: print "segment path is {}".format(seg)
        trans = gs.key_trans(seg)
        sf.write(trans + "\n")
        if DEBUG: print(trans)
        trans_list.append(trans)         
    """
    sf.close()
    ut.remove_seg_files(segdir, basefile + "__*.flac")
    #Trans_list is a list of lines that are transcribed
    return db_data
"""
calls transcribe function
@params
    filepath- path to input file; 
        can be path or just filename
    indir- if filepath specifies just name
        use this to specify dir
    sumpath- filepath or directory of summary file
    segdir- dir holding temporary segment files
    debug- debug flag
@ret- list of transcribed lines
"""

start_time = time.time()

def call_transcribe(filepath=None, sumpath=None, segdir=None, indir=None, debug=None):
    print time.time() - start_time, "seconds; started parse_args"
    filepath, sumpath, segdir = parse_args(fpath=filepath, idr=indir, spath=sumpath, sgdr=segdir, dbg=debug)
    
    print time.time() - start_time, "seconds; ended parse_args"
    trans_list = transcribe(filepath, sumpath, segdir)
    payload = {'id': t_id, 'text':trans_list}
    r = requests.post("https://localhost:3000/update_transcription", data=payload,verify=False)
    return trans_list

if __name__ == "__main__":      
    call_transcribe()
    
