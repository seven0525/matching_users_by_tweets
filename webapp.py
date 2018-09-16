# !//usr/bin/env/python

# -*- coding:utf-8 -*-
from flask import Flask, render_template
from os.path import join, dirname, abspath, exists
import matchuser

app = Flask(__name__)

@app.route('/')
def page():
    html = render_template('index.html', a = 'これは変数 a を通じて表示された文章です')
    return html

if __name__ == "__main__":
    app.run(debug=True)