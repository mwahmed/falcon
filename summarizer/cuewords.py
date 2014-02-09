import sys
import os
import pdb
from collections import defaultdict

cueword_zword_DS = defaultdict(float)

# TODO: Should we get all the cuewords, i.e. from AMI and the other corpus in Murray's thesis?
# load the cuewords into memory from the file
def populate_cueword_DS(cuewordsFileName):
	global cueword_zword_DS
	cuewordsFile = open(cuewordsFileName)
	cuewordlines = cuewordsFile.readlines()
	for line in cuewordlines:
		wordList = line.split(" ")
		word = wordList[0]
		# cuewords are ranked from 1 - 70.
		# Normalize the cuewords, so that the highest cueword has a rank of 1.0
		score = (71 - float(wordList[1].strip()))/70.0
		cueword_zword_DS[word] = score
		
# read each sentence and calculate its score
def parse_speech_transcript_and_get_summary(transcriptLines):
	importantSentences = list()
	for idx, transcriptLine in enumerate(transcriptLines):
		score = calculate_sentence_score(transcriptLine)
		importantSentences.append((score, idx))

	return importantSentences
		
# Calculate the score of a sentence, based on its cueword score
def calculate_sentence_score(sentence):
	# To make lookup fast, see if the word is a key in the dictionary
	global cueword_zword_DS
	sentence = sentence.lower()
	score = 0
	sentenceList = sentence.split(" ")
	for word in sentenceList:		
		# cuewords scores range from 1 - 70, with decreasing importance
		score += cueword_zword_DS[word]
	
	return score


# speechTranscriptionLines is the transcript, stored as a list of strings
def get_cuewords_zwords_scores(speechTranscriptionLines, zwords, inv_zwords):
	#populate_cueword_DS("/Users/ayushkulkarni/Documents/4S/ECE496/falcon/summarizer/cuewords.txt")
	populate_cueword_DS("/home/ubuntu/falcon/summarizer/cuewords.txt")
	if zwords != "":
		get_zwords_scores(zwords)
	
	if inv_zwords != "":
		handle_inv_zwords(inv_zwords)

	summary_idxs = parse_speech_transcript_and_get_summary(speechTranscriptionLines)
	return summary_idxs

# zwords is a string containing user defined keywords separated by a ";", all in lowercase
# The above function should call this function before populate_cueword_DS
def get_zwords_scores(zwords):
	global cueword_zword_DS
	zwords_list = list()
	if zwords.find(";") != -1:
		zwords_list = zwords.split(";")
	else:
		# if there is only a single zword
		zwords_list.append(zwords)
	for zword in zwords_list:
		# These will also be added to the cuewordsDS
		cueword_zword_DS[zword] = 1.0


# inv_zwords are words that the user does not want to include in the summary,
# they are passed in as a string separated by ";"

# This function assigns a score of negative 1 to inv_zwords so that they do not get included in the summary
def handle_inv_zwords(inv_zwords):
	global cueword_zword_DS
	inv_zwords_list = list()
	if inv_zwords.find(";") != -1:
		inv_zwords_list = inv_zwords.split(";")
	else:
		# if there's only a single inv_zword
		inv_words_list.append(inv_zwords)	
	for inv_zword in inv_zwords_list:
		# Add it to the cuewordsDS with a score of -1
		cueword_zword_DS[inv_zword] = -1.0 
