import pandas as pd
from tqdm import tqdm
from allocation_system.utils import hankaku_to_zenkaku_numbers, make_range_list
from allocation_system.allocator import perform_allocation
from allocation_system.api_runner import run_api


def process_allocation_row(
    allocation_rule, bmn_seg_record, kmk_master,
    bmn_master, existing_kmk_codes, existing_bmn_codes,
    existing_seg_codes, swk_source_df, den_date, LOGGER=None
):
    """
    単一の配賦情報に基づいて、対象科目と対象部門を抽出し、配賦処理を実行する。
    Returns:
        pd.DataFrame: swk_source_df に追加する仕訳データの一部（fragment）
    """
    if LOGGER:
        LOGGER.debug(f"配賦パターンNO:{allocation_rule['パターンＮＯ']}【{allocation_rule['パターン名称']}】の配賦処理を開始")
    tekiyo = f"配賦パターンNO:{allocation_rule['パターンＮＯ']}　{allocation_rule['パターン名称']}"

    # 対象科目抽出
    target_range_kmk_list = make_range_list(
        allocation_rule['配賦元 （開始）科目コード'],
        allocation_rule['配賦元 （終了）科目コード']
    )
    target_kmk_list = sorted(set(target_range_kmk_list) & set(existing_kmk_codes))

    # 対象部門抽出
    bmn_range = []
    for j in range(20):
        zenkaku_j = hankaku_to_zenkaku_numbers(str(j + 1))
        start_key = f"配賦先 （開始）部門コード（{zenkaku_j}）"
        end_key = f"配賦先 （終了）部門コード（{zenkaku_j}）"
        if allocation_rule[start_key] != "":
            min_bmn = int(allocation_rule[start_key])
            max_bmn = int(allocation_rule[end_key])
            bmn_range.extend(make_range_list(min_bmn, max_bmn))
    target_bmn_list = sorted(set(existing_bmn_codes) & set(bmn_range))

    swk_fragment_df, bmn_seg_record = perform_allocation(
        allocation_rule, bmn_seg_record, target_kmk_list,
        target_bmn_list, existing_seg_codes, swk_source_df, tekiyo, LOGGER
    )
    return swk_fragment_df, bmn_seg_record


def main_process(
    bmn_master, seg_master, kmk_master,
    bmn_seg_record, hif_information, den_date, START_YM, END_YM, LOGGER=None
):
    # 配賦種別ごとの処理ループ
    for allocation_level, keyword, j in [
        ("1次配賦", "収益認識後　一次", "0"),
        ("2次配賦", "収益認識後　二次", "1"),
        ("3次配賦", "収益認識後　三次", "2"),
        ("4次配賦", "収益認識後　四次", "3")
    ]:
        filtered_hif_info = hif_information[
            (hif_information["マスタ区分"] == 41) &
            (hif_information["配賦区分"] == 0) &
            (hif_information["パターン名称"].str.startswith(keyword, na=False))
        ]
        bmn_seg_record = main_process1(
            allocation_level, bmn_master, filtered_hif_info,
            seg_master, kmk_master,
            bmn_seg_record, den_date, START_YM, END_YM, j, LOGGER
        )


def main_process1(
    allocation_level, bmn_master, filtered_hif_info,
    seg_master, kmk_master, bmn_seg_record,
    den_date, START_YM, END_YM, j, LOGGER=None
):
    """
    単一レベルの配賦処理を実行し、CSVに出力します。
    """
    if LOGGER:
        LOGGER.info(f"{allocation_level}の配賦処理を開始します")

    existing_kmk_codes = kmk_master[kmk_master["SumKbn"] == 0]["GCode"].tolist()
    existing_bmn_codes = sorted([int(x) for x in bmn_master[bmn_master["SumKbn"] == 0]["GCode"].tolist()])
    existing_seg_codes = sorted([int(x) for x in seg_master[seg_master["SumKbn"] == 0]["GCode"].tolist()])

    columns = [
        '伝票番号','借方科目', '借方部門', '借方セグメント', '借方税CD', '借方金額', 
        '貸方科目', '貸方部門', '貸方セグメント', '貸方税CD', '貸方金額', '摘要文字列'
    ]
    swk_source_df = pd.DataFrame(columns=columns)

    for i in tqdm(range(len(filtered_hif_info)), desc=f"{allocation_level}計算処理実行中", unit="件"):
        allocation_rule = filtered_hif_info.iloc[i].fillna("").to_dict()
        swk_fragment_df, bmn_seg_record= process_allocation_row(
            allocation_rule, bmn_seg_record,
            kmk_master, bmn_master, existing_kmk_codes,
            existing_bmn_codes, existing_seg_codes,
            swk_source_df, den_date, LOGGER
        )
        swk_source_df = pd.concat([swk_source_df, swk_fragment_df], ignore_index=True)

    if LOGGER:
        LOGGER.info(f"{allocation_level}の配賦処理が完了しました")

    swk_source_df["データ基準"] = "0"
    swk_source_df["データ種別"] = "99"
    swk_source_df["仕訳入力形式"] = "1002"
    swk_source_df["入力画面NO"] = "0"
    swk_source_df["伝票日付"] = den_date
    swk_source_df["借方補助"] = ""
    swk_source_df["借方セグメント2"] = ""
    swk_source_df["借方資金繰り"] = ""
    swk_source_df["借方税率区分"] = ""
    swk_source_df["借方事業者区分"] = ""
    swk_source_df["貸方補助"] = ""
    swk_source_df["貸方セグメント2"] = ""
    swk_source_df["貸方資金繰り"] = ""
    swk_source_df["貸方税率区分"] = ""
    swk_source_df["貸方事業者区分"] = ""

    
    swk_source_df = swk_source_df[
        ["データ基準", "データ種別", "仕訳入力形式", "入力画面NO", "伝票日付", "伝票番号",
        "借方科目", "借方補助", "借方部門", "借方セグメント", "借方セグメント2", "借方資金繰り", "借方税CD", "借方税率区分", "借方事業者区分", "借方金額",
        "貸方科目", "貸方補助", "貸方部門", "貸方セグメント", "貸方セグメント2", "貸方資金繰り", "貸方税CD", "貸方税率区分", "貸方事業者区分", "貸方金額", "摘要文字列"]
        ]
       
    swk_source_df.to_csv(rf"./allocation_system/output/csv/収益認識後_{allocation_level}.csv", index=False, encoding="shift_jis")
    print("csv出力完了")
    print("配賦結果の取り込み開始")
    print("データインポート中...")
    in_out_no = "910" + str(int(j) + 4)
    run_api(
        file_path = rf"./allocation_system/output/csv/収益認識後_{allocation_level}.csv",
        log_path = rf"./allocation_system/output/logs/収益認識後_{allocation_level}.log",
        proc_kbn= "1",
        number = in_out_no,
        LOGGER = LOGGER,
        start_ym = START_YM,
        end_ym = END_YM
    )
    print("データインポート完了")

    
    
    return bmn_seg_record
