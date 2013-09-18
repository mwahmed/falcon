fp = File.open("file1","r")
file1 = fp.read
fp.close
fp = File.open("file2","r")
file2=fp.read
fp.close
fp = File.open("file3","r")
file3 = fp.read
fp.close
file3=file3.split(" ")
file2=file2.split(" ")
file1=file1.split(" ")

word_array=[]
file3.each do |word|
	if !file2.include?(word) and !file1.include?(word)
		word_array.push(word)
	end
end
p word_array
