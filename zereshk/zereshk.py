# -*- coding: utf-8 -*-
"""
    Zereshk
    ~~~~~~~~~~~~~~

    Web based download manager

    :copyright: (c) 2014 by Mehdi Bayazee.
    :license: BSD, see LICENSE for more details.
"""

from flask import Flask, render_template, request, redirect, url_for, g
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
    return 'OK'


@app.route('/account/new/', methods=['POST', 'GET'])
def new_account():
    if request.method == 'POST':
        name = request.form.get('account_name')
        username = request.form.get('username')
        password = request.form.get('password')
        DownloadAccount(name=name, username=username, password=password).save()
        return redirect(url_for('index'))
    return render_template('new_account.html')


@app.route('/download/new/', methods=['POST', 'GET'])
def new_download():
    if request.method == 'POST':
        dl_url = request.form.get('dl_url')
        path = request.form.get('path')
        username = request.form.get('username')
        password = request.form.get('password')
        dl = Download(url=dl_url, path=path)
        dl.save()
        return redirect(url_for('index'))
    return render_template('new_download.html', dl_accounts=DownloadAccount.select())


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0')
