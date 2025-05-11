import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy.*")

import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from allocation_system.logger import Logger
from allocation_system.config_ini import IniConfig
from allocation_system.config_env import EnvConfig
from allocation_system.db_access import fetch_dataframe
from allocation_system.api_runner import run_api
from allocation_system.csv_utils import read_csv_safe
from allocation_system.utils import clear_folder
from allocation_system.utils import select_processing_month
from allocation_system.main import main_process

def main():
    print("部門別セグメント配賦プログラム実行")
    print("収益認識基準修正前の実績に対して配賦処理を行います。")
    print("修正前後でプログラムの起動に誤りがある場合、処理月入力待機中にコンソールを終了してください。")
    # --------------------------------------------定数宣言部--------------------------------------------
    EXP_NO_BMN_SEG_REC = "9996"
    EXP_NO_HIF_INFORMATION = "9998"

    
    try:
        print("")
        print("初期処理を開始")
        # --------------------------------------------初期化処理部--------------------------------------------
        # 環境設定読み込み
        env_config = EnvConfig()
        DEBUG_MODE = env_config.getboolean("DEBUG_MODE", fallback=False)
        LOGGER = Logger(__name__, debug_mode=DEBUG_MODE).get_logger()

        LOGGER.info("処理を開始します")

        # iniファイル読み込み
        ini_config = IniConfig()
        LOGGER.info("iniファイル読み込み成功")

        # 環境変数取得（ログに出す。パスワードも含む）
        DSN = env_config.get("DSN")
        DBUID = env_config.get("DBUID")
        DBPWD = env_config.get("DBPWD")
        DATABASENAME = env_config.get("DATABASENAME")
        ENGINENAME = env_config.get("ENGINENAME")
        AUTOSTOP = env_config.get("AUTOSTOP")
        
        LOGGER.debug(f'DSN:{DSN}')
        LOGGER.debug(f'DBUID:{DBUID}')
        LOGGER.debug(f'DBPWD:{DBPWD}')
        LOGGER.debug(f'DATABASENAME:{DATABASENAME}')
        LOGGER.debug(f'ENGINENAME:{ENGINENAME}')
        LOGGER.debug(f'AUTOSTOP:{AUTOSTOP}')

        GALI_APIPath = ini_config.get("APIModule", "APIPath")
        GALI_UID = ini_config.get("APIModule", "GaliUID")
        GALI_PASS = ini_config.get("APIModule", "GaliPass")
        TEMP_FOLDER = ini_config.get("FilesDirectory", "TEMPFOLDER")
        OUT_PUT_FOLDER = ini_config.get("FilesDirectory", "OUTPUTFOLDER")
        
        LOGGER.debug(f'GALI_APIPath:{GALI_APIPath}')
        LOGGER.debug(f'GALI_UID:{GALI_UID}')
        LOGGER.debug(f'GALI_PASS:{GALI_PASS}')
        LOGGER.debug(f'TEMP_FOLDER:{TEMP_FOLDER}')
        LOGGER.debug(f'OUT_PUT_FOLDER:{OUT_PUT_FOLDER}')

        # TEMPフォルダ初期化処理
        LOGGER.info("フォルダ初期化実行")
        clear_folder(folder_path=os.path.join(TEMP_FOLDER, "csv"), LOGGER=LOGGER)
        clear_folder(folder_path=os.path.join(TEMP_FOLDER, "logs"), LOGGER=LOGGER)
        clear_folder(folder_path=os.path.join(OUT_PUT_FOLDER, "csv"), LOGGER=LOGGER)
        
        
        # --------------------------------------------実行月指定部--------------------------------------------
        # 実行月指定
        
        YM, den_date = select_processing_month()
        LOGGER.info(f"選択された内部処理月: {YM}")
        START_YM = YM
        END_YM = YM
        
        print("")
        print("マスタ情報の取得を開始")
        # --------------------------------------------マスタ取得部--------------------------------------------
        timestamp = str(datetime.now().strftime("%Y-%m-%d"))
        
        print("部門マスタの取得開始")
        # 部門マスタ取得
        LOGGER.info("Galileopt部門マスタ取得開始")
        bmn_master_sql = f"""SELECT SumKbn, GCode, NCode, LongName, TEndDate 
         FROM MJSDBMASTER.PV_JNT_BUMON
         WHERE TEndDate > {timestamp} AND SumKbn = 0"""
        try:
            bmn_master = fetch_dataframe(bmn_master_sql, LOGGER)
            LOGGER.info(f"部門マスタ取得件数: {len(bmn_master)}")
        except Exception as e:
            LOGGER.error(f"部門マスタの取得に失敗しました: {e}", exc_info=True)

        print("セグメントマスタの取得開始")
        # セグメントマスタ取得
        LOGGER.info("Galileoptセグメントマスタ取得開始")
        seg_master_sql = f"""SELECT SumKbn, GCode, NCode, LongName, TEndDate
FROM MJSDBMASTER.PV_JNT_SEGMENT1
WHERE TEndDate > {timestamp} AND SumKbn = 0"""
        try:
            seg_master = fetch_dataframe(seg_master_sql, LOGGER)
            LOGGER.info(f"セグメントマスタ取得件数: {len(seg_master)}")
        except Exception as e:
            LOGGER.error(f"セグメントマスタの取得に失敗しました: {e}", exc_info=True)

        print("勘定科目マスタの取得開始")
        # 勘定科目マスタ取得
        LOGGER.info("Galileopt勘定科目マスタ取得開始")
        kmk_master_sql = f"""SELECT SumKbn, GCode, NCode, LongName, TEndDate
FROM MJSDBMASTER.PV_JNT_KMKMA
WHERE TEndDate > {timestamp}"""
        try:
            kmk_master = fetch_dataframe(kmk_master_sql, LOGGER)
            LOGGER.info(f"勘定科目マスタ取得件数: {len(kmk_master)}")
        except Exception as e:
            LOGGER.error(f"勘定科目マスタの取得に失敗しました: {e}", exc_info=True)
        
        print("")
        print("実績の取得開始")
        # --------------------------------------------実績取得部--------------------------------------------
        # 部門別セグメント実績-通常実績取得
        print("部門別セグメント実績-通常の取得")
        LOGGER.info("部門別セグメント実績-通常の取得開始")
        LOGGER.info("エクスポート実行中...")

        api_result = run_api(
            file_path=rf"{TEMP_FOLDER}\csv\Sample.csv",
            log_path=rf"{TEMP_FOLDER}\logs\Sample.log",
            proc_kbn="2",   
            number=EXP_NO_BMN_SEG_REC,
            LOGGER=LOGGER,
            start_ym=START_YM,
            end_ym=END_YM,
        )

        LOGGER.info("CSVデータ取得実行")
        bmn_seg_record_df = read_csv_safe(LOGGER=LOGGER ,filepath = rf"{TEMP_FOLDER}/csv/Sample.csv")
        
        print("")
        print("配賦情報の取得を実行")
        
        # --------------------------------------------配賦情報取得部--------------------------------------------
        # 配賦情報取得部
        print("配賦情報取得")
        LOGGER.info("配賦情報の取得開始")
        LOGGER.info("エクスポート実行中...")

        api_result = run_api(
            file_path=rf"{TEMP_FOLDER}\csv\Sample2.csv",
            log_path=rf"{TEMP_FOLDER}\logs\Sample2.log",
            proc_kbn="2",   
            number=EXP_NO_HIF_INFORMATION,
            LOGGER=LOGGER,
        )
        
        LOGGER.info("CSVデータ取得実行")
        hif_information_df = read_csv_safe(LOGGER=LOGGER, filepath = rf"{TEMP_FOLDER}/csv/Sample2.csv")
        
        dataframes = [
        bmn_master,
        seg_master,
        kmk_master,
        bmn_seg_record_df,
        hif_information_df,
        ]

        if all(df is not None and not df.empty for df in dataframes):
            print("")
            print("配賦処理へ移行")
            LOGGER.info("すべてのデータが正常に取得されました。配賦処理へ進みます。")
            journal_df = main_process(
            bmn_master,
            seg_master,
            kmk_master,
            bmn_seg_record_df,
            hif_information_df,
            den_date,
            START_YM,
            END_YM,
            LOGGER=LOGGER
            )
            
        else:
            LOGGER.error("必要なデータの一部が取得できなかったため、処理を中断します。")
            print("必要なデータの一部が取得できなかったため、処理を中断します。")
            input("エンターキーを押して終了します")
            sys.exit(1)

    except Exception as e:
        try:
            LOGGER 
        except NameError:
            LOGGER = Logger("startup", debug_mode=True).get_logger()
        LOGGER.error(f"致命的なエラーが発生しました: {e}", exc_info=True)
        print(f"致命的なエラーが発生しました")
        input("エンターキーを押して終了します")
        sys.exit(1)

    input("処理が完了しました。エンターキーを押して終了します。")

if __name__ == "__main__":
    main()
