# NRHSプロジェクト

## 概要
このプロジェクト「NRHS」は、部門別セグメント配賦をシステム外部で実行するために設計されています。  
主な目的は、会計システムからマスタや実績・配賦ルールを取得し、仕訳データを生成・加工して再度インポートすることです。

---

## 特徴
- `.bat` 実行によるワンアクションでの実績更新
- データ基準による配賦段階の管理

---

## 必要条件
以下の環境が必要です：

- Python 3.10.6（推奨: 3.8以上）
- 外部ライブラリ：`requirements.txt` に記載

---

## インストール手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/ryosuke-takiguchi/NRHS.git

# 2. ディレクトリに移動
cd NRHS

# 3. setting.bat を実行（仮想環境とパッケージをセットアップ）
setting.bat
```

---

## 使用方法

### ▶ 収益認識基準「前」の配賦実行：

1. `run.bat` をダブルクリックまたはコマンドラインで実行  
2. 処理月を入力（例：202405）  
3. 伝票日付を入力（例：2025/05/01）  

### ▶ 収益認識基準「後」の配賦実行：

1. `run_after.bat` を実行  
2. 処理月を入力  
3. 配賦伝票の日付を入力  

---

## ディレクトリ構成（抜粋）

```
NRHS/
├── allocation_system/
│   ├── main_after.py
│   ├── db_access.py
│   └── ...
├── scripts/
│   ├── run_allocation.py
│   └── run_allocation_after.py
├── run.bat
├── run_after.bat
└── setting.bat
```

---

## 📄 ライセンス
MIT License（必要であればここに記載）