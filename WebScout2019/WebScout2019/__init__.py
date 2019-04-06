"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
import WebScout2019.views

#import Data
#import logging
#import time
#import pickle
#import json
#import os


if __name__ == "__main__":
    print("Welcome to the Highlanders Scouting Application")
    app.run(host='0.0.0.0',threaded=True)


