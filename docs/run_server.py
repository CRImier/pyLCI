#!/usr/bin/env python

import os
import sys

os.chdir('_build/html')

if os.fork():
    sys.exit()

import SimpleHTTPServer
SimpleHTTPServer.test()

