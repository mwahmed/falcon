
sudo apt-get update
sudo apt-get install curl -y

#To install RVM
\curl -L https://get.rvm.io | bash -s stable

# load RVM
source ~/.rvm/scripts/rvm

#To install dependancies 
rvm requirements

#To install Ruby
rvm install ruby

rvm use ruby --default

#To install RubyGems
rvm rubygems current

#To install Rails
gem install rails --no-ri --no-rdoc

