#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, url_for
import logging

from uut import Uut
from test_station import TestStation

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'UUT_Status'

@app.route('/', methods=['get', 'post'])
def home():
    return redirect(url_for('test_station'))


@app.route('/ts/')
def test_station():
    """ Listing all of the test stations
    """
    TSs= "root@192.168.0.83".split()
    # map to list of TestStation instance
    tsl = list(map(lambda x: TestStation(x), TSs))
    for t in tsl:
        t.sync()
        pass

    return render_template('tsr.html', tsl=tsl)

@app.route('/ts/<hostn>')
def get_tsl(hostn):
    """ Get Test Station Listing
    """
    ts = TestStation(hostn)
    uuts = ts.GetUutFacotry()
    return render_template('ts.html', ts=ts, uuts=uuts)


