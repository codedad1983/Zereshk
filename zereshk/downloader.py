#!/usr/bin/env python
"""
    Zereshk
    ~~~~~~~~~~~~~~

    Downloader

    :copyright: (c) 2014 by Mehdi Bayazee.
    :license: BSD, see LICENSE for more details.
"""

import os
from config import PIDFILE_PATH, LOG_PATH, FAILED_RETRY
from models import Download
from time import sleep


class ZereshkDownloader(object):
    max_jobs = 4
    jobs = {}
    wget_cmd = ["wget", "-nd", "-np", "-c", "-r"]

    def __init__(self):
        print 'Starting Zeresh Downloader ...'
        self.check_create_dirs()

    def check_last_close_problems(self):
        "check if program terminated without update db and close downloads normally"
        pass

    def check_create_dirs(self):
        for path in (LOG_PATH, PIDFILE_PATH):
            if not os.path.exists(path):
                os.mkdir(path)

    def start_new_download(self, dl):
        if dl.status in ('running', 'finished'):
            return

        cmd = self.wget_cmd + ['-o%s' % dl.log_path, '-P %s' % dl.path, dl.url]
        print 'Command to exec:', cmd
        pid = None
        try:
            pid = os.spawnlp(os.P_NOWAIT, 'wget', *cmd)
        except Exception, inst:
            print "'%s': %s" % ("\x20".join(cmd), str(inst))
        else:
            dl.pid = pid
            dl.status = 'running'
            dl.save()
            print 'New download started. PK: %d, PID: %d, name: %s' % (dl.pk, dl.pid, dl.name)
        print 1
        os.wait()
        print 2
        return pid

    def run(self):
        while True:
            todos = list(Download.select().where((Download.status << ['waiting', 'failed']) &
                        (Download.try_count <= FAILED_RETRY)).limit(self.max_jobs - len(self.jobs)))

            if not len(todos):
                print 'Any new download! sleeping ...'
                sleep(10)
                continue
            else:
                print len(todos), 'new downloads ...'

            for todo in todos:
                new_pid = self.start_new_download(todo)
                self.jobs[new_pid] = todo.pk

            if len(self.jobs) >= self.max_jobs:
                (pid, status) = os.wait()
                print 'Wget terminated. PID: %d, status=%d' % (pid, status)
                # TODO: must be in another thread to catch any close jobs
                # TODO: remove from job list
                # TODO: if error retry

downloader = ZereshkDownloader()
downloader.run()