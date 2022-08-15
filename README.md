# UUT_Status

# Development mode
$ export FLASK_APP=app.py (app.py is the default app, so it's not required to set this command.)
$ export FLASK_ENV=development

to eanble the virtual environemnt.
$ . ./venv/bin/activate

## seeds data.
To get the seeds data
$ python seeds.py

Sync configuraiton is using ssh key authentication. 
use
$ python setup_env.py to setup the environment.

## run the server
$ python -m flask run

# Deployment to Centos/Redhat Apache Server
$ yum install python3-flask
$ yum install python-mod_wsgi

Link the conf file into the /etc/httpd/conf.d
ln -s [abs_path_to_conf]/UUT_Status.conf /etc/httpd/conf.d/


# Test
$ python -m unittest
