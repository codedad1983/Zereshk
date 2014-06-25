import os
import config
from uuid import uuid4
import peewee

database = peewee.SqliteDatabase('zereshk.db3')


# class DownloadAccount(peewee.Model):
#     class Meta:
#             database = database
#
# #     pk = peewee.CharField(primary_key=True)
#     pk = peewee.PrimaryKeyField()
#     name = peewee.CharField()
#     username = peewee.CharField()
#     password = peewee.CharField()

STATUS_TYPES = (('running', 'Running'),
                ('waiting', 'Waiting'),
                ('finished', 'Finished'),
                ('paused', 'Paused'),
                ('failed', 'Failed'))


class Download(peewee.Model):
    class Meta:
            database = database

    key = peewee.CharField(primary_key=True, default=str(uuid4()))
    status = peewee.CharField(max_length=25, choices=STATUS_TYPES, default='waiting')
    link = peewee.TextField()
    username = peewee.CharField(null=True)
    password = peewee.CharField(null=True)

    @property
    def name(self):
        return self.link

    @property
    def log_path(self):
        return os.path.join(config.PATH_LOG, '%s.log' % self.key)
