import os
from uuid import uuid4
import threading
import config
from subprocess import Popen, PIPE
from time import sleep


class DownloadInfo(object):
    def __init__(self, link, username, password):
        self.key = str(uuid4())
        self.link = link
        self.username = username
        self.password = password

    @property
    def log_path(self):
        return os.path.join(config.PATH_LOG, '%s.log' % self.key)


class WgetOutputHandler(object):
    def __init__(self):
        self.ip = '0.0.0.0'
        self.total_size = "0K"
        self.target = ''
        self.percent = "0%"
        self.speed = "0K/s"
        self.time_left = ""
        self.downloaded_size = "0K"
        self.error = ()

    def process(self, s):
        if not s:
            return

        line = s.split(' ')
        print 'WGET:', s
        if line[1] == '..........':
            self.downloaded_size = line[0]
            self.percent = line[6]
            self.speed = line[7]
            self.time_left = line[8]
        elif line[0] == 'Resolving':
            self.ip = line[-1]
        elif line[0] == 'Length:':
            self.total_size = line[1]
        elif line[0] == 'Saving':
            self.target = line[-1][:-1]
        elif (s.find('416 Requested Range Not Satisfiable')):
            self.error = ('416_1', 'Requested Range Not Satisfiable')

        print self.to_string()
        print '='*20

    def to_string(self):
        return ('\n\t' + self.target+'\n\t'
            +self.total_size+'\n\t'
            +self.downloaded_size+'\n\t'
            +self.ip+'\n\t'
            +self.percent+'\n\t'
            +self.speed+'\n\t'
            +self.time_left)


def wget_command(dl_data, resume=True):
    wget_opts = ['wget']
    if resume:
        wget_opts += ['-c']
    cmd = wget_opts + ['-P %s' % config.PATH_WORK, dl_data.link]
    return cmd


class DownloadThread(threading.Thread):
    def __init__(self, dl_info):
        super(DownloadThread, self).__init__()
        self.data = dl_info
        self.stop_flag = False
        self.done = False
        self.status = WgetOutputHandler()

    def run(self):
        print 'Starting download'
        pipe = Popen(wget_command(self.data, resume=False), stdout=PIPE, stderr=PIPE)

        pipe_out = pipe.stderr

        while (pipe.poll() == None and self.stop_flag == False):
            # TODO: check how much this loop execute and if it needed increase sleep time
#             print self.data.key, 'Going to read new data from WGET output'
            self.status.process(pipe_out.readline().strip())
#             print self.data.key, 'WGET output processed. sleeping ...'
            sleep(0.001)

        # TODO: handle this
        # wget print some errors and outputs by stdout
        std_out = pipe.stdout.readline()

        if pipe.returncode == None:
            pipe.kill()

        self.done = True


class ThreadedDownloadManager(object):
    pool = {}

    def add_download(self, link, username=None, password=None):
        dl_info = DownloadInfo(link, username, password)
        dl = DownloadThread(dl_info)
        dl.start()
        self.pool[dl.data.key] = dl

    def run(self):
        while True:
            sleep(1)

if __name__ == '__main__':
    tdm = ThreadedDownloadManager()
    tdm.start_new_download('http://flask.pocoo.org/docs/flask-docs.pdf')
