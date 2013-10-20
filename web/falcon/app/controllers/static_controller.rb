class StaticController < ApplicationController

	def basic

	end

	def index

	end

	def file
		p "in controller"
		p params
	  



	file = File.new("public/test.wav", "w+b")
	file.write request.raw_post
	file.close
		
	file = File.new("public/test.flac", "w+b")
	file.write request.raw_post
	file.close
		
	render json: params
	end


end
