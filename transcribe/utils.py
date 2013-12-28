#!/bin/python

#Contains utility functions
import subprocess
import re
"""
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
@ret= sampling frequency of file
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
@ret=return number N corresponding to time t
@params
  t - time in seconds
  samp_freq-sampling frequency in Hz
"""
def time_to_sample(t, samp_freq):
    return t*samp_freq

"""
Returns the base file name, 
    does not work properly for
    cases where extensions has '.' 
    in it, i.e. "tar.gz"
@ret=returns the basefile path
@params
    filepath - the filepath
"""
def base_filename(filepath):
    ret = filepath.split("/")[-1]
    ret = ret.split(".")[:-1]
    return ".".join(ret)
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
	fs- sampling frequency
"""
def play(audio, samp_freq=44100):
	try:
		sa.play( audio, fs=samp_freq)
	except Exception as e:
		print "Exception thrown : {}".format(e)
		
"""
Plays audio file from given bounds, i.e. start and end indices
"""
def play_seg(audio, bounds, samp_freq=44100):
	start = bounds[0]
	end = bounds[1]
	play(audio[:, start:end], samp_freq)


"""
returns index of value
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

