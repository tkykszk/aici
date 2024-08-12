"""
aici  CLI for AI

This module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

"""
import os
import sys
from .version import __version__
from dotenv import load_dotenv

env_candidates = [os.path.expanduser('~/.config/aici/config'),]

ary = []
for fn in env_candidates:
    if os.path.exists(fn):
        ary.append(fn)

if len(ary) == 0:
    raise RuntimeError("env file not existing")

# read .env file
ENV_FILE = ary[0]

load_dotenv(ENV_FILE)

API_KEY = os.environ.get('OPENAI_API_KEY')
if API_KEY == None:
    raise RuntimeError("API KEY info not found")

from .main import main



