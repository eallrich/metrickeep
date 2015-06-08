import datetime
import json
import logging
import os
import time

from flask import Flask, abort, request

from . import settings
from .whisperdb import Whisper

logging.basicConfig(**settings.logging)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def root():
    return str(int(time.time()))


def find_whispers():
    whispers = []
    if not os.path.isdir(settings.whisper_path):
        return whispers
    
    # We're going to remove this prefix from results
    prefix = "%s/" % settings.whisper_path
    
    for root, _, files in os.walk(settings.whisper_path):
        root = root.replace(prefix, '')
        for name in files:
            # Drop the extension
            name = name.rsplit('.', 1)[0]
            path = os.path.join(root, name)
            whispers.append(path)
    
    return whispers


@app.route('/metrics', methods=['GET',])
def fetch():
    response = {'metrics': [w.replace('/','.') for w in find_whispers()]}
    return json.dumps(response)


@app.route('/metrics/<metric>')
def fetch_metric(metric):
    return fetch_metric_hour(metric)


@app.route('/metrics/<metric>/<start>/<end>')
def fetch_metric_interval(metric, start, end):
    wsp = Whisper(metric)
    timeinfo, values = wsp.fetch(start, end)
    start, stop, step = timeinfo
    
    response = {'start': start, 'stop': stop, 'step': step, 'values': values}
    return json.dumps(response)


@app.route('/metrics/<metric>/hour')
def fetch_metric_hour(metric):
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    start_ts = one_hour_ago.strftime("%s")
    end_ts = int(time.time())
    
    return fetch_metric_interval(metric, start_ts, end_ts)


@app.route('/metrics/<metric>/day')
def fetch_metric_day(metric):
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    start_ts = one_day_ago.strftime("%s")
    end_ts = int(time.time())

    return fetch_metric_interval(metric, start_ts, end_ts)


def save(metrics):
    logger.info("Saving %d metrics" % len(metrics))
    for m in metrics:
        wsp = Whisper(m['metric'])
        wsp.save(m['value'], m['timestamp'])


@app.route('/metrics', methods=['POST',])
def create():
    """Accepts metrics from clients
    
    Saves metrics to whispers for persistene"""
    if request.content_type != 'application/json':
        abort(415) # Unsupported media type
    
    data = request.get_json()
    
    try:
        # List or dictionary?
        _ = data[0]
    except KeyError:
        # It's a dictionary, make it a list for consistency
        data = [data,]
    
    metrics = []
    
    # Make sure the syntax is as expected. If not, return 400 Bad Syntax
    for document in data:
        clean = {}
        
        # Make sure all the keys exist
        for key in ('metric', 'value', 'timestamp',):
            try:
                clean[key] = document[key]
            except KeyError:
                return "Missing required key '%s'\n" % key, 400
        
        # Float-able value?
        try:
            clean['value'] = float(clean['value'])
        except (ValueError, TypeError):
            return "'value' (%r) must be a float\n" % clean['value'], 400
        
        # Int-able timestamp?
        try:
            clean['timestamp'] = int(clean['timestamp'])
        except (ValueError, TypeError):
            return "'timestamp' (%r) must be an int\n" % clean['timestamp'], 400
        
        metrics.append(clean)
    
    save(metrics)
    
    # Created
    return "Saved %d metrics\n" % len(metrics), 201

