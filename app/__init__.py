from flask import Flask
import sys
import json

app = Flask(__name__)
CONF = json.load(open('conf.json', 'r+'))
app.secret_key = CONF['secret_key']

from app import routes