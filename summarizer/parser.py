import sys
import re
'''
This script parses text to convert it to a form that can be processed by the summarizer modules
This needs to be changed to also be able to take string as input
'''

# Make phrases into a single word so that the score gets assigned appropriately
def handlePhrases(parsed_transcription_lines):
	print "TODO: Handle Phrases"


# transcript is a string
# This method is used in testing
def parse_transcription(filepath):
	# read the text input
	transcriptFile = sys.argv[1]
	fr = open(transcriptFile, "r")
	transcription = fr.read()
	fr.close();
	parsed_transcription = parse_transcription_string(transcription)
	
	'''fw = open(filepath, "w")
	lastLineIdx = len(parsed_transcription_lines)
	for idx, line in enumerate(parsed_transcription_lines):
		if (line != "" and line != None):
			if (line[0] == " "):
				line = line[1:]
			if idx < lastLineIdx:
				fw.write(line + "\n")
	fw.close()	
	'''
	return parsed_transcription

# This method is called in the actual summarizer module
# The argument "transcription" is a string
def parse_transcription_string(transcription):
	parsed_transcription = transcription.replace("\n", " ")
	
	parsed_transcription = re.sub("[\"]", "", parsed_transcription)

	# TODAY's changes
	#parsed_transcription = re.sub("([A-Z])[\.]", "\\1", parsed_transcription)
	#print "###################################################################"
	#print parsed_transcription 
	#print "###################################################################"

	# remove "..." and replace them with a space
	parsed_transcription = re.sub("\.[\.]+", " ", parsed_transcription)

	# handle decimal points carefully
	parsed_transcription = re.sub("([0-9\"]+)[\.]([^0-9])", "\\1\n\\2", parsed_transcription)

	# parsed_transcription = re.sub("([a-z]+)[\.]", "\\1\n", parsed_transcription)

	# Remove full stops and other sentence delineators
	# parsed_transcription = re.sub("[.?!] ", "\n", parsed_transcription)
	# Handle sentences that are separated by a full-stop and a space, 
	#parsed_transcription = re.sub("[\.\?\!][ ]+([A-Z])", "\n\\1", parsed_transcription)
	parsed_transcription = re.sub("[\.\?\!][ ]+", "\n", parsed_transcription)
	# Handle sentences that are separated by a full-stop but no space
	parsed_transcription = re.sub("([a-zA-Z])[\.\?\!]([A-Z][^\.^\n])", "\\1\n\\2", parsed_transcription)
	
	# TODAY's changes
	parsed_transcription_lines_copy = parsed_transcription.split("\n")
	#parsed_transcription_lines_copy = parsed_transcription.split("\r")
	parsed_transcription_lines = list()

	for line in parsed_transcription_lines_copy:
		if line[-1] == "."  or line[-1] == "?" or line[-1] == "!":
			parsed_transcription_lines.append(line[:-1])
		else:
			parsed_transcription_lines.append(line)

	#Print "####################i#########################3#########################"
	#print parsed_transcription_lines
	#print "#######################################################################" 	
	return parsed_transcription_lines

if __name__ == "__main__":
	if sys.argv[1] == "":
		print "Usage: parser.py path_to_transcription_file"
	else:
		parse_transcription(transcription, transcriptFile)
