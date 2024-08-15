"""
aici  CLI for AI

This module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

test 
    env only 
    env and configuration file
    configuration file only

"""
import os
import sys
from .version import __version__
from dotenv import load_dotenv
import platform

env_candidates = []
if platform.system() == 'Windows': # Windows specific
    env_candidates.extend([
        os.path.expanduser('~/Appdata/Local/aici/config'), # 1st priority
        os.path.expanduser('~/Appdata/Roaming/aici/config')
    ]) # 2nd priority
env_candidates.extend([
            os.path.expanduser('~/.config/aici/config'), # 1st priority
            os.path.expanduser('~/.aici')]) # 2nd priority

API_KEY = None
_API_KEY = os.environ.get('OPENAI_API_KEY') # preserve value before reading config file

ary = []
for fn in env_candidates:
    if os.path.exists(fn):
        ary.append(fn)

# check must env values are set or config file exists
if _API_KEY is None:
    if len(ary) == 0:
        raise RuntimeError(f"Env file not existing {env_candidates}")

if len(ary) > 0:
    ENV_FILE = ary[0]
    load_dotenv(ENV_FILE)
    API_KEY = os.environ.get('OPENAI_API_KEY')  # env value is prior to config file

if API_KEY is None and _API_KEY is None: # not specified in env file
    raise RuntimeError("API KEY info not found")

if API_KEY is None:
    API_KEY = _API_KEY

from .main import main



