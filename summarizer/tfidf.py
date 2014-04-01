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

# The total number of files used to get list of tf-idf words
total_files = 8269

# The speech transcription is passed in as a list of strings
# The path to the file containing the saved df scores is also passed in as an argument
# This function also sets doc_specific_words

def get_tfidf_scores(input_transcription, saved_df_file):
	global tfidf
	global total_files

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
	
	# Store the tfidf values for the transcription's words in the tfidf dictionary
	calculate_word_tfidf_scores(word_list_input_transcription, saved_df_file)

	# Store the tf-idf values for each sentence in a list
	num_sentences = len(list_input_transcription)
	for idx, sentence in enumerate(list_input_transcription):
		#sentence_tfidf_variance = get_sentence_tfidf_variance(sentence, ignored_words)
		#sentence_tfidf_total = get_sentence_tfidf_total(sentence, ignored_words)
		sentence_top_tfidf_variance = get_sentence_tfidf_variance_and_topThirdWords(sentence, ignored_words)
		summary_sentence_idxs.append((sentence_top_tfidf_variance, idx))
		 	
	return summary_sentence_idxs


# Calculate the tfidf score of each word in the transcription using the saved_df file
# Write these values into the global tfidf Dictionary
def calculate_word_tfidf_scores(word_list_input_transcription, saved_df_file):

	global tfidf
	global doc_specific_words
	# REMEMBER TO UPDATE this total_files variable everytime you get more tf-idf data
	global total_files

	input_transcription_word_len = len(word_list_input_transcription)
	# Creates a set, i.e. repeated words appear only once in this data structure
	input_transcription_word_set = set(word_list_input_transcription)
	input_word_count = len(input_transcription_word_set)

	freq = DF.read_df_vals_into_dict(saved_df_file)

	for word in input_transcription_word_set:
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


# Calculate the total tfidf score for each sentence
def get_sentence_tfidf_total(sentence, ignored_words):
	global tfidf
	sentence_tfidf = 0.0
	for word in sentence.split(" "):
		if word not in ignored_words:
			sentence_tfidf += tfidf[word]
	
	return sentence_tfidf		

# Calculate the tfidf variance score for each sentence
def get_sentence_tfidf_variance(sentence, ignored_words):
	global tfidf
	sentence_tfidf = 0.0
	sentence_tfidf_variance = 0.0
	sentence_length = 0
	for word in sentence.split(" "):
		if word not in ignored_words:
			sentence_tfidf += tfidf[word]
			sentence_length += 1


	sentence_tfidf_avg = sentence_tfidf / sentence_length
	for word in sentence.split(" "):
		if word not in ignored_words:
			sentence_tfidf_variance += abs(sentence_tfidf_avg - tfidf[word])

	#sentence_tfidf_variance /= sentence_length
	return ( ( 0.25 * sentence_tfidf_variance) + (0.75 * sentence_tfidf) )		


# Calculate the tfidf variance score for each sentence
# Also calculate the avg of the top "n" % of words in each sentence
def get_sentence_tfidf_variance_and_topThirdWords(sentence, ignored_words):
	if sentence == "":
		return 0.0
	global tfidf
	word_tfidf_scores = list()
	sentence_tfidf_variance = 0.0
	sentence_tfidf_avg = 0.0
	sentence_length = 0
	for word in sentence.split(" "):
		if word not in ignored_words:
			word_tfidf_scores.append(tfidf[word])
			sentence_tfidf_avg += tfidf[word]
			sentence_length += 1


	word_tfidf_scores.sort(reverse = True)

	topWordThreshold = int(0.33 * sentence_length)
	if topWordThreshold >= sentence_length:
		print "Something's wrong, sentence_length=" + str(sentence_length) + "Top Word Threshold=" + str(topWordThreshold)
		print "Sentence is:", sentence
		return 0.0
		#pdb.set_trace()
	
	sentence_tfidf = sum(word_tfidf_scores[:(topWordThreshold + 1)])
	sentence_tfidf_avg /= sentence_length

	for word in sentence.split(" "):
		if word not in ignored_words:
			sentence_tfidf_variance += abs(sentence_tfidf_avg - tfidf[word])

	sentence_tfidf_variance /= sentence_length
	return ( ( -1.0 * 0.25 * sentence_tfidf_variance) + (1.00 * sentence_tfidf) )		


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
