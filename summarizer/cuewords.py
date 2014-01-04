import sys
import os
import pdb
from collections import defaultdict

importantSentences = list()	
cuewordDS = defaultdict(int)

def populate_cueword_DS(cuewordsFileName):
	global cuewordDS
	cuewordsFile = open(cuewordsFileName)
	cuewordlines = cuewordsFile.readlines()
	rank = 0
	for line in cuewordlines:
		wordList = line.split(" ")
		word = wordList[0]
		score = int(wordList[1].strip())
		cuewordDS[word] = score
		
# read each sentence and calculate its score
def parse_speech_transcript(transcriptStr):
	global importantSentences
	transcriptLines = transcriptStr.split("\n")
	avg_sentence_score = 0
	sentence_count = 0
	for transcriptLine in transcriptLines:
		score = calculate_sentence_score(transcriptLine)
		
		avg_sentence_score += score
		sentence_count += 1

		if score > 0:
			importantSentences.append((score, sentence))

	# TODO: See if we need to add some limits, i.e. only include the sentences that have cueword rank sum greater than the avg	
		
# Calculate the score of a sentence, based on the cueword score of each sentence
def calculate_sentence_score(sentence):
	# To make lookup fast, see if the word is a key in the dictionary
	global cuewordDS
	score = 0
	sentenceList = sentence.split(" ")
	for word in sentenceList:		
		score += cuewordDS[word]
	
	return score


def main(speechTranscriptionAsStr):
	global importantSentences
	populate_cueword_DS("cuewords.txt")
	parse_speech_transcript(speechTranscriptionAsStr)
	# return the sentences containing cuewords
	cuewords_summary = [line[1] for line in importantSentences]

main(speechTranscriptionAsStr)