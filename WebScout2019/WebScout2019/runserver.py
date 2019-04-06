"""
This script runs the WebScout2019 application using a development server.
"""

from os import environ
from WebScout2019 import app

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True)
