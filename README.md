# スケジュール管理 Web アプリ

Flask と SQLite を使ったシンプルなスケジュール管理アプリです。予定の追加・編集・削除をブラウザ上から行えます。

## セットアップ
1. 依存パッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
2. アプリを起動します。
   ```bash
   flask --app app run
   ```
3. ブラウザで http://localhost:5000 を開きます。

## 主な機能
- 予定の作成・編集・削除
- ISO8601 形式での日時保存（SQLite）
- 一覧の自動並び替えと手動更新
- PC/モバイル両対応の簡易 UI
