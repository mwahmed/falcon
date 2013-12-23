#Configure Package Management System 
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

#Create a /etc/apt/sources.list.d/mongodb.list file
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list

sudo apt-get update

#Install MongoDB
sudo apt-get install mongodb-10gen

