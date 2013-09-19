#!/usr/bin/ruby

file_data = {}
file_input = ARGV[0]
ARGV.shift
compare_files = ARGV

ARGV.each do |file|
	fp = File.open(file,"r")
	file_words = fp.read
	fp.close
	file_words = file_words.downcase
	file_data[file]=file_words.split(" ")
end
word_array=[]
fp=File.open(file_input,"r")
file_input_data = fp.read
fp.close
file_input_data = file_input_data.gsub(".","")
file_input_data = file_input_data.gsub(",","")
file_input_data = file_input_data.split(" ")
file_input_data.each do |word|
	keys = file_data.keys
	search_results = file_data.select { |key, val| val.include?(word) }
	if search_results.keys.size==0
		word_array.push(word)
	end
end
p word_array.size
