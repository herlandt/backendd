import os
import sys
from config.wsgi import application

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'