class StaticController < ApplicationController

	def basic

	end

	def index

	end

	def file
		p "in controller"
		p params
	  



	file = File.new("/tmp/audio/test.wav", "w+b")
	file.write request.raw_post
	file.close
		render json: params
	end


end
