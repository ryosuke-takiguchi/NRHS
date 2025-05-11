import pandas as pd

def read_csv_safe(LOGGER , filepath: str) -> pd.DataFrame:
    """
    CSVファイルを例外処理付きで読み込み、安全にDataFrameを返します。

    この関数は、指定されたCSVファイルを読み込みます。
    ファイルが存在しない、空である、またはフォーマットに異常がある場合は、
    ログ出力を行い、空のDataFrameを返します。

    Args:
        LOGGER (logging.Logger): ログ出力に使用するロガーインスタンス。
        filepath (str): 読み込むCSVファイルのパス。

    Returns:
        pd.DataFrame: 読み込みに成功した場合はその内容を含むDataFrame、
                      失敗した場合は空のDataFrame。
    """
    try:
        df = pd.read_csv(filepath)
        LOGGER.info(f"CSV読み込み成功: {filepath}, 件数: {len(df)}")
        return df
    except FileNotFoundError:
        LOGGER.error(f"CSVファイルが見つかりません: {filepath}", exc_info=True)
    except pd.errors.EmptyDataError:
        LOGGER.error(f"CSVファイルが空です: {filepath}", exc_info=True)
    except pd.errors.ParserError as e:
        LOGGER.error(f"CSVファイル構文エラー: {filepath}, 内容: {e}", exc_info=True)
    except Exception as e:
        LOGGER.error(f"CSV読み込み中に予期しないエラーが発生しました: {filepath}, {e}", exc_info=True)

    return pd.DataFrame()
