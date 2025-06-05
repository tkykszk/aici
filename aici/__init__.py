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
from .i18n import get_message

env_candidates = []
if platform.system() == "Windows":  # Windows specific
    env_candidates.extend(
        [
            os.path.expanduser("~/Appdata/Local/aici/config"),  # 1st priority
            os.path.expanduser("~/Appdata/Roaming/aici/config"),
        ]
    )  # 2nd priority
elif platform.system() == "Linux":  # Linux specific
    env_candidates.extend(
        [
            os.path.expanduser("~/.config/aici/config"),  # 1st priority
            os.path.expanduser("/etc/aici/config"),       # 2nd priority (system-wide)
            os.path.expanduser("~/.local/share/aici/config"),  # 3rd priority
        ]
    )
else:  # macOS and others
    env_candidates.extend(
        [
            os.path.expanduser("~/.config/aici/config"),  # 1st priority
            os.path.expanduser("~/.aici"),               # 2nd priority
        ]
    )

API_KEY = None
_API_KEY = os.environ.get("OPENAI_API_KEY")  # preserve value before reading config file

ary = []
for fn in env_candidates:
    if os.path.exists(fn):
        ary.append(fn)

# check must env values are set or config file exists
if _API_KEY is None:
    if len(ary) == 0:
        # コンフィグファイルが見つからない場合、説明とテンプレートを表示
        print(get_message('config_not_found'))
        for path in env_candidates:
            print(f"  - {path}")
        
        print(get_message('config_template_header'))
        print("----------------------------------")
        print(get_message('config_template_comment'))
        print("OPENAI_API_KEY=your_api_key_here")
        print("OPENAI_CHATGPT_MODEL=gpt-4o")
        print("OPENAI_CHATGPT_SYSTEM=You are a helpful assistant.")
        print("OPENAI_MAX_RETRIES=3")
        print("OPENAI_INITIAL_RETRY_DELAY=1.0")
        print("OPENAI_MAX_RETRY_DELAY=60.0")
        print("----------------------------------")
        print(get_message('api_key_info'))
        print(get_message('api_key_env_info'))
        
        raise RuntimeError(get_message('config_not_found_error'))

if len(ary) > 0:
    ENV_FILE = ary[0]
    load_dotenv(ENV_FILE)
    API_KEY = os.environ.get("OPENAI_API_KEY")  # env value is prior to config file

if API_KEY is None and _API_KEY is None:  # not specified in env file
    print(get_message('api_key_not_set'))
    print(get_message('api_key_config_option'))
    print(get_message('api_key_env_option'))
    print(get_message('api_key_info'))
    raise RuntimeError(get_message('api_key_not_found'))

if API_KEY is None:
    API_KEY = _API_KEY

from .main import main
