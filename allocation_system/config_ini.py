import configparser
import os

class IniConfig:
    def __init__(self, ini_path="allocation_system/config/config.ini"):
        """
        INIファイルから設定を読み込むクラス。
        指定されたパスにファイルが存在すれば読み込む。
        """
        self.config = configparser.ConfigParser()
        self.ini_loaded = False

        if os.path.exists(ini_path):
            self.config.read(ini_path, encoding="utf-8")
            self.ini_loaded = True

    def get(self, section, key, fallback=None):
        """
        値を文字列として取得。存在しなければfallbackを返す。
        """
        if self.ini_loaded and self.config.has_section(section):
            if self.config.has_option(section, key):
                return self.config.get(section, key)
        return fallback

    def getint(self, section, key, fallback=None):
        """
        値をintとして取得。変換できない場合はfallback。
        """
        value = self.get(section, key, fallback)
        return int(value) if value is not None else fallback

    def getfloat(self, section, key, fallback=None):
        """
        値をfloatとして取得。変換できない場合はfallback。
        """
        value = self.get(section, key, fallback)
        return float(value) if value is not None else fallback

    def getboolean(self, section, key, fallback=False):
        """
        値をboolとして取得。'true', '1', 'yes' などをTrueと判定。
        """
        value = self.get(section, key, fallback)
        if value is not None:
            return str(value).lower() in ("1", "true", "yes", "on")
        return fallback
