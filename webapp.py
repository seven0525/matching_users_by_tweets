# !//usr/bin/env/python

# -*- coding:utf-8 -*-
from flask import Flask, render_template, redirect, request
from os.path import join, dirname, abspath, exists
import matchuser

app = Flask(__name__)

@app.route('/')
def show_toppage():
    return render_template('index.html')

@app.route('/adduser', methods=['POST'])
def add_user():
    user_name = request.form['user_name']
    target_name = request.form['target_name']
    if not user_name:
        return redirect('/')

    matchuser.users.append(user_name)
    matchuser.users.append(target_name)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)