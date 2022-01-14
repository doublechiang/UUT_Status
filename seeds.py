#!/usr/bin/env python3

import os
import test_station

tss = "log@192.168.0.130 root@192.168.0.83".split()
hop = "cchiang@192.168.66.95"

if __name__ == '__main__':
    # if flask_env env is development will not sync
    if os.getenv('FLASK_ENV') == 'development':
        del os.environ['FLASK_ENV']

    for ts in tss:
        t = test_station.TestStation(ts)
        t.sync(hop=hop)
        

