import pandas as pd
import numpy as np

from allocation_system.api_runner import run_api


def perform_allocation(
    row_dict,
    bmn_seg_record,
    target_kmk_list,
    target_bmn_list,
    jitsuzai_segs_list,
    swk_base_df,
    tekiyo,
    bmn_rec,
    LOGGER=None
):
    """
    指定された配賦ルールに従って、元データから仕訳データを生成する。

    Returns:
        pd.DataFrame: 仕訳データの断片（swk_fragment_df）
        pd.DataFrame: 実績データ更新後の bmn_seg_record
    """
    HKGO = 999888
    swk_add_rows = []

    kjn_kbn = row_dict["基準科目区分（１）"]
    kjn_code = row_dict["基準科目コード（１）"]
    bmn_cd = row_dict["配賦元 部門コード"]

    # 配賦係数の取得
    if kjn_kbn == 1:
        hif_kjn_df = bmn_rec[
            (bmn_rec['部門コード'].isin(target_bmn_list)) &
            (bmn_rec['科目コード'] == kjn_code)
        ][['部門コード', '月次実績']].copy()

        hif_kjn_df.columns = ['配賦先部門コード', '配賦係数']
    else:
        hif_kjn = [1] * len(target_bmn_list)
        hif_kjn_df = pd.DataFrame({
            '配賦先部門コード': target_bmn_list,
            '配賦係数': hif_kjn
        })

    # 科目・セグメント単位で配賦処理
    for kmk_cd in target_kmk_list:
        for seg_cd in jitsuzai_segs_list:
            filtered_df = bmn_seg_record[
                (bmn_seg_record['科目コード'] == kmk_cd) &
                (bmn_seg_record['部門コード'] == bmn_cd) &
                (bmn_seg_record['セグメントコード'] == seg_cd)
            ]

            if filtered_df.empty:
                continue

            haihutaisyou = filtered_df.iloc[0].tolist()
            haihutaisyou = [int(x) if isinstance(x, np.integer) else x for x in haihutaisyou]

            # 差額が存在する場合のみ配賦処理
            if haihutaisyou[6] != 0 or haihutaisyou[7] != 0:
                if LOGGER:
                    LOGGER.info(f"{kmk_cd}:{bmn_cd}:{seg_cd}")
                
                amount_to_allocate = haihutaisyou[6] - haihutaisyou[7]
                
                # 貸方：配賦元の減額仕訳
                swk_add_rows.append([
                    "910" + str(row_dict['パターンＮＯ']).zfill(3),
                    str(HKGO), "", "", "", "",
                    str(kmk_cd), str(bmn_cd).zfill(4),
                    str(seg_cd).zfill(4), "40",
                    str(amount_to_allocate), tekiyo
                ])

                # 配賦先への金額配分
                total_rate = hif_kjn_df["配賦係数"].sum()
                kingaku_sum = 0

                for i, target_bmn in enumerate(target_bmn_list):
                    rate = hif_kjn_df.loc[
                        hif_kjn_df["配賦先部門コード"] == target_bmn,
                        "配賦係数"
                    ].iloc[0]

                    if i < len(target_bmn_list) - 1:
                        kingaku = round(amount_to_allocate * (rate / total_rate))
                    else:
                        kingaku = amount_to_allocate - kingaku_sum

                    # 実績更新
                    condition = (
                        (bmn_seg_record['科目コード'] == kmk_cd) &
                        (bmn_seg_record['部門コード'] == target_bmn) &
                        (bmn_seg_record['セグメントコード'] == seg_cd)
                    )
                    if not bmn_seg_record[condition].empty:
                        bmn_seg_record.loc[condition, '借方発生額'] += kingaku

                    kingaku_sum += int(kingaku)

                    # 借方：配賦先の増額仕訳
                    swk_add_rows.append([
                        "910" + str(row_dict['パターンＮＯ']).zfill(3),
                        str(kmk_cd), str(target_bmn).zfill(4),
                        str(seg_cd).zfill(4), "40", str(kingaku),
                        str(HKGO), "", "", "", "", tekiyo
                    ])

                # 元部門の実績を減額
                condition2 = (
                    (bmn_seg_record['科目コード'] == kmk_cd) &
                    (bmn_seg_record['部門コード'] == bmn_cd) &
                    (bmn_seg_record['セグメントコード'] == seg_cd)
                )
                if not bmn_seg_record[condition2].empty:
                    bmn_seg_record.loc[condition2, '借方発生額'] -= kingaku_sum

    swk_fragment_df = pd.DataFrame(swk_add_rows, columns=swk_base_df.columns)
    return swk_fragment_df, bmn_seg_record
