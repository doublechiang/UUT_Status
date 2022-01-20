# UUT_Status

# Development
$ export FLASK_APP=app.py (app.py is the default app, so it's not required to set this command.)
$ export FLASK_ENV=development


# Configuration
To deploy the Test station configuration, define it in the shell environment
UUT_SSHPASS='[user]:[pass]@[server],[user]:[pass]@[server]......'
No space in the environment, common separate for the server.
For example
$ export UUT_SSHPASS='log:log@192.168.0.130'

# run the server
$ python -m flask run

