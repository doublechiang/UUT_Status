#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for
import logging
from multiprocessing import Process
import threading
from itsdangerous import base64_encode
import requests
from urllib.parse import urlencode
import urllib
import base64
from tm import TestMonitor

# from tm import TestMonitor
from uut import Uut
from test_station import TestStation
import settings

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'UUT_Status'
logging.basicConfig(level=logging.DEBUG)

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


@app.route('/ts/<hostn>')
def get_tsl(hostn):
    """ Get Test Station Listing
    """
    racks = {}
    for ts in tsl:
        ts.getRackFactory()
        if hostn == ts.hostn:
            uuts = ts.GetUutFacotry(prjl)
            return render_template('ts.html', ts=ts, uuts=uuts)

@app.route('/rack/')
def racks():
    trig_url = request.host_url + url_for('test_station')
    triggerSyncScan(trig_url)
    # map to list of TestStation instance
    racks = dict()
    for t in tsl:
        racks.update(t.getRackFactory())
    return render_template('rack.html', racks=racks)

@app.route('/rack/<rsn>')
def rack(rsn):
    # map to list of TestStation instance
    racks = []
    for t in tsl:
        r_list = t.getRackFactory()
        racks.extend(r_list)

    for r in racks:
        print(r)
    return render_template('rack.html', racks=racks)



@app.route('/uut/', methods=['get', 'post'])
def uut_main():
    if request.method == 'POST':
        sn=request.form.get('sn')
        return redirect(url_for('uut_info', mlbsn=sn))

    trig_url = request.host_url + url_for('test_station')
    threading.Thread(target=triggerSyncScan, args=(trig_url,)).start()
    return render_template('uut.html')

@app.route('/uut/<mlbsn>')
def uut_info(mlbsn):
    trig_url = request.host_url + url_for('test_station')
    triggerSyncScan(trig_url)
    uuts = []
    for t in tsl:
        uut = t.GetUutFacotry(mlbsn)
        if uut is not None:
            logging.info("found uut SN:{} from PXE:{}".format(mlbsn, uut.ts.hostn))
            # since the UUT will swap between rack, check if the UUT's RM got the IP, if not, then skip
            if uut.ts.getLeaseIp(uut.rack_mount_mac1) is None:
                continue
            uuts.append(uut)
    
    return render_template('uut.html', uuts=uuts, tm=TestMonitor())

@app.route('/sshtunnel/create')
def create_tunnel():
    tm = TestMonitor()
    port = tm.getFreeTunnelPort()
    uut_ip = request.args.get('target')
    ts_ip = request.args.get('ts')
    logging.debug("uut_ip:{}, ts_ip:{}".format(uut_ip, ts_ip))
    if uut_ip is None:
        pass
    if port is None:
        # Create 2 layers NAT SSH tunnel
        # Local tunnel -L 
        pass

    # from the test station ip get the username and password
    logging.debug(f"tm.pxes:{tm.pxes}")
    for ts in tm.pxes:
        logging.debug(f"ts in tm.pxes:{ts}")
        if ts_ip == ts.ip:
            ts_pass = ts.passw
            ts_user = ts.user
            logging.debug(f'ts ip {ts_ip}, user:{ts_user}, pass:{ts_pass}')
            break

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









    

