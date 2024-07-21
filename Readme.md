
# OBS-AutoResetAppAudioCapture

* OBS : v29以降（30.2.0で動作確認）

## 1. 概要

* 2時間程度経過するとブチブチというノイズが乗り始めるApplication audio capture（アプリケーション音声キャプチャ）の問題に対処するために、一定周期でソースを一瞬無効にして自動的に回避するツールです。
* この問題はWindows11 24H2で解決する予定なので、不要になる方も居ると思われます。


## 2. 必要情報の設定

1. .envファイルに以下の必要情報を記入して、AutoResetAppAudioCapture.exeと同じフォルダに入れる（example.envをリネーム＆編集してお使いください）<br>
   <>で囲われた部分を、お使いのOBSの設定に合わせて設定してください。

   * OBSHost=<接続先OBSのIPアドレス。同じPCであればlocalhost>
   * OBSPort=<接続先OBSのWebSocketサーバーのサーバーポート>
   * OBSPass=<接続先OBSのWebSocketサーバーのサーバーパスワード>
   * IntervalSec=<Application audio captureを一瞬切る周期(秒)>

## 3. 使用方法


1. OBSを先に起動して、WebSocketサーバーを有効にしておく
   * ツール＞WebSocketサーバー設定から「WebSocketサーバー設定」ウィンドウを開く
   ![obs_websocket_1](https://github.com/L4yLa/OBS-AutoResetAppAudioCapture/assets/69630402/abaeebc2-bf69-4ce6-9e94-adcabb6ee04b)
   * WebSocketサーバーを有効にするのチェックボックスを入れる
   * サーバーポートが.envに設定した値と一致しているか確認(OBSPort)
   * 認証を有効にするのチェックボックスを入れる
   * サーバーパスワードが.envに設定した値を一致しているか確認(OBSPass)
   ![obs_websocket_2](https://github.com/L4yLa/OBS-AutoResetAppAudioCapture/assets/69630402/980133ef-8278-4157-8926-ebd6be535abd)
3. AutoResetAppAudioCapture.exeをダブルクリックして起動
4. IntervalSec[s]の周期で自動的に現在のソースにあるApplication audio captureを一瞬切ってノイズを回避します。特に操作は必要ありません。

