#!/usr/bin/python
import sys
import os
import df as DF 
import math
import pdb
from collections import defaultdict

'''
This script calculates the tf (term frequency) for each word in the document
It uses the code in the df module to caculate the number of occurences of each word
'''
# The speech transcription is passed in as a list of strings
# The path to the file containing the saved df scores is also passed in as an argument
def get_tfidf_summary(input_transcription, saved_df_file):

	# Store a list of words that are specific to this document, and do not appear anywhere else
	doc_specific_words = []

	# list of strings that make up the summary, this will be returned
	summary = []
	# list of sorted linenumbers for sentences to be included in the summary
	summary_sentence_idxs = []

	tfidf = defaultdict()
	if not input_transcription:
		print "The transcription passed in to the get_tfidf_summary is empty"
		sys.exit(1)
		
	
	if not saved_df_file or not os.path.exists(saved_df_file):
		print "Path to saved_df_file does not exist or the argument passed to get_tfidf_summary is empty"
		sys.exit(1)
	
	ignored_words = ['', 'the', 'of', 'at', 'on', 'in', 'is', 'it',\
		     'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',\
		     'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',\
		     'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or']

	# convert the list into lower case
	list_input_transcription = []
	word_list_input_transcription = []
	input_transcription_word_len = 0

	for sentence in input_transcription:
		tmp_sent = sentence.lower()
		# store the transcription as a list of strings in lowercase
		list_input_transcription.append(tmp_sent)
		tmp_sent = tmp_sent.split(" ") # split it into a list of words
		for word in tmp_sent:
			input_transcription_word_len += 1
			if word not in ignored_words:
				word_list_input_transcription.append(word)
	

	freq = DF.read_df_vals_into_dict(saved_df_file)
	input_transcription_word_len = len(word_list_input_transcription)
	input_split = set(word_list_input_transcription)
	input_word_count = len(input_split)
	total_files = len(os.listdir("data/"))

	for word in input_split:
		tf = float(word_list_input_transcription.count(word))/input_transcription_word_len
		# DEBUG
		#print "tf[" + word + "]=", tf
		# pdb.set_trace()
		df = float(freq[word])
		if df > 0.0:
			tfidf[word] = tf * math.log10(total_files/df)
			# DEBUG
			# print "tfidf[" + word + "]=", tfidf[word], " ------ ", "df[" + word + "]=", freq[word]

		# if df is zero, this word has not been encountered before and so it should be a specific word
		elif df == 0.0:
			tfidf[word] = 0.0
			doc_specific_words.append(word)
			# DEBUG
			# print "tfidf[" + word + "]=", tfidf[word], " ------ ", "df[" + word + "]=", freq[word]


	# Calculate per sentence tfidf by adding tfidf values for every word in the transcription and dividing by the number of sentences
	sentence_avg_tfidf = 0.0
	num_sentences = len(list_input_transcription)
	for sentence in list_input_transcription:
		sentence_avg_tfidf += sum([tfidf[word] for word in sentence.split(" ") if word not in ignored_words])

	sentence_avg_tfidf /= num_sentences
	
	# Pick sentences for which the sum of individual tf-idf terms is higher than the avg tf-idf score per sentence 
	for sentence in list_input_transcription:
		sentence_tfidf = sum([tfidf[word] for word in sentence.split(" ") if word not in ignored_words])/len(sentence)
		if sentence_tfidf > sentence_avg_tfidf:
			summary_sentence_idxs.append(sentence)
	
	# select words that will have tf-idf of zero, but do not appear in any other document
	print doc_specific_words
	for word in doc_specific_words:
		for idx, sentence in enumerate(list_input_transcription):
			if idx not in summary_sentence_idxs and word in sentence:
				summary_sentence_idxs.append(idx)

	# sort the indices of the sentences that are to be part of the summary so that the summary may be in correct order.
	summary_sentence_idxs.sort()
	summary = [list_input_transcription[idx] for idx in summary_sentence_idxs]
	return summary