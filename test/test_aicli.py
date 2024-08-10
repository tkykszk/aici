import os
import sys
import pytest
import aicli

class TestAicli:

    def test_keysetting(self):
        assert os.getenv('OPENAI_API_KEY') is not None, "OPENAI_API_KEY is not set"

    def test_query(self, monkeypatch):
        # sys.argv を一時的に ['script_name', 'Hello'] に設定
        test_args = ['Hello']
        monkeypatch.setattr(sys, 'argv', test_args)

        try:
            # ここで aicli 関数やメソッドを呼び出すことを想定
            pass
        except Exception as e:
            pytest.fail(f"command error: {e}")
            
