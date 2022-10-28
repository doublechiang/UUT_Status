#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for, session
from flask_session import Session
import logging
from multiprocessing import Process
import threading
from itsdangerous import base64_encode
import requests
from urllib.parse import urlencode
import urllib
import base64, os
import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer
from flask_mail import Mail
from flask_mail import Message



# from tm import TestMonitor
from uut import Uut
from tm import TestMonitor
from test_station import TestStation
import settings

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'UUT_Status'
app.config['SESSION_PERMANENT'] = False
app.config["SESSION_TYPE"] = "filesystem"
# app.config['SESSION_KEY_PREFIX'] = 'session:'
# app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)
# app.config['SECRET_KEY'] = os.urandom(16).hex()
app.config['SECRET_KEY'] = 'FIXED'
app.secret_key = 'FIXED'
# app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
app.config.update(settings.mail_settings)
Session(app)
mail=Mail(app)

logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(level=logging.DEBUG)

# Commonly used Test Station instance
# tsl = list(map(lambda x: TestStation(x), TSs))
tsl = TestMonitor().pxes

def triggerSyncScan(trig_url):
    headers = {'Content-type': 'text/html; charset=UTF-8'}
    requests.post(trig_url, data=None, headers=headers)
    return 

@app.route('/', methods=['get', 'post'])
def home():
    return redirect(url_for('uut_main'))


@app.route('/ts/', methods = ['post'])
def test_station():
    """ Post command to sync and scan all directory
    """
    if request.method == 'POST':
        # to build TS directory
        threads = []
        for t in tsl:
            prjs = t.models
            tst = threading.Thread(target=t.sync_scan, args=(prjs,))
            tst.start()
            threads.append(tst)
            logging.debug("starting threading sync and build on {}".format(t.hostn))

        for tst in threads:
            tst.join()

        logging.debug("sync and scan completed for all TS")
        return 'TS Posted'
    return 'TS get'



@app.route('/uut/', methods=['get', 'post'])
def uut_main():
    token = request.args.get('token')
    logging.debug(f'token in uut_main: {token}')
    user = None
    if request.method == 'POST':
        token = request.form.get('token')
        print(f'POST token:{token}')
        if token is not None:
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            user = serializer.loads(token, salt=app.config['APPLICATION_ROOT'])

        sn=request.form.get('sn')
        if sn is not None:
            return redirect(url_for('uut_info', mlbsn=sn, token=token))


    trig_url = request.host_url + url_for('test_station')
    threading.Thread(target=triggerSyncScan, args=(trig_url,)).start()
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        user = serializer.loads(token, salt=app.config['APPLICATION_ROOT'])
    except Exception as error:
        logging.error(error)

    return render_template('uut.html', current_user=user, token=token)

@app.route('/uut/<mlbsn>', methods=['get'])
def uut_info(mlbsn):
    trig_url = request.host_url + url_for('test_station')
    triggerSyncScan(trig_url)
    uuts = []
    user = None
    for t in tsl:
        uut = t.GetUutFacotry(mlbsn)
        if uut is not None:
            logging.info("found uut SN:{} from PXE:{}".format(mlbsn, uut.ts.hostn))
            # since the UUT will swap between rack, check if the UUT's RM got the IP, if not, then skip
            if uut.ts.getLeaseIp(uut.rack_mount_mac1) is None:
                continue
            uuts.append(uut)

    token = request.args.get('token')
    logging.debug(f'token:{token}')
    user=None
    if token is not None:
        try:
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            user = serializer.loads(token, salt=app.config['APPLICATION_ROOT'])
        except Exception as error:
            logging.error(error)
            return redirect(url_for('login'), error=error)


    return render_template('uut.html', uuts=uuts, tm=TestMonitor(), current_user=user, token=token)

@app.route('/sshtunnel/create')
def create_tunnel():
    tm = TestMonitor()
    port = tm.getFreeTunnelPort()
    uut_ip = request.args.get('target')
    ts_ip = request.args.get('ts')
    logging.debug("uut_ip:{}, ts_ip{}".format(uut_ip, ts_ip))
    if uut_ip is None:
        pass
    if port is None:
        # Create 2 layers NAT SSH tunnel
        # Local tunnel -L 
        pass

    # from the test station ip get the username and password
    for ts in tm.pxes:
        if ts_ip == ts:
            ts_pass = ts.passw
            ts_user = ts.user
            break


    settings = tm.settings
    tunnel_host = settings.rdp_tunnel['host']
    tunnel_user = settings.rdp_tunnel['user']
    tunnel_pass = settings.rdp_tunnel['pass']

    cmd = 'sshpass -p {} ssh -o StrictHostKeyChecking=no -L {}:{}:{}:3389 {}@{}'.format(
        ts_pass, tunnel_host, port, uut_ip, ts_user, ts_ip)
    cmd_encode = urllib.parse.quote(cmd.encode())

    webssh = settings.webssh['host']
    base_url = webssh

    params = dict(username=tunnel_user, 
        password=base64.b64encode(tunnel_pass.encode()).decode('utf-8'),
        hostname=tunnel_host,
        command = cmd_encode)
    redirect_url = base_url + '?' + urlencode(params)
    return redirect(redirect_url)


@app.route("/login", methods=["POST", "GET"])
def login():
  # if form is submited
    if request.method == "POST":
        # record the user name
        # session["user"] = request.form.get("email")
        # return redirect('/uut')

        email = request.form.get("email")
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt=app.config['APPLICATION_ROOT'])
        login_url = request.host_url + url_for('mail_confirm')
        logging.debug(f"login_url is: {login_url}")

        subject = 'UUT Status Login Confirmation, click below link then copy/paste the confirmation code'
        now= datetime.datetime.now()
        dt_str = now.strftime("%m/%d/%Y, %H:%M:%S")
        m = Message(subject, recipients=[email])
        html= render_template('email/login_mail.html', email=email, login_url=login_url, current_dt=dt_str, token=token)
        m.html = html
        try:
            mail.send(m)
        except Exception as error:
            logging.error(error)
            return render_template('login.html', error=error)
        return redirect(url_for('mail_confirm'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["user"] = None
    session.pop('user')
    return redirect(url_for('home'))

@app.route('/mail_confirm/<string:token>')
@app.route('/mail_confirm/', methods=["POST", "GET"])
def mail_confirm(token=None):
    if request.method == "POST":
        token=request.form.get('token')
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = None
        try:
            email = serializer.loads(token, salt=app.config['APPLICATION_ROOT'])
            print(f"mail is {email}")
        except:
             logging.error('Mail authentication failed.')
        session['user'] = email
        session.modified = True
        print(f"session in mail_login() is: {session}")
        return redirect('/uut', token=token)

    # Get, send mail with a token with get, session doesn't work, always forward the token by ourselves.
    print(f'token:{token}')

    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        user = serializer.loads(token, salt=app.config['APPLICATION_ROOT'])
        print(f'user is {user}')
    except:
        redirect(url_for('login', error='Can not decode the crendentials, please consult the one who told you the link'))

    return redirect(url_for('uut_main', token=token))
    # return redirect(url_for('uut_main'))
    # return redirect('/uut')
    
    










    

