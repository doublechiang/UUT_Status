# UUT_Status

# Development mode
$ export FLASK_APP=app.py (app.py is the default app, so it's not required to set this command.)
$ export FLASK_ENV=development

## seeds data.
To get the seeds data
$ python seeds.py

## run the server
$ python -m flask run

# Deployment
Sync configuraiton is using ssh key authentication. 
use
$ python setup_env.py to setup the environment.


To deploy the Test station configuration, define it in the shell environment
UUT_SSHPASS='[user]:[pass]@[server],[user]:[pass]@[server]......'
No space in the environment, common separate for the server.
For example
$ export UUT_SSHPASS='log:log@192.168.0.130,[server]...'
$ export UUT_PRJS='prj,[prj]'


# Test
$ python -m unittest
