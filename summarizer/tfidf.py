#!/usr/bin/python
import sys
import os
import df as DF 
import math
import pdb
from collections import defaultdict
from operator import itemgetter

'''
This script calculates the tf (term frequency) for each word in the document
It uses the code in the df module to caculate the number of occurences of each word
'''
# Store a list of words that are specific to this document, and do not appear anywhere else 
doc_specific_words = []

# The global var which will store tf-idf values
tfidf = defaultdict()
# The speech transcription is passed in as a list of strings
# The path to the file containing the saved df scores is also passed in as an argument
# This function also sets doc_specific_words
def get_tfidf_scores(input_transcription, saved_df_file):
	global tfidf
	# stores (sentence_tf_idf_score, sentence_idx) 
	# returned to the caller
	summary_sentence_idxs = []

	if not input_transcription:
		print "The transcription passed in to the get_tfidf_summary is empty"
		sys.exit(1)
		
	
	if not saved_df_file or not os.path.exists(saved_df_file):
		print "Path to saved_df_file:" + saved_df_file + " does not exist or the argument passed to get_tfidf_summary is empty"
		sys.exit(1)
	
	ignored_words = ['', 'the', 'of', 'at', 'on', 'in', 'is', 'it',\
		     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',\
		     'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',\
		     'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or', 'not', 'to', 'do', 'don\'t']

	# convert the list into lower case
	list_input_transcription = []
	word_list_input_transcription = []

	for sentence in input_transcription:
		tmp_sent = sentence.lower()
		# store the transcription as a list of strings in lowercase
		list_input_transcription.append(tmp_sent)
		tmp_sent = tmp_sent.split(" ") # split it into a list of words
		for word in tmp_sent:
			if word not in ignored_words:
				word_list_input_transcription.append(word)
	

	freq = DF.read_df_vals_into_dict(saved_df_file)
	input_transcription_word_len = len(word_list_input_transcription)
	input_split = set(word_list_input_transcription)
	input_word_count = len(input_split)
	total_files = 8269
	#print "###########################################################################################"
	#print "REMEMBER TO UPDATE THE total_files variable in tfidf.py everytime you get more tf-idf data"
	#print "###########################################################################################"

	for word in input_split:
		tf = float(word_list_input_transcription.count(word))/input_transcription_word_len
		# DEBUG
		# print "tf[" + word + "]=", tf
		# pdb.set_trace()
		df = float(freq[word])
		if df > 0.0:
			tfidf[word] = tf * math.log10(total_files/df)
			# DEBUG
			# print "tfidf[" + word + "]=", tfidf[word], " ------ ", "df[" + word + "]=", freq[word]

		# if df is zero, this word has not been encountered before and so it should be given tfidf score of 1
		elif df == 0.0:
			tfidf[word] = 1.0
			doc_specific_words.append(word)
			# DEBUG
			# print "tfidf[" + word + "]=", tfidf[word], " ------ ", "df[" + word + "]=", freq[word]


	# Store the tf-idf values for each sentence in a list
	num_sentences = len(list_input_transcription)
	for idx, sentence in enumerate(list_input_transcription):
		sentence_tfidf = 0.0
		for word in sentence.split(" "):
			if word not in ignored_words:
				sentence_tfidf += tfidf[word]
		summary_sentence_idxs.append((sentence_tfidf, idx))
		 	
	return summary_sentence_idxs



'''
This function returns doc_specific_words to the user
TODO: Make this smarter, uses NLTK POS tagging to get nouns
'''
def get_doc_specific_words():
	return doc_specific_words


'''
Return the top-10 highest scoring words to the user
'''
def get_top10_words():
	tfidf_tuples = tfidf.items()
	tfidf_tuples = sorted(tfidf_tuples, reverse=True, key = itemgetter(1))
	top10words = [tup[0] for tup in tfidf_tuples[0:10] ]
	return top10words
