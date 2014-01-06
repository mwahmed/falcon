import cuewords
import tfidf
import pdb
import sys
from bson.objectid import ObjectId
from pymongo import MongoClient

# Take the transcription and summary size ( as % of total sentences ) as input,
# call the tfidf module and the cuewords module passing in the respective limits to each 
# The results should also return the sentence idx, so that the sentences can be displayed in order.

# transcriptionLines stores the transcription as a list of strings
# summary_limit is the percentage of lines that should be in the summary
# saved_df_file_path is the path to the file containing df values for words
def summarize(transcriptionLines, summary_limit_percent, saved_df_file_path):
	linecount = len(transcriptionLines)
	summary_limit_abs = int(summary_limit_percent/100.0 * linecount)
	cueword_sentence_scores_idxs = cuewords.get_cuewords_scores(transcriptionLines)
	tfidf_sentence_scores_idxs = tfidf.get_tfidf_scores(transcriptionLines, saved_df_file_path)
	combined_summary_scores = list()
	for idx in xrange(linecount):
		try:
			combined_score = tfidf_sentence_scores_idxs[idx][0] + cueword_sentence_scores_idxs[idx][0]
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

	summary_idxs.sort()
	summary = [transcriptionLines[idx] for idx in summary_idxs]
	return summary


# Get the transcription from the database
# Convert it into a list of strings
def main(post_id, summary_limit_percent):
	client = MongoClient('localhost', 27017)
	db =  client.ahks_development
	transcriptions = db.transcriptions
	document = transcriptions.find_one({'_id': ObjectId(post_id)})
	transcriptionText = document['text']
	transcriptionLines = transcriptionText.split("\n")
	summary_limit_percent = float(summary_limit_percent)
	return summarize(transcriptionLines, summary_limit_percent, "/home/ubuntu/falcon/summarizer/saved_df.scores")


if __name__ == "__main__":
	post_id = sys.argv[1]
	summary_limit_percent = sys.argv[2]
	summary =  main(post_id, summary_limit_percent)
	for line in summary:
		print line
