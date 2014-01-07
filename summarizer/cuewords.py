import sys
import os
import pdb
from collections import defaultdict

cuewordDS = defaultdict(int)

# TODO: Should we get all the cuewords, i.e. from AMI and the other corpus in Murray's thesis?
# load the cuewords into memory from the file
def populate_cueword_DS(cuewordsFileName):
	global cuewordDS
	cuewordsFile = open(cuewordsFileName)
	cuewordlines = cuewordsFile.readlines()
	for line in cuewordlines:
		wordList = line.split(" ")
		word = wordList[0]
		# cuewords are ranked from 1 - 70.
		score = 70 - int(wordList[1].strip())
		cuewordDS[word] = score
		
# read each sentence and calculate its score
def parse_speech_transcript_and_get_summary(transcriptLines):
	importantSentences = list()
	for idx, transcriptLine in enumerate(transcriptLines):
		score = calculate_sentence_score(transcriptLine)
		importantSentences.append((score, idx))

	return importantSentences
		
# Calculate the score of a sentence, based on the cueword score of each sentence
def calculate_sentence_score(sentence):
	# To make lookup fast, see if the word is a key in the dictionary
	global cuewordDS
	sentence = sentence.lower()
	score = 0
	sentenceList = sentence.split(" ")
	for word in sentenceList:		
		# cuewords scores range from 1 - 70, with decreasing importance
		score += cuewordDS[word]
	
	return score


# speechTranscriptionLines is the transcript, stored as a list of strings
def get_cuewords_scores(speechTranscriptionLines):
	populate_cueword_DS("/home/ubuntu/falcon/summarizer/cuewords.txt")
	summary_idxs = parse_speech_transcript_and_get_summary(speechTranscriptionLines)
	return summary_idxs
