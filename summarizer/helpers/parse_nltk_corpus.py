import sys
import os
import re
from collections import defaultdict
import pdb

# parse brown corpus, convert to plain english text
def convert_to_plain_english(content):
	res = re.sub("/[a-z].*? ", " ", content)
	#print res
	res = re.sub("``.``", "", res)
	res = re.sub("''.''", "", res)
	#print res
	res = re.sub("[.,;/.,;]", "", res)
	#print res
	return res 

def parse_unneeded_chars(content):
	# remove punctuation and other characters from the string
	for ch in [". ", ", ", "? ", "! ", "-"]:
		content = content.lower().replace(ch, " ")

	for ch in ["\"", ",", ";", "(", ")", "_", "#", "\r", "\n", "\t",  ">", "<", "{", "}", "/", "[", "]", ":", "*", "+", "!", "?"]:
		content = content.replace(ch, "")

	return content

# path to parsed NLTK data
destPathToCorpus = "brown_parsed"

path = os.getcwd()
# get only the list of files

# path to unparsed NLTK data, change this depending on the corpus you want to parse
srcFiles = list()
for srcPathToCorpus in ["brown", "reuters/training"]:
	srcFiles += [ srcPathToCorpus + "/" + srcFile for srcFile in os.listdir(srcPathToCorpus) if not os.path.isfile(os.path.join(path,srcFile)) and srcFile[0] != "." and srcFile != "README" and srcFile.find(".") == -1 and srcFile != "CONTENTS" ]

print len(srcFiles)
global_df = defaultdict(int)
for srcFile in srcFiles:
	# to keep track of words occuring in a single file
	local_df = defaultdict(int)
	fr = open(srcFile, "r")
	content = fr.read()
	fr.close()
	content = content.lower()
	
	content = convert_to_plain_english(content)
	content = parse_unneeded_chars(content)
	
	# save the parsed file
	# fw1 = open(destPathToCorpus+"/"+srcFile, "w")
	# fw1.write(content)
	# fw1.close()

	# split the string into a list of words
	content_words = content.split(" ")
	# remove empty "" from the strings
	parsed_words = filter(lambda a: a != "" or a != '', content_words)
	del content_words
	del content
	#print parsed_words
	for word in parsed_words:
		local_df[word] = 1

	# update global occurence
	for word in local_df.keys():
		global_df[word] += 1


fw = open("saved_df.scores.2", "w")
for key, value in global_df.items():
	fw.write(str(key) + ">>" + str(value) + "\n")
fw.close()