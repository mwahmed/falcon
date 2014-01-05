#!/usr/bin/python
import sys
import os
import subprocess as sp
from collections import defaultdict
import time
import pdb

'''

df = number of times a term occurs in all documents

Purpose:
Calculate df and re-use it so that we don't have to do a 'grep' each time we need to find the number of occurences of a word. 

Maintain a df file containing df scores for each word. When this script is run:

- Load the values from that file into a dictionary, df, whose keys are words and the values are the number of occurences in
   the set of transcriptions

- Check a meta-file for the last succesful run time-stamp. Get a list of data files created after this point in time, and calculate 
  dfs only against these new data files

- For each transcription file 
	- Get the 'set' of words for that transcription i.e. no repetition
		- For each word in this set, if the word exists in the above dictionary, df, then add 1 to the value for the coressponding key
		- If it does not exist, then create a new key

	- After going over all the files in this manner,  store the current timestamp in the meta file.
		

TODO-1:
- If we decide to use pre-existing transcriptions for the purpose of providing the data to calculate tf.idf on, then this module has to
   be modified to calculate df values from those transcriptions, which are stored in the DB
 		- Once we move to a DB store a timestamp value for each tuple in the DB so that we can check the timestamp and get a list of 
		  transcripts generated after this point in time 

'''


ignore_chars = [""]
# Stores the new files for which df has to be calculated
new_files_list = list()

# This function reads the values from the df file into a dictionary
def read_df_vals_into_dict(saved_df_file_path):
	
	if not saved_df_file_path or not os.path.exists(saved_df_file_path):
		print "Path to file:" + saved_df_file_path + " does not exist."
		exit(1)

	df = defaultdict(int)
	df_read = open(saved_df_file_path, "r")
	df_file = df_read.readlines()
	df_read.close()

	# Read all the stored df values
	for df_file_line in df_file:
		df_file_line = df_file_line.strip()
		arrowIdx = df_file_line.find(">>")
		key = df_file_line[: arrowIdx]
		val = int(df_file_line[arrowIdx + 2 : ])
		if key not in ignore_chars:
			df[key] = val

	return df


'''
- For each transcription file 
	- Get the 'set' of words for that transcription i.e. no repetition
		- For each word in this set, if the word exists in the above dictionary, df, then add 1 to the value for the coressponding key
		- If it does not exist, then create a new key

	- After going over all the files in this manner,  store the current timestamp in the meta file.
	- Change the file permission to read only to avoid accidental deletes etc

- store the updated values in the df file
'''

def write_df_vals_to_file(saved_df_file_path, df):
	
	print new_files_list
	for new_file in new_files_list:		
		if not new_file:
			continue
		fr = open(new_file, "r")
		content = fr.read()
		fr.close()
		content = content.lower().replace(".", " ")
		content_words = content.split(" ") # get a list of words
		# Remove all strings = "" from content_words SO# 1157106
		parsed_words = filter(lambda a: a != "", content_words)

		lines = [whitespace_line.lower().strip() for whitespace_line in whitespace_lines]
		lines_str = " ".join(lines) # single string
		transcription = lines_str.split(" ") # single list

		set_transcription = set(transcription) 
		for word in set_transcription:
			if word not in ignore_chars:
				df[word] += 1 # defaultdict(0) makes this work even if the key does not exist in the dict initially 


	# Update the df values
	try:

		df_list = list()
		for key in df.keys():
			df_list.append(key + ">>" + str(df[key]) + "\n")
		
		df_file_w = open(saved_df_file_path, "w")
		df_file_w.writelines(df_list)
		df_file_w.close()


	except:
		print "Exception occured while trying to update file:"  + saved_df_file_path
		print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
		sys.exit(3)


	# Update the meta file
	try:
		# store timestamp in the file
		modtime = time.gmtime()
		meta_file_w = open(df_meta_file_path, "a")
		meta_file_w.write(str(modtime))
		meta_file_w.close()
	
	except:
		print "Exception encountered while trying to update file:" + df_meta_file_path
		print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
		sys.exit(3)


if __name__ == '__main__':
	# Pass in the name of the file containing df scores for each word as an argument
	if  len(sys.argv) != 3:
		print "Expecting syntax: python df.py /path/to/<saved_df_scores_file> /path/to/<df_meta_file>"
		sys.exit(1)

	# Path to the file containing the df scores for each word, upto the current occurence of running the script
	saved_df_file_path = sys.argv[1]

	# Path to the file containing the time-stamp when the last run of this script was completed. 
	df_meta_file_path = sys.argv[2]

	if not os.path.exists(saved_df_file_path):
		opt = raw_input("File " +  saved_df_file_path + " does not exist, enter Y to create it or N to exit")
		if opt == "Y":
			with file(saved_df_file_path, "a"):
				os.utime(saved_df_file_path)

		elif opt == "N":
			sys.exit(1)

	if not os.path.exists(df_meta_file_path):
		print "File " + df_meta_file_path + " does not exist, and it will be created."
		with file(df_meta_file_path):
			os.utime(df_meta_file_path)

	# Find all files created after the last modified time for the meta file
	# TODO-1: Change it to work with the MONGODB instance if needed
	proc = sp.Popen(["find", "data", "-cnewer", df_meta_file_path, "-iname", "*.txt"], stdout = sp.PIPE)
	out,err = proc.communicate()
	if proc.returncode:
		print "Error while trying to get list of new files from tf df meta file."
		sys.exit(2)

	new_files_list = out.split("\n")		

	df = read_df_vals_into_dict(saved_df_file_path)
	write_df_vals_to_file(saved_df_file_path, df)