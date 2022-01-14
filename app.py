#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for
import logging

from uut import Uut
from test_station import TestStation

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'UUT_Status'

TSs= "root@192.168.0.83 log@192.168.0.130".split()
# Commonly used Test Station instance
tsl = list(map(lambda x: TestStation(x), TSs))

@app.route('/', methods=['get', 'post'])
def home():
    return render_template('status.html')

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

    

