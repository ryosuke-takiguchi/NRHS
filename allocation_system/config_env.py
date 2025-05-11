import os
from dotenv import load_dotenv

class EnvConfig:
    def __init__(self, dotenv_path="allocation_system\env\.env"):
        """
        .env ファイルを読み込み、環境変数として取得できるようにする。
        """
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        else:
            print(f".env ファイルが見つかりません: {dotenv_path}")


    def get(self, key, fallback=None):
        """
        環境変数を文字列として取得。存在しなければ fallback を返す。
        """
        return os.getenv(key.upper(), fallback)

    def getint(self, key, fallback=None):
        """
        環境変数を整数として取得。
        """
        value = self.get(key, fallback)
        return int(value) if value is not None else fallback

    def getfloat(self, key, fallback=None):
        """
        環境変数を浮動小数点として取得。
        """
        value = self.get(key, fallback)
        return float(value) if value is not None else fallback

    def getboolean(self, key, fallback=False):
        """
        環境変数を真偽値として取得。'1', 'true', 'yes', 'on' を True として扱う。
        """
        value = self.get(key, fallback)
        if value is not None:
            return str(value).lower() in ("1", "true", "yes", "on")
        return fallback
