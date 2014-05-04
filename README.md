newslynx-core
=============
The core framework for populating newslynx's data store.

## Install
First, you must setup an account for [`manta`](http://www.joyent.com/products/manta) or login to ours:
* email: services@newslynx.org
* username: newslynx
* password: manta-{{our_services_password}}

Next, upload your ssh key, and then set these environmental variables:
```
export MANTA_URL=https://us-east.manta.joyent.com 
export MANTA_USER=newslynx 
export MANTA_KEY_ID=`ssh-keygen -l -f ~/.ssh/id_rsa.pub | awk '{print $2}' | tr -d '\n'`
```

You might also want to install `manta`'s node cli:
```
sudo npm install manta -g
```

Now you should be able to install `newslynx-core` and it's core dependencies via:

```
sudo pip install -r requirements.txt # why can't i incorporate this into setup.py ?
sudo python setup.py install
```

Or if you are responsible, first setup a virtual environment:

```
mkvirtualenv newslynx-core
pip install -r requirements.txt
python setup.py install
```

And then install optional libs. Read [this](http://stackoverflow.com/questions/8525193/how-to-install-jpype-on-os-x-lion-to-use-with-neo4j) before installing `boilerpipe`.

```
pip install git+https://github.com/grangier/python-goose.git
pip install boilerpipe
pip install git+https://github.com/stdbrouw/askmanta # waiting for Stijn's bugfix
```

## TK: Logic

## TK: Tests