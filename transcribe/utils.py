#!/bin/python

#Contains utility functions
import subprocess
import re
import ConfigParser as confpar
import os
import glob
import inspect

"""
[CONFIGURATION FILE]
"""
def get_cfg_path():
    filename="transcribe.conf"
    path = "./{}".format(filename)
    if not os.path.exists(path):
        dirpath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) 
        path="{}/{}".format(dirpath, filename) 
    return path    

"""
GLOBALS
"""
CFG_FILE_LOC=get_cfg_path()
CFG_FILE_SEC="main"

"""
Returns whether debug flag is set
@ret=Boolean value of debug flag 
    from conf file
"""
def get_debug():
    cp = confpar.ConfigParser() 
    cp.read(CFG_FILE_LOC)
    return cp.getboolean(CFG_FILE_SEC, "debug")

"""
Returns dictionary of conf params in conf file
@ret=dictionary of param name to value from conf file
"""
def get_cfg_params():
    cp = confpar.ConfigParser() 
    cp.read(CFG_FILE_LOC)
    opts = cp.options(CFG_FILE_SEC)
    return { p: cp.get(CFG_FILE_SEC, p) for p in opts}

"""
[GENERAL FILE MANAGEMENT/INFO]
"""
"""
Returns the base file name, 
    does not work properly for
    cases where extensions has '.' 
    in it, i.e. "tar.gz"
@ret= basefile path
@params
    filepath - the filepath
"""
def base_filename(filepath):
    ret = filepath.split("/")[-1]
    ret = ret.split(".")[:-1]
    return ".".join(ret)

"""
Returns filepath and filename
@ret= returns tuple of path and filename
Note: filepath may not exist
"""
def split_path(path):
    #path is the filename
    if "/" not in path: return(None, path)
    #path is path to directory
    if os.path.isdir(path): 
        if path[-1] == "/": path=path[:-1]
        return(path, None)        
    return os.path.split(path)
    
"""
Removes all matching files from given dir
"""
def remove_seg_files(drct, pattern):
    cwd = os.getcwd()
    os.chdir(drct)
    filelist = glob.glob(pattern)
    for f in filelist:
        os.remove(f)
    os.chdir(cwd)

"""
@ret= returns directory path with '/' appended
"""
def dir_path(path):
    if path[-1] != "/": path+="/"
    return path   

"""
[AUDIO FILE]
"""    
"""
Returns the file length in seconds
@ret= length of file in seconds
@params
    filepath- path to file
"""
def file_length(filepath):
    p=subprocess.Popen(["sox", filepath, "-n", "stat"], stderr=subprocess.PIPE)
    out, err= p.communicate()
    stats=err.split("\n")
    length = [ s for s in stats if "seconds" in s ][0].split(" ")[-1]
    return float(length)

"""
Returns sampling frequency of file
@ret= sampling frequency of file in Hz
@params
    filepath- path to file
"""
def file_sampfreq(filepath):
    p=subprocess.Popen(["sox", "--i", filepath], stdout=subprocess.PIPE)
    out, err= p.communicate()
    stats=out.split("\n")
    samp_freq = [ s for s in stats if "Sample Rate" in s ][0].split(" ")[-1]
    return int(samp_freq)
     
"""
Plots audio file
@params
    audio- nparray      
"""         
def plot(audio):
    plt.plot(audio.transpose())
    plt.show()

"""
Plays given file
@params
    audio- np array representing file
    samp_freq- sampling frequency
"""
def play(audio):
    try:
        sa.play( audio, fs=file_sampfreq(audio))
    except Exception as e:
        print "Exception thrown : {}".format(e)
        
"""
Plays audio file from given bounds
@params
    audio- np array representing audio file
    bounds- tuple representing start and end indices
        in audio array
    samp_freq- sampling frequency 
"""
def play_seg(audio, bounds):
    start = bounds[0]
    end = bounds[1]
    #FIX: This will only work if audio has 2 channels
    play(audio[:, start:end])

"""
[MISC]
"""
"""
returns index of value, or index of 
    closest value if no exact match
@params
    value is the value being searched
    srt_indx is the list of sorted indices
    vect is the unsorted list
    srt_fnc is the comparison function
        == 'gt' : returns index of value greater than 'value' if value DNE
        == 'ln' : returns index of value less than 'value' if value DNE
        == None : returns only index of value
"""
def binsrc(value, srt_indx, vect, src_fnc=None):

    low = 0
    high = len(vect) - 1
    
    if value < vect[srt_indx[low]]: 
        if src_fnc == 'gt': ret = -1
        elif src_fnc == 'lt': ret =  0
        else: ret = -1
        return ret
    if value > vect[srt_indx[high]]: 
        if src_fnc == 'gt': ret = high
        elif src_fnc == 'lt': ret = -1
        else: ret = -1
        return ret
    while low <= high:
        mid = (low + high) / 2

        if vect[srt_indx[mid]] > value:
            if src_fnc == 'gt':
                if vect[srt_indx[mid-1]] < value:
                    return mid
            high = mid - 1
        elif vect[srt_indx[mid]] > value:
            if src_fnc == 'lt':
                if vect[srt_indx[mid+1]] > value:
                    return mid             
            low = mid + 1
        else: #if vect[srt_indx[mid]] == value: 
            return mid
    return -1

