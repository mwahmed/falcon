import google_speech as gs
import prepro as pp
import sys
import re
import os
import glob
import utils as ut

DEBUG = 1

#TODO: Store the following info in a conf file
#TODO: move some stuff to a utils module
#Default dir to look for audio files
DEFAULT_DIR = "../sample_audio"
#default dir for audio segment files
OUTPATH = "./seg_audio"

SUMMARY_DIR = "../summary"

#Returns filepath if valid argument passed
#else raises an Exception
def parse_args(sys):
	#should be called with one argument, the audio file 
	if len(sys.argv) != 2:
		print "Invalid number of arguments. Call with filepath only"
		raise Exception
	
	filepath = sys.argv[1]
	#Check file extension is .flac
	if len(filepath) < 4 or filepath[-4:] != "flac":
		print "Invalid filename..."
		raise Exception
	
	#Accepts unqualified filename
	# in this case look in default dir 
	if "/" not in filepath:	
		fpath = DEFAULT_DIR + "/" + filepath
		if not os.path.exists(fpath):
			"{} does not exist in default dir; specify full path".format(filepath)
			raise Exception
		filepath = fpath	
	#check whether path points to a valid file	
	else:	
		if not os.path.exists(fpath):
			"{} does not exist".format(filepath)
			raise Exception

	return filepath

def parse_args2(argv):
	#should be called with one argument, the audio file 
	if len(sys.argv) != 2:
		print "Invalid number of arguments. Call with filepath only"
		raise Exception
	
	filepath = sys.argv[1]
	#Check file extension is .flac
	if len(filepath) < 4 or filepath[-4:] != "flac":
		print "Invalid filename..."
		raise Exception
	
	#Accepts unqualified filename
	# in this case look in default dir 
	if "/" not in filepath:	
		fpath = DEFAULT_DIR + "/" + filepath
		if not os.path.exists(fpath):
			"{} does not exist in default dir; specify full path".format(filepath)
			raise Exception
		filepath = fpath	
	#check whether path points to a valid file	
	else:	
		if not os.path.exists(fpath):
			"{} does not exist".format(filepath)
			raise Exception

	return filepath





def remove_seg_files(basefile):
		#remove all matching files
		cwd = os.getcwd()
		os.chdir(OUTPATH)
		filelist = glob.glob(basefile + "__*.flac")
		for f in filelist:
			os.remove(f)
		os.chdir(cwd)

def transcribe(filepath):
		if DEBUG: print "Pre-processing {}".format(filepath)
		if DEBUG: print "File length = {}".format(ut.file_length(filepath))		
		
		seg_count = pp.prepro2(filepath, OUTPATH)			
	 	
		basefile = ut.base_filename(filepath)		
		if DEBUG: print "basefile is {}".format(basefile)
		summaryfile = SUMMARY_DIR + "/" + basefile + ".txt"
		sf = open(summaryfile, "w")
		#The path to the segment file
		opath = OUTPATH+"/"+ basefile + "__" + str(i) + ".flac" 
		i=0
		while i < seg_count: 
		#while os.path.exists(opath):
			if DEBUG: print "opath is {}".format(opath)
			trans = gs.key_trans(opath)
			sf.write(trans)
			if DEBUG: print(trans)
			#print gs.keyless_trans(opath)			
			i+=1
			opath = OUTPATH+"/"+ basefile + "__" + str(i) + ".flac"        	 
			if DEBUG: print "opath is {}, i is {}".format(opath, i)
		
		sf.close()
		remove_seg_files(basefile)

if __name__ == "__main__":	
		
		filepath=parse_args(sys)
		
		DEFAULT_DIR = "../sample_audio"
		OUTPATH = "./seg_audio"
		SUMMARY_DIR = "../summary"
		
		transcribe(filepath)
