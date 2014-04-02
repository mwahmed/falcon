import cuewords
import tfidf
import pdb
import sys
from bson.objectid import ObjectId
from pymongo import MongoClient
import parser
import re

# Global variable used for debugging
debug_sentence_score = list()


# Debug flag
debug = 0
'''
Take the transcription and summary size ( as % of total sentences ) as input,
call the tfidf module and the cuewords module passing in the respective limits to each 
The results should also return the sentence idx, so that the sentences can be displayed in order.

 transcriptionLines stores the transcription as a list of strings
 summary_limit is the percentage of lines that should be in the summary
 saved_df_file_path is the path to the file containing df values for words
 zwords is string containing user defined keywords, separated by a ";"
 inv_zwords is same as above, but these are words NOT to be matched
'''

def summarize(transcriptionLines, summary_limit_percent, saved_df_file_path, zwords, inv_zwords):
	linecount = len(transcriptionLines)
	summary_limit_abs = int(summary_limit_percent/100.0 * linecount)
	# Note that cuewords and zwords are calculated together, so this function returns the 
	# cueword and the zword scores
	transcriptionLinesCopy = list()
	for line in transcriptionLines:
		transcriptionLinesCopy.append(re.sub("[.?!,;]", "", line))
	transcriptionLines = transcriptionLinesCopy
	cueword_zword_sentence_scores_idxs = cuewords.get_cuewords_zwords_scores(transcriptionLines, zwords, inv_zwords)
	tfidf_sentence_scores_idxs = tfidf.get_tfidf_scores(transcriptionLines, saved_df_file_path)
	combined_summary_scores = list()
	for idx in xrange(linecount):
		try:
			combined_score = tfidf_sentence_scores_idxs[idx][0] + cueword_zword_sentence_scores_idxs[idx][0]
			combined_summary_scores.append((combined_score, idx))
		except:
			print "#### Exception ####"
			print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]

	# sort in descending order
	combined_summary_scores.sort(reverse = True)
	
	summary = list()
	summary_idxs = list()
	for score, idx in combined_summary_scores[:summary_limit_abs]:
		summary_idxs.append(idx)

	# This for loop is for debugging purposes
	for score, idx in combined_summary_scores:
		debug_sentence_score.append((transcriptionLines[idx], score))
	summary_idxs.sort()
	#summary = [transcriptionLines[idx] for idx in summary_idxs]
	
	return summary_idxs

def debug_summarizer():
	global debug_sentence_score
	for line in debug_sentence_score:
		print line

'''
These lines were copied from the parser function. 
Only the functionality to split the lines is used here
'''
def splitTextIntoLines(transcriptionText):
	parsed_transcription = transcriptionText.replace("\n", " ")
	
	#convert acronyms like U.S. to US
	parsed_transcription = re.sub("([A-Z])\.", "\\1", parsed_transcription)
	
	# remove "..." and replace them with a space
	parsed_transcription = re.sub("\.[\.]+", " ", parsed_transcription)

	# Remove full stops and other sentence delineators, a space follows
	parsed_transcription = re.sub("[\.\?\!][ ]+", "\n", parsed_transcription)
	
	# Handle sentences that are separated by a ./?/! but no space
	parsed_transcription = re.sub("([a-z0-9])[\.\?\!]([A-Z])", "\\1\n\\2", parsed_transcription)

	parsed_transcription_lines_copy = parsed_transcription.split("\n")
	parsed_transcription_lines = list()
	
	for line in parsed_transcription_lines_copy:
		if line != "":
			if line[0] == " ":
				line = line[1:]

			if line[-1] == "."  or line[-1] == "?" or line[-1] == "!":
				parsed_transcription_lines.append(line[:-1] + "\n")
		 	else:
				parsed_transcription_lines.append(line + "\n")
	
	#Print "####################i#########################3#########################"
	#print parsed_transcription_lines
	#print "#######################################################################" 	
	return parsed_transcription_lines


# Get the transcription from the database
# Convert it into a list of strings
def main(post_id, summary_limit_percent, zwords, inv_zwords, sentence_delimiter, dbName):
	client = MongoClient('localhost', 27017)
	db =  client.ahks_development
	# Databases for storing audio transcripts and text are differnt
	if dbName == "transcriptions":
		userInputData = db.transcriptions
	elif dbName == "documents":
		userInputData = db.documents

	# Databases for storing audio transcripts and text are differnt
	document = userInputData.find_one({'_id': ObjectId(post_id)})
	if dbName == "transcriptions":
		transcriptionText = document['text']
	elif dbName == "documents":
		transcriptionText = document['data']
	
	# Unparsed transcription lines, to be displayed to the user
	transcriptionLines = list()

	if sentence_delimiter == "newline":
		transcriptionLines = transcriptionText.split("\n")

	else:
		# parsed_transcription_string parses the input so that the summarizer can calculate word scores easily
		transcriptionLines = parser.parse_transcription_string(transcriptionText)
	
	summary_limit_percent = float(summary_limit_percent)
	summary_idxs = summarize(transcriptionLines, summary_limit_percent, "/home/ubuntu/falcon/summarizer/saved_df.scores", zwords, inv_zwords)
	#summary_idxs = summarize(transcriptionLines, summary_limit_percent, "saved_df.scores", zwords, inv_zwords)
	summary = list()
	for summary_idx in summary_idxs:
		line = transcriptionLines[summary_idx]
		if line.find("{[") != -1:
			line = line.replace("{[", ".")
		summary.append(line)
	
	return summary

if __name__ == "__main__":
	post_id = sys.argv[1]
	summary_limit_percent = sys.argv[2]
	zwords = sys.argv[3]
	inv_zwords = sys.argv[4]
	sentence_delimiter = sys.argv[5]
	dbName = sys.argv[6]
	summary =  main(post_id, summary_limit_percent, zwords, inv_zwords, sentence_delimiter, dbName)
	for line in summary:
		print line

	# delimiter between output
	print ";;;ayush;;;"
	# 	
	topwords = tfidf.get_topN_words()
	for word in topwords:
		print word
