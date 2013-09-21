#!/usr/bin/ruby

tfidf={}
if ARGV[0].nil?
	p "Expecting syntax: ruby tfidf.rb <filename>"
	exit
end
fp=File.open("./data/#{ARGV[0]}","r")
file_input_data = fp.read.downcase
fp.close

# TODO: Cleanup the data. For eg: remove "a", "the", etc.
file_input_split = file_input_data.split(" ")
file_input_word_count = file_input_split.size
total_files = `ls -1 data/ | wc -l`.to_i
file_input_split.uniq.each do |word|
	_tf = (file_input_split.count(word))/file_input_word_count.to_f
	_idf = `grep -icr "#{word}" data/.`.split("\n").collect{|x| x if !x.include?(":0")}.compact.size
	if _idf!=0
		tfidf[word] = _tf * Math.log10(total_files/_idf.to_f)
	else
		tfidf[word] = 0.0
	end
	
end
p tfidf
