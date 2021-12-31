from flask import Flask, request, redirect, render_template, url_for
from flask import send_file

from uut import Uut

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'UUT_Status'

@app.route('/', methods=['get', 'post'])
def home():
    uuts = Uut.parse_dir('samples/WIN/Response')
    return  render_template('status.html', listing=uuts)
