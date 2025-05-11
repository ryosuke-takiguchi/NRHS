import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, name=__name__, debug_mode=False, log_dir="./logs"):
        """
        ロガーの初期化

        :param name: ロガーの名前（通常は __name__）
        :param debug_mode: TrueならDEBUGレベルを含めて出力、FalseならINFO以上
        :param log_dir: ログファイルの保存先ディレクトリ
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        self.logger.propagate = False  # 二重出力防止

        # 出力先ディレクトリ作成
        os.makedirs(log_dir, exist_ok=True)

        # ログファイル名（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        log_filename = f"実行ログ_{timestamp}.log"
        log_filepath = os.path.join(log_dir, log_filename)

        # ログ出力形式: [LEVEL]yyyy/MM/dd hh:mm:ss [message]
        formatter = logging.Formatter("[%(levelname)s]%(asctime)s %(message)s", datefmt="%Y/%m/%d %H:%M:%S")

        # ファイル出力ハンドラ
        file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.debug("loggerの初期化完了")

    def get_logger(self):
        """
        設定済みの logger オブジェクトを返す
        """
        return self.logger
