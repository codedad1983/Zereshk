import zmq
import threading
from time import sleep
import config
from models import Download
from subprocess import Popen, PIPE


class DownloadThread(threading.Thread):
    def __init__(self, dl, download_stop_handler):
        super(DownloadThread, self).__init__()
        self.data = dl
        self.stop_flag = False
        self.done = False
        self._status = {'ip': '0.0.0.0',
                        'total_size': "0K",
                        'target': '',
                        'percent': "0%",
                        'speed': "0K/s",
                        'time_left': "",
                        'downloaded_size': "0K",
                        'error': ()}

        self.download_stop_handler = download_stop_handler

    def wget_command(self, resume=True):
        wget_opts = ['wget']
        if resume:
            wget_opts += ['-c']
        cmd = wget_opts + ['-P%s' % config.PATH_WORK, self.data.link]
        return cmd

    def run(self):
        print 'Starting download'
        pipe = Popen(self.wget_command(resume=False), stdout=PIPE, stderr=PIPE)

        pipe_out = pipe.stderr

        while (pipe.poll() is None) and (self.stop_flag is False):
            # TODO: check how much this loop execute and if it needed increase sleep time
            # print self.data.key, 'Going to read new data from WGET output'
            self.status.process(pipe_out.readline().strip())
            # print self.data.key, 'WGET output processed. sleeping ...'
            sleep(0.01)

        # TODO: handle this
        # wget print some errors and outputs by stdout
        std_out = pipe.stdout.readline()

        if pipe.returncode is None:
            pipe.kill()

        self.done = True
        self.download_stop_handler(self.data.key)

    def process_status(self, s):
        if not s:
            return

        line = s.split(' ')
#         print 'WGET:', s
        if line[1] == '..........':
            self._status['downloaded_size'] = line[0]
            self._status['percent'] = line[6]
            self._status['speed'] = line[7]
            self._status['time_left'] = line[8]
        elif line[0] == 'Resolving':
            self._status['ip'] = line[-1]
        elif line[0] == 'Length:':
            self._status['total_size'] = line[1]
        elif line[0] == 'Saving':
            self._status['target'] = line[-1][:-1]
        elif (s.find('416 Requested Range Not Satisfiable')):
            self._status['error'] = ('416_1', 'Requested Range Not Satisfiable')


class AdminServer(threading.Thread):
    """
    Main way to communicate with user interface and get commands
    """

    def __init__(self):
        super(AdminServer, self).__init__()
        self.stop_flag = False
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % 7766)

    def run(self):
        print 'Running new download server ...'
        while not self.stop_flag:
            req = self.socket.recv_json()
            print 'New Download request ...'
            # TODO: handle commands
#             self.queue.put(req)
            self.socket.send('OK')


class DownloadManager(threading.Thread):
    def __init__(self):
        super(DownloadManager, self).__init__()
        self.pool = dict()
        self.stop_flag = False

    def run(self):
        print 'Download Manager Started ...'
        while True:
            if self.stop_flag:
                self.stop_downlods()
                break

            while not self.queue.empty():
                req = self.queue.get()
                dl = Download()
                dl.link = req['link']
                dl.username = req.get('username')
                dl.password = req.get('password')
                dl.save(force_insert=True)
                print dl
                if len(self.pool) < config.MAX_JOBS:
                    self.start_new_download(dl)

            sleep(2)

    def start_new_download(self, dl_info):
        dl = DownloadThread(dl_info, self.download_stop_handler)
        dl.start()
        dl_info.status = 'running'
        dl_info.save()
        self.pool[dl.data.key] = dl

    def download_stop_handler(self, key):
        print '**** Download stopped. Going to handle it ...', key
        try:
            dl_info = Download.get(Download.key == key)
            dl_info.status = 'Finished'
            dl_info.save()
        except:
            print 'Problem in updating download info'
        del self.pool[key]

    def stop_downlods(self):
        pass
