"""
This script runs the WebScout2019 application using a development server.
"""

from os import environ
from WebScout2019 import app

if __name__ == '__main__':
    #HOST = environ.get('SERVER_HOST', 'localhost')
    #HOST = "192.168.137.1"
    try:
        PORT = 5800 #int(environ.get('SERVER_PORT', '5800'))
    except ValueError:
        PORT = 5800
    #app.run(HOST, PORT)
    app.run(host='0.0.0.0',port=5800)
