import os

def clear_folder(folder_path: str, LOGGER=None):
    """
    指定フォルダ内のファイルをすべて削除する（サブフォルダ除く）。

    Args:
        folder_path (str): 削除対象フォルダのパス
        LOGGER (logging.Logger, optional): ログ出力用ロガー（任意）
    """
    if not os.path.exists(folder_path):
        if LOGGER:
            LOGGER.warning(f"指定フォルダが存在しません: {folder_path}")
        return

    deleted = 0
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                deleted += 1
                if LOGGER:
                    LOGGER.debug(f"削除: {file_path}")
            except Exception as e:
                if LOGGER:
                    LOGGER.error(f"ファイル削除に失敗: {file_path}, {e}", exc_info=True)

    if LOGGER:
        LOGGER.info(f"{folder_path} フォルダから {deleted} 件のファイルを削除しました。")

def select_processing_month() -> str:
    """
    ユーザーに処理月を選択させ、内部的なYMコードを返す。
    入力が無効な場合は再入力を促す。

    Returns:
        str: 内部月コード（例: "1", "2", ..., "12", "y3", "y4", "y5"）
    """
    print("")
    print("処理を実行する月を選択してください")
    print("　 3月・・・ 3   　 4月・・・ 4     　 5月・・・ 5")
    print("　 6月・・・ 6   　 7月・・・ 7     　 8月・・・ 8")
    print("　 9月・・・ 9   　10月・・・10     　11月・・・11")
    print("　12月・・・12   　 1月・・・ 1     　 2月・・・ 2")
    print("翌 3月・・・y3   翌 4月・・・y4     翌 5月・・・y5")

    month_map = {
        "3": "1", "4": "2", "5": "3", "6": "11", "7": "12", "8": "13",
        "9": "21", "10": "22", "11": "23", "12": "31", "1": "32", "2": "33",
        "y3": "41", "y4": "42", "y5": "43"
    }

    while True:
        input_month = input("処理月を上記選択肢の内から入力してください >>> ").strip()
        ym = month_map.get(input_month)
        if ym is not None:
            while True:
                input_den_date = str(input("配賦伝票の伝票日付をyyyymmdd形式で入力してください。").strip())
                confirm = input(f"伝票日付は「{input_den_date}」で間違いないですか？ (Y/n): ").strip().lower()
                if confirm in ("", "y", "yes"):
                    return ym, input_den_date
                elif confirm == "n":
                    print("もう一度日付を入力してください。")
                else:
                    print("Y または N で入力してください。")
            # ※ return はループの内側にあるため、適切に終了します
        else:
            print("入力が正しくありません。もう一度選択してください。")

def hankaku_to_zenkaku_numbers(text: str) -> str:
    """
    半角数字を全角数字に変換する。

    Args:
        text (str): 変換対象の文字列

    Returns:
        str: 全角数字に変換された文字列
    """
    hankaku = "0123456789"
    zenkaku = "０１２３４５６７８９"
    trans_table = str.maketrans(hankaku, zenkaku)
    return text.translate(trans_table)

def make_range_list(a, b):
    start = min(a, b)
    end = max(a, b)
    return list(range(start, end + 1))