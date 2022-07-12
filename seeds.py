#!/usr/bin/env python3

import os
import test_station
# import tm
import logging


import settings

""" This file is used for development purpose.
    Copy the seeds data from PXE test station accroding to the settings
"""

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # unset the development mode, if flask_env env is development will not sync
    if os.getenv('FLASK_ENV') == 'development':
        del os.environ['FLASK_ENV']

    for ts in settings.tss:
        t = test_station.TestStation(**ts)
        t.sync(hop=settings.hop_station)
        

