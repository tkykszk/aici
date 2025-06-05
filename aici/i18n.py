"""
i18n module for aici

This module provides internationalization support for the aici CLI.
"""

import os
import locale
from typing import Dict, Any

# 現在サポートされている言語
SUPPORTED_LANGUAGES = ['en', 'ja']

# デフォルト言語
DEFAULT_LANGUAGE = 'en'

# 言語設定を取得
def get_language() -> str:
    """
    Get the current language setting.
    
    Returns:
        str: Language code ('en', 'ja', etc.)
    """
    # 環境変数から言語設定を取得
    lang = os.environ.get('AICI_LANG')
    
    # 環境変数が設定されていない場合はシステムのロケールを使用
    if not lang:
        try:
            system_locale, _ = locale.getlocale()
            if system_locale:
                lang = system_locale.split('_')[0]
        except (ValueError, AttributeError):
            pass
    
    # サポートされている言語かチェック
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang
    
    return DEFAULT_LANGUAGE

# メッセージ辞書
MESSAGES: Dict[str, Dict[str, str]] = {
    'en': {
        # エラーメッセージ
        'error_api_quota': "Error: API quota limit reached",
        'error_api_connection': "Error: Could not connect to OpenAI server",
        'error_api_status': "Error: An error occurred with the OpenAI API (status code: {status_code})",
        'error_unexpected': "Error: An unexpected problem occurred",
        
        # レート制限メッセージ
        'rate_limit_retry': "Temporary API rate limit reached. Retrying in {sleep_time:.1f} seconds ({retry_count}/{max_retries})...",
        
        # 対処方法メッセージ
        'solutions_header': "Try the following solutions:",
        'solution_check_dashboard': "1. Check your usage on the OpenAI dashboard (https://platform.openai.com/)",
        'solution_check_billing': "2. Ensure your billing information is up to date",
        'solution_upgrade_plan': "3. Consider upgrading your plan if you need higher quotas",
        'solution_contact_support': "4. Contact OpenAI support if the problem persists",
        
        # インターネット接続メッセージ
        'check_internet': "Check your internet connection and try again later.",
        
        # API関連メッセージ
        'api_retry_later': "Try again later. If the problem persists, check your API key.",
        
        # 詳細情報メッセージ
        'verbose_info': "For detailed error information, use the -V or --verbose option.",
        
        # コンフィグファイル関連メッセージ
        'config_not_found': "Configuration file not found. Please create a configuration file in one of the following locations:",
        'config_template_header': "\nConfiguration file template:",
        'config_template_comment': "# OpenAI API Settings",
        'api_key_info': "\nYou can get your OpenAI API key from https://platform.openai.com/api-keys",
        'api_key_env_info': "Alternatively, you can set your API key directly in the OPENAI_API_KEY environment variable.",
        'config_not_found_error': "Configuration file not found. Please refer to the instructions above to set it up.",
        'api_key_not_set': "API key is not set. Please set your API key using one of the following methods:",
        'api_key_config_option': "1. Add OPENAI_API_KEY=your_api_key_here to your configuration file",
        'api_key_env_option': "2. Set the OPENAI_API_KEY environment variable",
        'api_key_not_found': "API key information not found.",
    },
    'ja': {
        # エラーメッセージ
        'error_api_quota': "エラー: APIクォータ制限に達しました",
        'error_api_connection': "エラー: OpenAIサーバーに接続できませんでした",
        'error_api_status': "エラー: OpenAI APIでエラーが発生しました（ステータスコード: {status_code}）",
        'error_unexpected': "エラー: 予期しない問題が発生しました",
        
        # レート制限メッセージ
        'rate_limit_retry': "一時的なAPIレート制限に達しました。{sleep_time:.1f}秒後に再試行します（{retry_count}/{max_retries}）...",
        
        # 対処方法メッセージ
        'solutions_header': "以下の対処方法を試してください:",
        'solution_check_dashboard': "1. OpenAIダッシュボード（https://platform.openai.com/）で使用状況を確認",
        'solution_check_billing': "2. 請求情報が最新であることを確認",
        'solution_upgrade_plan': "3. より高いクォータが必要な場合は、プランのアップグレードを検討",
        'solution_contact_support': "4. 問題が解決しない場合は、OpenAIサポートに連絡",
        
        # インターネット接続メッセージ
        'check_internet': "インターネット接続を確認し、しばらくしてから再度お試しください。",
        
        # API関連メッセージ
        'api_retry_later': "しばらくしてから再度お試しください。問題が続く場合は、APIキーを確認してください。",
        
        # 詳細情報メッセージ
        'verbose_info': "詳細なエラー情報を確認するには、-V または --verbose オプションを使用してください。",
        
        # コンフィグファイル関連メッセージ
        'config_not_found': "コンフィグファイルが見つかりません。以下のいずれかの場所にコンフィグファイルを作成してください：",
        'config_template_header': "\nコンフィグファイルのテンプレート:",
        'config_template_comment': "# OpenAI API設定",
        'api_key_info': "\nOpenAI APIキーは https://platform.openai.com/api-keys から取得できます。",
        'api_key_env_info': "または、環境変数 OPENAI_API_KEY に直接APIキーを設定することもできます。",
        'config_not_found_error': "コンフィグファイルが見つかりません。上記の説明を参考に設定してください。",
        'api_key_not_set': "APIキーが設定されていません。以下のいずれかの方法でAPIキーを設定してください：",
        'api_key_config_option': "1. コンフィグファイルに OPENAI_API_KEY=your_api_key_here を追加",
        'api_key_env_option': "2. 環境変数 OPENAI_API_KEY にAPIキーを設定",
        'api_key_not_found': "APIキー情報が見つかりません。",
    }
}

def get_message(key: str, **kwargs: Any) -> str:
    """
    Get a localized message.
    
    Args:
        key (str): Message key
        **kwargs: Format parameters for the message
        
    Returns:
        str: Localized message
    """
    lang = get_language()
    
    # 指定された言語のメッセージを取得
    messages = MESSAGES.get(lang, MESSAGES[DEFAULT_LANGUAGE])
    
    # キーが存在しない場合はデフォルト言語から取得
    message = messages.get(key)
    if message is None and lang != DEFAULT_LANGUAGE:
        message = MESSAGES[DEFAULT_LANGUAGE].get(key, f"Missing message: {key}")
    elif message is None:
        message = f"Missing message: {key}"
    
    # フォーマットパラメータがある場合は適用
    if kwargs:
        try:
            message = message.format(**kwargs)
        except KeyError:
            pass
    
    return message
