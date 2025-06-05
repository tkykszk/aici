"""
aici  CLI for AI

This module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

Functions:
    def query_chatgpt(prompt:str, complete:bool=False, model:str=DEFAULT_MODEL, 
                  system:str=DEFAULT_SYSTEM, output=sys.stdout) -> None:

    def main() -> None:

Examples:
    >>> sys.argv = ['/path/to/aici', 'Hello']
    >>> aici.main()
    Hello! How can I assist you today

"""

import os
import io
import sys
import argparse
import openai
from openai import OpenAI
import pyperclip
import logging
from . import __version__

# デフォルトの設定
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_SYSTEM = "You are a helpful assistant."

# ログ設定 - デフォルトはINFOレベル
logger = logging.getLogger("aici")

# ログファイルのパスを設定ファイルと同じ場所に設定
def setup_logging():
    from . import ENV_FILE, CONFIG_LOADED
    
    # デフォルトのログファイルパス
    log_dir = os.path.expanduser("~/.config/aici")
    log_file = os.path.join(log_dir, "aici.log")
    
    # 設定ファイルが読み込まれている場合は、そのディレクトリにログファイルを作成
    if CONFIG_LOADED and ENV_FILE:
        config_dir = os.path.dirname(ENV_FILE)
        if os.path.isdir(config_dir):
            log_file = os.path.join(config_dir, "aici.log")
    
    # ログディレクトリが存在しない場合は作成を試みる
    log_dir = os.path.dirname(log_file)
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # ログファイルハンドラーを設定
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
        
    except (IOError, PermissionError) as e:
        # ログファイルに書き込めない場合は警告を出して続行
        print(f"Warning: Could not create log file at {log_file}. Logging to file is disabled.")
        print(f"Error: {str(e)}")
    
    # コンソールハンドラーを設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # デフォルトは警告以上のみ表示
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(console_handler)
    
    # ロガーのレベルを設定
    logger.setLevel(logging.INFO)

# Check if we're in test mode
is_test_mode = os.environ.get('AICI_TEST_MODE', 'false').lower() == 'true'

# デフォルトモデルを環境変数から取得することも可能
DEFAULT_OPENAI_MODEL = os.getenv("AICI_OPENAI_MODEL", DEFAULT_MODEL)
DEFAULT_DEEPSEEK_MODEL = os.getenv("AICI_DEEPSEEK_MODEL", "deepseek-chat")

# モデル名に基づいてAPIプロバイダーを選択する関数
def select_api_provider(model_name):
    """モデル名に基づいて適切なAPIキーとベースURLを返す"""
    if model_name.startswith("deepseek"):
        # DeepSeekモデルの場合
        provider_api_key = os.getenv("AICI_DEEPSEEK_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if not provider_api_key:
            raise RuntimeError("モデル名がdeepseekで始まる場合、AICI_DEEPSEEK_KEYまたはDEEPSEEK_API_KEYが必要です")
        return provider_api_key, "https://api.deepseek.com"
    else:
        # それ以外はデフォルトでOpenAIとして扱う
        provider_api_key = os.getenv("AICI_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
        if not provider_api_key:
            raise RuntimeError("モデル名がdeepseekで始まらない場合、AICI_OPENAI_KEYまたはOPENAI_API_KEYが必要です")
        return provider_api_key, "https://api.openai.com/v1"

# 初期化時はクライアントをNoneに設定し、必要に応じて作成する
client = None

if is_test_mode:
    from .mock_api import mock_create

# 環境変数からシステムメッセージを取得
DEFAULT_SYSTEM = os.getenv("AICI_SYSTEM", DEFAULT_SYSTEM)

# システムメッセージをファイルから読み込む関数
def read_system_from_file(file_path):
    """ファイルからシステムメッセージを読み込む"""
    try:
        with open(os.path.expanduser(file_path), 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.error("システムメッセージファイルの読み込みエラー: %s", e)
        return None

# 環境変数からシステムメッセージファイルを取得
system_file = os.getenv("AICI_SYSTEM_FILE")
if system_file:
    file_content = read_system_from_file(system_file)
    if file_content:
        DEFAULT_SYSTEM = file_content


def query_deepseek(
    prompt: str,
    complete: bool = False,
    model: str = DEFAULT_MODEL,
    system: str = DEFAULT_SYSTEM,
    output=sys.stdout,
) -> str:
    """Sends a prompt to the AI API and handles the response, either streaming or complete.
    
    Args:
        prompt (str): The prompt to send to the API.
        complete (bool, optional): Whether to return the complete response or stream it. Defaults to False.
        model (str, optional): The model to use. Defaults to DEFAULT_MODEL.
        system (str, optional): The system message to use. Defaults to DEFAULT_SYSTEM.
        output (optional): Where to write the output. Defaults to sys.stdout.
        
    Returns:
        str: The complete response if complete=True, otherwise an empty string.

    Raises:
        openai.APIConnectionError: If the server could not be reached.
        openai.RateLimitError: If the API rate limit is exceeded (429 status code).
        openai.APIStatusError: If any other non-200-range status code is received.
    """
    # モデル名に基づいてAPIプロバイダーを選択
    global client
    provider_api_key, provider_base_url = select_api_provider(model)
    
    # 新しいクライアントを作成
    client = OpenAI(
        api_key=provider_api_key,
        base_url=provider_base_url
    )
    
    logger.debug("選択されたAPIプロバイダー: %s", provider_base_url)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    try:
        # Use mock API in test mode
        if is_test_mode:
            if complete:
                # For complete response in test mode
                response = mock_create(
                    model=model,
                    messages=messages,
                    stream=False
                )
                response_content = "Mocked DeepSeek Response"
                print(response_content, flush=True, file=output)
                return response_content
            else:
                # For streaming response in test mode
                collected_response = "Mocked DeepSeek Response"
                print(collected_response, flush=True, file=output)
                return collected_response
        else:
            if not complete:
                # Streaming response from DeepSeek API
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,  # Enable streaming mode
                )

                # Collecting and printing the streamed response
                collected_response = ""
                for chunk in stream:
                    chunk_message = chunk.choices[0].delta.content or ""
                    print(chunk_message, end="", flush=True, file=output)
                    collected_response += chunk_message

                print()  # Print a newline at the end
                return collected_response
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=False,  # Explicitly disable streaming for complete mode
                )
                # Print a newline at the end
                response_content = response.choices[0].message.content
                print(response_content, flush=True, file=output)
                return response_content

    except openai.APIConnectionError as e:
        logger.error("The server could not be reached", exc_info=e)
        # ログにはエラーの詳細を残すが、ユーザーには簡潔なメッセージを表示
        return "Error: Could not connect to the server. Please check your internet connection."
    except openai.RateLimitError as e:
        logger.error(
            "A 429 status code was received; we should back off a bit.", exc_info=e
        )
        return "Error: API rate limit exceeded. Please wait a moment and try again."
    except openai.NotFoundError as e:
        logger.error("404 Not Found error occurred", exc_info=e)
        # 404エラーの場合はモデル名に関するエラーメッセージを表示
        error_message = str(e)
        if "model" in error_message.lower() and "not exist" in error_message.lower():
            # 利用可能なモデルの例を表示
            openai_examples = "gpt-3.5-turbo, gpt-4, gpt-4o"
            deepseek_examples = "deepseek-chat"
            
            if model.startswith("deepseek"):
                return f"Error: Model '{model}' does not exist or you do not have access to it.\nAvailable DeepSeek models: {deepseek_examples}"
            elif model.startswith("gpt") or model.startswith("chatgpt"):
                return f"Error: Model '{model}' does not exist or you do not have access to it.\nAvailable OpenAI models: {openai_examples}"
            else:
                return f"Error: Model '{model}' does not exist or you do not have access to it.\nAvailable models:\n- OpenAI: {openai_examples}\n- DeepSeek: {deepseek_examples}"
        else:
            return "Error: API endpoint not found. Please check if the API version or URL is correct."
    except openai.APIStatusError as e:
        logger.error("Non-200-range status code was received", exc_info=e)
        # ステータスコードに応じたメッセージ
        if hasattr(e, 'status_code'):
            if e.status_code == 401:
                return "Error: Authentication failed. Please check if your API key is correct."
            elif e.status_code == 403:
                return "Error: Access denied. Please check the permissions of your API key."
            else:
                return f"Error: The API server returned an error (status code: {e.status_code})."
        else:
            return "Error: The API server returned an error."


def main() -> None:
    """Main function for the CLI"""
    # ログ設定を初期化
    setup_logging()
    
    try:
        parser = argparse.ArgumentParser(
            description="AICI - AI Chat Interface: OpenAI/DeepSeekモデルを簡単に利用するコマンドラインツール",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""例:
  aici "日本の首都はどこですか"                  # 基本的な使い方
  aici -m gpt-4o "日本の首都はどこですか"        # モデルを指定
  aici -S system.txt "日本の首都はどこですか"   # システムメッセージファイルを指定
  aici -o clip "日本の首都はどこですか"        # 結果をクリップボードにコピー
  echo "日本の首都はどこですか" | aici -       # 標準入力から読み込み
"""
        )
        parser.add_argument(
            "prompt",
            type=str,
            nargs="?",
            default=argparse.SUPPRESS,
            help='AIに送るプロンプト。"-"を指定すると標準入力から読み込みます',
        )
        parser.add_argument(
            "-v", "--version", action="store_true", help="バージョンを表示して終了"
        )
        # モデル名はコマンドライン引数か環境変数から取得
        default_model = DEFAULT_MODEL
        if os.getenv("AICI_MODEL"):
            default_model = os.getenv("AICI_MODEL")
        elif os.getenv("AICI_OPENAI_MODEL") and not os.getenv("AICI_DEEPSEEK_MODEL"):
            default_model = os.getenv("AICI_OPENAI_MODEL")
        elif os.getenv("AICI_DEEPSEEK_MODEL") and not os.getenv("AICI_OPENAI_MODEL"):
            default_model = os.getenv("AICI_DEEPSEEK_MODEL")
            
        parser.add_argument(
            "-m", "--model", 
            default=default_model, 
            help="使用するモデル名 (gpt-3.5-turbo, gpt-4, gpt-4o, deepseek-chat など)"
        )
        parser.add_argument(
            "-c",
            "--complete",
            default=False,
            action="store_true",
            help="ストリーミングせずに完全な応答を一度に取得",
        )
        parser.add_argument(
            "-s", "--system", default=DEFAULT_SYSTEM, help="システムメッセージを指定"
        )
        parser.add_argument(
            "-S", "--system-file", 
            help="システムメッセージを含むファイルを指定"
        )
        parser.add_argument(
            "-V", "--verbose", "--VERBOSE", 
            dest="verbose",
            action="store_true", 
            help="詳細なデバッグ情報を表示"
        )
        parser.add_argument(
            "-o",
            "--output",
            help='出力先を指定。"clip"でクリップボードにコピー',
            default=sys.stdout,
        )
        args = parser.parse_args()

        if args.version:
            print(__version__)
            sys.exit(0)
            
        # デバッグモードの設定
        if args.verbose:
            # ログレベルをDEBUGに設定
            logger.setLevel(logging.DEBUG)
            
            # すべてのハンドラーのレベルをDEBUGに設定
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.DEBUG)
            
            logger.debug("Debug mode enabled")
            logger.debug("Model: %s", args.model)
            
            # 設定ファイルの読み込み状況を表示
            from . import ENV_FILE, CONFIG_LOADED
            if CONFIG_LOADED:
                logger.debug("Config file loaded from: %s", ENV_FILE)
            else:
                logger.debug("No config file loaded. Using environment variables.")
            
            # 利用可能なAPIキーの確認
            openai_key = os.getenv("AICI_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
            deepseek_key = os.getenv("AICI_DEEPSEEK_KEY") or os.getenv("DEEPSEEK_API_KEY")
            
            if openai_key:
                logger.debug("OpenAI APIキー: %s%s", openai_key[:4], '*' * 8)
            else:
                logger.debug("OpenAI APIキー: 設定されていません")
                
            if deepseek_key:
                logger.debug("DeepSeek APIキー: %s%s", deepseek_key[:4], '*' * 8)
            else:
                logger.debug("DeepSeek APIキー: 設定されていません")
                
            # 環境変数のモデル設定を確認
            aici_model = os.getenv("AICI_MODEL")
            aici_openai_model = os.getenv("AICI_OPENAI_MODEL")
            aici_deepseek_model = os.getenv("AICI_DEEPSEEK_MODEL")
            
            if aici_model:
                logger.debug("AICI_MODEL: %s", aici_model)
            if aici_openai_model:
                logger.debug("AICI_OPENAI_MODEL: %s", aici_openai_model)
            if aici_deepseek_model:
                logger.debug("AICI_DEEPSEEK_MODEL: %s", aici_deepseek_model)
            
            # モデル名に基づいて使用されるAPIプロバイダーを表示
            try:
                selected_api_key, selected_base_url = select_api_provider(args.model)
                logger.debug("選択されるAPIキー: %s%s", selected_api_key[:4], '*' * 8)
                logger.debug("選択されるベースURL: %s", selected_base_url)
            except Exception as e:
                logger.debug("モデル選択エラー: %s", e)

        # システムファイルが指定されていれば読み込む
        if args.system_file:
            file_content = read_system_from_file(args.system_file)
            if file_content:
                args.system = file_content
            else:
                print(f"Error: Could not read system message from file: {args.system_file}", file=sys.stderr)
                sys.exit(1)

        # Check if 'prompt' exists and is not None
        if getattr(args, "prompt", None) is None or args.prompt is None:
            parser.error("the following arguments are required: prompt")

        # Check if the prompt is "-" and read from stdin if so
        if args.prompt == "-":
            prompt = sys.stdin.read().strip()
        else:
            prompt = args.prompt

        if args.output == "clip" or args.output == "clipboard":
            buffer = io.StringIO()
        else:
            buffer = sys.stdout

        # デバッグ情報の記録
        if args.verbose:
            prompt_preview = prompt[:50] + ('...' if len(prompt) > 50 else '')
            system_preview = args.system[:50] + ('...' if len(args.system) > 50 else '')
            logger.debug("プロンプト: %s", prompt_preview)
            logger.debug("システムメッセージ: %s", system_preview)
            
        response = query_deepseek(
            prompt,
            model=args.model,
            complete=args.complete,
            system=args.system,
            output=buffer,
        )
        
        # エラーメッセージが返された場合は表示する
        if response and response.startswith("Error:"):
            print(response, file=sys.stderr)
            sys.exit(1)

        if args.output == "clip" or args.output == "clipboard":
            pyperclip.copy(buffer.getvalue() if hasattr(buffer, 'getvalue') else str(buffer))

    except Exception as e:
        logger.error("Error", exc_info=e)
        # スタックトレースを表示せず、ユーザーフレンドリーなエラーメッセージを表示
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
