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
_API_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('DEEPSEEK_API_KEY') # preserve value before reading config file

ary = []
for fn in env_candidates:
    if os.path.exists(fn):
        ary.append(fn)

# 設定ファイルが見つからない場合でも、APIキーが環境変数から取得できればOK
if _API_KEY is None and len(ary) == 0:
    # 設定ファイルが見つからず、環境変数にもAPIキーがない場合は警告を表示
    print("Warning: No configuration file found. Please set AICI_OPENAI_KEY or AICI_DEEPSEEK_KEY environment variable.")
    print("You can also create a config file in one of these locations:")
    for path in env_candidates:
        print(f"  - {path}")
    print("\nFor more information, see: https://github.com/tkykszk/aici#-config-environment-variables-or-file")

# 設定ファイルの読み込み状況を記録するグローバル変数
ENV_FILE = None
CONFIG_LOADED = False

if len(ary) > 0:
    ENV_FILE = ary[0]
    load_dotenv(ENV_FILE)
    CONFIG_LOADED = True
    API_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')  # env value is prior to config file

if API_KEY is None and _API_KEY is None: # not specified in env file or environment variables
    print("Error: API key not found. Please set one of the following environment variables:")
    print("  - AICI_OPENAI_KEY or OPENAI_API_KEY for OpenAI models")
    print("  - AICI_DEEPSEEK_KEY or DEEPSEEK_API_KEY for DeepSeek models")
    print("\nOr create a config file with these keys in one of these locations:")
    for path in env_candidates:
        print(f"  - {path}")
    print("\nFor more information, see: https://github.com/tkykszk/aici#-config-environment-variables-or-file")
    sys.exit(1)

if API_KEY is None:
    API_KEY = _API_KEY

from .main import main



