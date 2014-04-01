import peewee


database = peewee.SqliteDatabase('zereshk.db3')


class DownloadAccount(peewee.Model):
    class Meta:
            database = database

#     pk = peewee.CharField(primary_key=True)
    pk = peewee.PrimaryKeyField()
    name = peewee.CharField()
    username = peewee.CharField()
    password = peewee.CharField()


class Download(peewee.Model):
    class Meta:
            database = database

    pk = peewee.PrimaryKeyField()
    pid = peewee.IntegerField(null=True)
    url = peewee.TextField()
    path = peewee.TextField()
    username = peewee.CharField(null=True)
    password = peewee.CharField(null=True)
    account = peewee.ForeignKeyField(DownloadAccount, related_name='downloads', null=True)
