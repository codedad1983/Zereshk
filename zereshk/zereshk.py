# -*- coding: utf-8 -*-
"""
    Zereshk
    ~~~~~~~~~~~~~~

    Web based download manager

    :copyright: (c) 2014 by Mehdi Bayazee.
    :license: BSD, see LICENSE for more details.
"""

from flask import Flask, render_template, request, redirect, url_for, g, flash
from models import database, Download, DownloadAccount

app = Flask(__name__)
app.config.from_object('config')


class DownloadManager(object):
    def new_download(self, url, path, user=None, password=None):
        pass


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/create-db/')
def create_database():
    Download.create_table()
    DownloadAccount.create_table()
    return redirect('/')


@app.route('/account/new/', methods=['POST', 'GET'])
def new_account():
    if request.method == 'POST':
        name = request.form.get('account_name')
        username = request.form.get('username')
        password = request.form.get('password')
        DownloadAccount(name=name, username=username, password=password).save()
        flash('New account created successfully.', 'alert-success')
        return redirect(url_for('index'))
    return render_template('new_account.html')


@app.route('/download/new/', methods=['POST', 'GET'])
def new_download():
    if request.method == 'POST':
        dl_url = request.form.get('dl_url').strip()
        path = request.form.get('path').strip()
        username = request.form.get('username')
        password = request.form.get('password')
        dl_account = request.form.get('dl_account')

        dl = Download(url=dl_url, path=path)
        if username:
            dl.username = username
        if password:
            dl.password = password

        if dl_account != 'None':
            dl.account = DownloadAccount.select().where(DownloadAccount.pk==int(dl_account))[0]

        dl.save()
        flash('New download added successfully.', 'alert-success')
        return redirect(url_for('index'))
    return render_template('new_download.html', dl_accounts=DownloadAccount.select())


@app.route('/')
def index():
    dl = Download.select()[0]
    dl.start()
    return render_template('index.html', downloads=Download.select())


if __name__ == '__main__':
    app.run('0.0.0.0')
