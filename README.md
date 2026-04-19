# 條陳機器人（康定所報告／萬華分局報告）

## 目標

輸入草稿、群組訊息、口述紀錄或他所文本，輸出可直接上呈的正式條陳。

## 核心行為

- 預設固定輸出：
  1. 康定所報告
  2. 萬華分局報告
- 僅在明確指定時輸出：
  - 報局長版本（`--chief`）
  - 回覆議座版本（`--council`）
- `--verbatim`：原文照登，不潤飾、不重排。
- 條列間不留空行。
- 時間格式去除前導 0（例如：115年4月2日、23時5分）。

## CLI 快速使用

```bash
python tiaochen_bot.py "民眾疑遭投資詐騙，匯款新台幣50萬元"
python tiaochen_bot.py --input-file case.txt
python tiaochen_bot.py --input-file case.txt --chief --council
python tiaochen_bot.py --input-file case.txt --verbatim
```

## APP（網頁版）使用

```bash
python web_app.py
```

啟動後打開：

- `http://localhost:8000`

畫面可直接：

- 貼上原始案件內容
- 選擇「自動判斷」或指定模板
- 勾選是否加出局長版／議座版／原文照登
- 一鍵產生條陳

## PWA（可加到手機主畫面）

此專案已支援 PWA（manifest + service worker）：

- Android（Chrome）：開啟網址後，選單點「加入主畫面」。
- iPhone（Safari）：分享 →「加入主畫面」。

> 注意：手機安裝 PWA 建議使用 HTTPS 網址；`localhost` 主要供本機測試。

## 案型路由（摘要）

- fraud：165 / 投資 / 面交 / 詐欺
- drug：毒品 / 毒駕
- dui：酒駕 / 公共危險
- group_brawl：鬥毆 / 聚眾
- fight：打架 / 口角 / 傷害
- theft：竊盜 / 監視器
- death：死亡 / 行政相驗 / OHCA
- fire_or_signal：119 / 火災 / 誤報 / 號誌

## 測試

```bash
python -m py_compile tiaochen_bot.py web_app.py
python -m unittest -v
```
