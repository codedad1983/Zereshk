#!/usr/bin/env python
"""
    Zereshk
    ~~~~~~~~~~~~~~

    Downloader

    :copyright: (c) 2014 by Mehdi Bayazee.
    :license: BSD, see LICENSE for more details.
"""

import os
from config import PIDFILE_PATH, LOG_PATH


class ZereshkDownloader(object):
    max_jobs = 4

    def __init__(self):
        print 'Starting Zeresh Downloader ...'
        self.check_create_dirs()

    def check_create_dirs(self):
        for path in (LOG_PATH, PIDFILE_PATH):
            if not os.path.exists(path):
                os.mkdir(path)
