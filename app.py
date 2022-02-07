#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for
import logging
from multiprocessing import Process
import threading
import requests
from tm import TestMonitor

from uut import Uut
from test_station import TestStation

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'UUT_Status'
logging.basicConfig(level=logging.DEBUG)

# Commonly used Test Station instance
# tsl = list(map(lambda x: TestStation(x), TSs))
tsl = TestStation.getTestStationFactory()


def triggerSyncScan():
    headers = {'Content-type': 'text/html; charset=UTF-8'}
    requests.post(request.url_root + url_for('test_station'), data=None, headers=headers)
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
        prjs = TestMonitor.getSupportedPrj()
        threads = []
        for t in tsl:
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
    for ts in tsl:
        if hostn == ts.hostn:
            uuts = ts.GetUutFacotry(prjl)
            return render_template('ts.html', ts=ts, uuts=uuts)

@app.route('/rack/')
def racks():
    # map to list of TestStation instance
    racks = []
    for t in tsl:
        t.sync(prjl)
        rs = t.getRackFactory()
        racks.extend(rs)

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
    threading.Thread(target=triggerSyncScan()).start()
    if request.method == 'POST':
        sn=request.form.get('sn')
        return redirect(url_for('uut_info', mlbsn=sn))

    return render_template('uut.html')

@app.route('/uut/<mlbsn>')
def uut_info(mlbsn):
    triggerSyncScan()
    uuts = []
    for t in tsl:
        uut = t.GetUutFacotry(mlbsn)
        if uut is not None:
            logging.info("found uut SN:{} from PXE:{}".format(mlbsn, uut.ts.hostn))
            # since the UUT will swap between rack, check if the UUT's RM got the IP, if not, then skip
            if uut.ts.getLeaseIp(uut.rack_mount_mac1) is None:
                continue
            uuts.append(uut)
    
    return render_template('uut.html', uuts=uuts)







    

