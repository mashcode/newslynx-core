#!/bin/sh
sudo su
sudo apt-get update -y
sudo apt-get install git python-pip postgresql postgresql-contrib -y
updatedb

# build postgres database
echo "build a database with:"
echo "* user_name postgres"
echo "* password - postgresql-{newslynx_password}"
echo "* db_name - nl"
# sudo -u postgres psql postgres

echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
echo "export PROJECT_HOME=$HOME/Devel" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
echo "unset SSH_ASKPASS" >> ~/.bashrc
source ~/.bashrc

# virtual env
mkvirtualenv newslynx-core
workon newslynx-core

# git repo
git clone https://github.com/newslynx/newslynx-core.git

# instlal dependencies
cd newslynx-core
pip install -r requirements.txt

# install newslynx
python setup.py install 

# build
./rebuild.sh

# TODO insert cronjobs