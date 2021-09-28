#! /usr/bin/python3

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/ubuntu/spiders/bcpzonasegurabeta')
from bcpzonasegurabeta import app as application
application.secret_key = 'myverysecretkey'