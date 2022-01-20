#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for
import logging

from uut import Uut
from test_station import TestStation

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'UUT_Status'

# Commonly used Test Station instance
# tsl = list(map(lambda x: TestStation(x), TSs))
tsl = TestStation.getTestStationFactory()

@app.route('/', methods=['get', 'post'])
def home():
    # return render_template('status.html')
    return redirect(url_for('racks'))

@app.route('/ts/')
def test_station():
    """ Listing all of the test stations
    """
    # map to list of TestStation instance
    for t in tsl: t.sync()

    return render_template('tsr.html', tsl=tsl)

@app.route('/ts/<hostn>')
def get_tsl(hostn):
    """ Get Test Station Listing
    """
    for ts in tsl:
        if hostn == ts.hostn:
            uuts = ts.GetUutFacotry()
            return render_template('ts.html', ts=ts, uuts=uuts)

@app.route('/rack/')
def racks():
    # map to list of TestStation instance
    racks = []
    for t in tsl:
        t.sync()
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



@app.route('/uut')
def uuts():
    uuts=[]
    for t in tsl:
        t.sync()
        part_uuts = t.GetUutFacotry()
        uuts.extend(part_uuts)

    return render_template('uut.html', uuts=uuts)



    

