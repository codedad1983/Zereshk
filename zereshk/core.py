import os
from uuid import uuid4
import threading
import config
from subprocess import Popen, PIPE
from time import sleep
import zmq
from Queue import Queue


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

#         print self.to_string()
#         print '='*20

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
    cmd = wget_opts + ['-P%s' % config.PATH_WORK, dl_data.link]
    return cmd


class DownloadThread(threading.Thread):
    def __init__(self, dl_info, download_stop_handler):
        super(DownloadThread, self).__init__()
        self.data = dl_info
        self.stop_flag = False
        self.done = False
        self.status = WgetOutputHandler()
        self.download_stop_handler = download_stop_handler

    def run(self):
        print 'Starting download'
        pipe = Popen(wget_command(self.data, resume=False), stdout=PIPE, stderr=PIPE)

        pipe_out = pipe.stderr

        while (pipe.poll() == None and self.stop_flag == False):
            # TODO: check how much this loop execute and if it needed increase sleep time
#             print self.data.key, 'Going to read new data from WGET output'
            self.status.process(pipe_out.readline().strip())
#             print self.data.key, 'WGET output processed. sleeping ...'
            sleep(0.01)

        # TODO: handle this
        # wget print some errors and outputs by stdout
        std_out = pipe.stdout.readline()

        if pipe.returncode == None:
            pipe.kill()

        self.done = True
        self.download_stop_handler(self.data.key)


class AdminServer(threading.Thread):
    def __init__(self, queue):
        super(AdminServer, self).__init__()
        self.queue = queue
        self.stop_flag = False
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % 7766)

    def run(self):
        print 'Running new download server ...'
        while not self.stop_flag:
            req = self.socket.recv_json()
            print 'New Download request ...'
            self.queue.put(req)
            self.socket.send('OK')


class DownloadManager(threading.Thread):
    def __init__(self, queue, pool):
        super(DownloadManager, self).__init__()
        self.queue = queue
        self.pool = pool
        self.stop_flag = False

    def run(self):
        print 'Download Manager Started ...'
        while True:
            if self.stop_flag:
                self.stop_downlods()
                break

            while not self.queue.empty():
                req = self.queue.get()
                dl_info = DownloadInfo(req['link'], req.get('username'), req.get('password'))
                print dl_info
                dl = DownloadThread(dl_info, self.download_stop_handler)
                dl.start()
                self.pool[dl.data.key] = dl

            sleep(2)

    def download_stop_handler(self, key):
        print '**** Download stoped. Going to handle it ...', key
        del self.pool[key]

    def stop_downlods(self):
        pass


class StatusServer(threading.Thread):
    def __init__(self, pool):
        super(StatusServer, self).__init__()
        self.pool = pool
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            print 'ZSS:', self.pool

            sleep(2)


class ZereshkThreadedServer(object):
    queue = Queue()
    pool = dict()

    def __init__(self):
        self.download_manager = DownloadManager(self.queue, self.pool)
        self.status_server = StatusServer(self.pool)
        self.admin_server = AdminServer(self.queue)

    def run(self):
        self.download_manager.start()
        self.admin_server.start()
        self.status_server.start()

        self.download_manager.join()

if __name__ == '__main__':
    zts = ZereshkThreadedServer()
    zts.run()
