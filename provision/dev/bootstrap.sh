#!/usr/bin/env bash

sudo apt-add-repository ppa:nginx/stable -y
sudo apt-get update -y
sudo apt-get install -y nginx
sudo apt-get install python-pip -y
sudo apt-get install git -y

sudo cp /vagrant/provision/dev/nginx_site.conf /etc/nginx/sites-enabled/default
sudo service nginx restart

sudo apt-get install libevent-dev -y
sudo apt-get install libpq-dev -y
sudo apt-get install python-virtualenv -y
sudo apt-get install python-dev -y
sudo apt-get install libbz2-dev -y
sudo apt-get install libsqlite3-dev -y
sudo apt-get install libreadline-dev -y

sudo su vagrant <<'EOF'
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.4.2
pyenv rehash
pyenv virtualenv 3.4.2 tock
pyenv rehash
pyenv activate tock
pip install -r /vagrant/requirements.txt
cd /vagrant/tock
python manage.py migrate
EOF