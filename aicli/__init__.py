import os
import sys

from dotenv import load_dotenv

env_candidates = [os.path.expanduser('~/.aicli'),]

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




