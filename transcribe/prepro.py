#! /usr/bin/env python
import numpy as np
import scikits.audiolab as sa 
import subprocess
import math
import matplotlib.pyplot as plt
import shutil 
import os
import utils as ut

DEBUG = 1

"""
returns smallest index of value closest to threshold
@params
	T - the threshold value
	S - the sorted indices, corresponding to the unsorted indices in audio_row1
	audio_row1 - the intensity array   
"""
def find_thresh_ind(T, S, audio_row1):    
    #Find index in array of sorted indices
    # i.e. indices corresponding to sorted values >= T
    ti = -1
    i=0
    while i < S.size: 
        if audio_row1[S[i]]>= T: 
            ti = S[i]
            break
        i+=1
    return i

"""
returns list of word boundaries
@params-
	srt_arr - array of sorted indices (typically a subset)
	disc - discontinuity 
	
"""
def get_words(srt_arr, disc=5):
	#Contains indices that define boundaries
	words=[srt_arr[0]] if len(srt_arr) else []  
	i=1
	while i<srt_arr.size:
 		if srt_arr[i] > srt_arr[i-1] + disc:    
 			words.append(srt_arr[i])
		i+=1
	#+1 because second ind is excluded
	words.append(srt_arr[-1] + 1) 
	return words 
	
"""
returns tuples of word boundaries
	first ind is starting index of word, ind from complete audio array 
@params
	words-  return of above function
"""
def get_word_bounds(words):
	word_bounds=[]
	i=0
	start = -1
	end = -1
	while i < len(words)-1:
	  word_bounds.append( (words[i], words[i+1]-1) )
	  i+=1 	  
	return word_bounds

"""
returns time corresponding to idx,
    i.e. idx = 0 -> time = 0
@params
	idx- index
	samp_freq- sample frequency
"""
def totime(idx, samp_freq=44100):
	return float(idx)/samp_freq	
	
"""
returns time represented by start and end indices
"""
def timediff(start, end, samp_freq=44100):
	return totime(end) - totime(start)
	
"""
removes any files in dir and dir at path
then recreates dir	
"""
def setup_dir(path):
	if os.path.isdir(path):
		shutil.rmtree(path)
	os.mkdir(path)

"""
writes segments to path
"""	
def write_segs(audio, word_bounds, snd_obj, path, base_filename="or_br"):	
	
	max_dim = max(audio.shape)
	axis = audio.shape.index(max_dim)
	#axis should be the one with the most values
	i=0
	while i<len(word_bounds):
		filename = base_filename + "__" + str(i) + '.flac'
		filepath = path + '/' + filename
		a1= word_bounds[i][0]
		a2= word_bounds[i][1]
		snd_w = sa.Sndfile(filepath, 'w', snd_obj.format, snd_obj.channels, snd_obj.samplerate)
		snd_w.write_frames(audio.take(range(a1,a2), axis=axis).transpose() )
		i+=1
	
"""
Performs all the preprocessing, and places segments in outpath
@params
	filepath- path to input flac file 
	outpath- directory to store segments
"""	
#TODO: add more default paramters to prepro, e.g. twt
def prepro(filepath, outpath):	
	#sndfile 
	sndf = sa.Sndfile(filepath, 'r')	
	#fs= sampling frequency(in Hz)
	fs = sndf.samplerate
	#total frames = file length * sample rate 
	total_frames = math.floor(fs * ut.file_length(filepath)) #235008 for orange2.flac
	
	#Audio file as np array
	audio=sndf.read_frames(total_frames).transpose()
	
	#First row of audio array
	audio_r1 = audio[0, :] 
	
	#TODO: Experiment with different t, twt, to get more accurate system
	#threshold weight
	twt = 3
	#Threshold
	t = twt*audio_r1.std() 
	
	#Array of sorted indices
	srt_ind = audio_r1.argsort()
	
	#Threshold index
	ti = find_thresh_ind(t, srt_ind, audio_r1)
	
	#Get all indices, for values >= t
	#indices for greater than srt
	srt_grt = srt_ind[ti:]
	#sort indices for easier clustering
	srt_grt.sort()
	
	#TODO: Experiment with values of disc
	words = get_words(srt_grt, disc=400)
	bounds=get_word_bounds(words)
	
	setup_dir(outpath)
	write_segs(audio, bounds, sndf, outpath)
	

"""
Segments audio file using a much simple algorithm than
  prepro, and places output segments in outpath 
@params
	filepath- path to input flac file 
	outpath- directory to store segments
	seg_size- length of segment in seconds
@return - returns the number of segments	
"""	
#TODO: add more default paramters to prepro, e.g. twt
def prepro2(filepath, outpath, seg_size=10):	
	#sndfile 
	sndf = sa.Sndfile(filepath, 'r')	
	#fs= sampling frequency(in Hz)
	fs = sndf.samplerate
	#File length in seconds 
	file_len = ut.file_length(filepath)
	
	#Total frames
	total_frames = int(math.floor(fs * ut.file_length(filepath)))
	
	#Audio file as np array
	audio=sndf.read_frames(total_frames).transpose()
	
	#Start and end time
	t_start=0
	t_end = seg_size
	#Starting and ending sample number
	samp_start = -1
	samp_end = -1
	#List of tuples of bounds
	seg_bounds = []
	while t_start < file_len:
		samp_start = t_start * fs
		samp_end = min(t_end * fs, total_frames)
		seg_bounds.append((samp_start, samp_end))		
		t_start += seg_size
		t_end += seg_size

	basename = ut.base_filename(filepath)
	if DEBUG: print "basename is {}".format(basename)
	if DEBUG: print "There are {} segments".format(len(seg_bounds))
	
	setup_dir(outpath)
	write_segs(audio, seg_bounds, sndf, outpath, base_filename=basename)
	return len(seg_bounds)

if __name__ == "__main__":
	#filepath
	filepath = './samples_audio/chan1.flac'
	#sndfile 
	sndf = sa.Sndfile(filepath, 'r')
	#fs= sampling frequency(in Hz)
	fs = sndf.samplerate
	#total frames = file length * sample rate 
	total_frames = math.floor(fs * file_length(filepath)) #235008 for orange2.flac
	
	#Audio file as np array
	audio=sndf.read_frames(total_frames).transpose()
	
	#First row of audio array
	audio_r1 = audio[0, :] 
	
	#TODO: Experiment with different t, twt, to get more accurate system
	#threshold weight
	twt = 3
	#Threshold
	t = twt*audio_r1.std() 
	
	#Array of sorted indices
	srt_ind = audio_r1.argsort()
	
	#Threshold index
	ti = find_thresh_ind(t, srt_ind, audio_r1)
	
	#Get all indices, for values >= t
	#indices for greater than srt
	srt_grt = srt_ind[ti:]
	#sort indices for easier clustering
	srt_grt.sort()
	
	#TODO: Experiment with values of disc
	words = get_words(srt_grt, disc=400)
	bounds=get_word_bounds(words)
	
	path='./sample_output'
	setup_dir(path)
	write_segs(audio, bounds, sndf, path)
	
	
