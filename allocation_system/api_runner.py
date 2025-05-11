import subprocess
from allocation_system.logger import Logger
from allocation_system.config_ini import IniConfig

def run_api(
    file_path: str,
    log_path: str,
    proc_kbn: str,
    number: str,
    LOGGER: "Logger",
    start_ym: str = "",
    end_ym: str = "",
    start_date: str = "",
    end_date: str = "",
) -> bool:
    ini = IniConfig()
    exe_path = ini.get("APIModule", "APIPath")
    uid = ini.get("APIModule", "GaliUID")
    pwd = ini.get("APIModule", "GaliPass")
    CmpCode = ini.get("APIModule", "CmpCode")
    display_mode = ini.getboolean("APIModule", "CmpCode")
    
    if display_mode:
        display_mode = "0"
    else :
        display_mode = "1"

    args = [
        exe_path,
        uid,
        pwd,
        CmpCode,
        "",             # 決算開始年月日
        proc_kbn,
        number,
        file_path,
        log_path,
        display_mode,            # 画面表示区分
        "APIModule",             # 画面表示名
        "0",            # 上書き区分
        "",             # オプション文字列
        start_ym,
        end_ym,
        start_date,
        end_date
    ]

    LOGGER.debug(f"APIモジュール実行コマンド: {' '.join(args)}")

    try:
        result = subprocess.run(args, capture_output=True, text=True)
        LOGGER.debug(f"標準出力: {result.stdout.strip()}")
        LOGGER.debug(f"標準エラー: {result.stderr.strip()}")

        if result.returncode == 0:
            LOGGER.info("APIモジュールの実行に成功しました。")
            return True
        else:
            LOGGER.error(f"APIモジュールは異常終了しました。戻り値: {result.returncode}")
            return False

    except FileNotFoundError as e:
        LOGGER.error(f"APIモジュールが見つかりません: {exe_path}", exc_info=True)
        return False
    except Exception as e:
        LOGGER.error(f"API実行中に予期しないエラーが発生しました: {e}", exc_info=True)
        return False
