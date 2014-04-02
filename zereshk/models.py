import os
import peewee
from config import LOG_PATH

database = peewee.SqliteDatabase('zereshk.db3')


class DownloadAccount(peewee.Model):
    class Meta:
            database = database

#     pk = peewee.CharField(primary_key=True)
    pk = peewee.PrimaryKeyField()
    name = peewee.CharField()
    username = peewee.CharField()
    password = peewee.CharField()

STATUS_TYPES = (('created', 'Created'),
                ('running', 'Running'),
                ('waiting', 'Waiting'),
                ('finished', 'Finished'),
                ('paused', 'Paused'),
                ('failed', 'Failed'))


class Download(peewee.Model):
    wget_cmd = ["wget", "-nd", "-np", "-c", "-r"]

    class Meta:
            database = database

    pk = peewee.PrimaryKeyField()
    status = peewee.CharField(max_length=25, choices=STATUS_TYPES, default='created')
    pid = peewee.IntegerField(null=True)
    url = peewee.TextField()
    path = peewee.TextField()
    username = peewee.CharField(null=True)
    password = peewee.CharField(null=True)
    account = peewee.ForeignKeyField(DownloadAccount, related_name='downloads', null=True)

    @property
    def name(self):
        return self.path

    @property
    def log_path(self):
        return os.path.join(LOG_PATH, '%s.log' % self.pk)

    def start(self):
        if self.status in ('running', 'finished'):
            return

        cmd = self.wget_cmd + ['-o%s' % self.log_path, self.url]
        print cmd
        pid = None
        try:
            pid = os.spawnlp(os.P_NOWAIT, 'wget', *cmd)
        except Exception, inst:
            print "'%s': %s" % ("\x20".join(cmd), str(inst))
        else:
            self.pid = pid
            self.save()
            print 'New download started. PK: %d, PID: %d, name: %s' % (self.pk, self.pid, self.name)
        return pid
