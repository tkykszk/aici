""" All tests need appropriate API-KEY for the OpenAI API.

"""

import os
import sys
import io
import pytest
import aici
import pyperclip



class Testaici:

    def test_keysetting(self):
        assert os.getenv('OPENAI_API_KEY') is not None, "OPENAI_API_KEY is not set"

    def test_query(self, monkeypatch):
        # REAL CALL to API
        # sys.argv を一時的に ['script_name', 'Hello'] に設定
        test_args = ['aici', 'Hello']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
            pass
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_option_complete(self, monkeypatch):
        # REAL CALL to API
        test_args = ['aici', 'Hello', '--complete']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
            pass
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_option_clipboard(self, monkeypatch):
        # REAL CALL to API
        test_args = ['aici', 'Hello', '--output=clip']
        monkeypatch.setattr(sys, 'argv', test_args)
        try:
            aici.main()
            pass
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
    def test_option_ai_out(self, monkeypatch):
        # REAL CALL to API
        # clipboard output
        test_args = ['aici', 'Hello', '--output=clip', '--system="すべてローマ字で答える"']
        monkeypatch.setattr(sys, 'argv', test_args)

        # sys.stdout をモックするために StringIO オブジェクトを使用
        mock_stdout = io.StringIO()
        monkeypatch.setattr(sys, 'stdout', mock_stdout)

        try:
            aici.main()
            clipboard_output = pyperclip.paste()

            assert all(ord(char) < 128 for char in clipboard_output), \
                f"Output contains non-ASCII characters: CONTENT:<<{clipboard_output}>>"

        except Exception as e:
            pytest.fail(f"command error: {e}")
            
