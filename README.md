# checkpoint_CVE_crawler

自動幫你到 [Check Point 安全公告網站](https://support.checkpoint.com/security-advisories) 找出「最近幾天內、很危險」的漏洞（CVE）。

---

## 🧸 用最簡單的方式說明（ELI5）

想像 Check Point 網站是一面**公告欄**，上面貼滿了「哪裡有破洞要小心」的紙條，每張紙條都寫著：

- **危險程度**：Critical（超危險）、High（很危險）、Medium（普通）、Low（還好）
- **貼上去的日期**（Published）

每天自己去看公告欄很累，所以我們做了一個**小機器人**：

1. 機器人自己打開瀏覽器，走到公告欄前面。
2. 一張一張看紙條，只撿起「**超危險**或**很危險**」而且是「**最近 3 天或 7 天內**貼上去」的紙條。
3. 看到超過指定天數的舊紙條時，就知道後面都是更舊的，直接收工回家（因為公告欄會把新紙條貼在最前面）。
4. 把撿到的紙條念給你聽（印在畫面上），再抄一份到筆記本（CSV 檔）。

### 為什麼要「避開反爬蟲機制」？

有些網站不喜歡機器人來看，會想辦法把機器人趕走。所以我們的小機器人會**假裝成一般人**：

| 小機器人做的事 | 就像是… |
|---|---|
| 換掉瀏覽器的身分標籤（User-Agent） | 把「我是機器人」的名牌拿掉 |
| 隱藏 `navigator.webdriver` | 把「這是自動操作」的標記藏起來 |
| 翻頁前後隨機停一下 | 像真人一樣慢慢看，不會一秒翻十頁 |
| 打不開時等一下再試（最多 3 次，一次比一次等更久） | 敲門沒人應，過一會兒再敲，不會一直狂敲 |
| 用大螢幕尺寸開網頁 | 螢幕太小，網站會變成手機版，就看不到表格了 |

---

## 🛠️ 事前準備

你的電腦需要有：

- **Python 3**（開發時使用 3.13；檢查方式：`python3 --version`）
- **Google Chrome 或 Chromium 瀏覽器**（小機器人要用它來開網頁）

## 📦 安裝（只要做一次）

```bash
# 1. 下載專案
git clone https://github.com/joe50304/checkpoint_CVE_crawler.git
cd checkpoint_CVE_crawler

# 2. 建立虛擬環境（像是幫這個專案準備一個專屬的工具箱）
python3 -m venv .venv

# 3. 打開工具箱
source .venv/bin/activate

# 4. 把需要的工具放進工具箱
pip install -r requirements.txt
```

> 💡 看到命令列前面出現 `(.venv)`，就代表工具箱已經打開了。
> 用完想關掉，輸入 `deactivate` 即可。

## ▶️ 開始使用

先確認工具箱有打開（`source .venv/bin/activate`），再執行：

```bash
# 抓最近 7 天的 Critical / High 漏洞（沒指定時預設就是 7 天）
python crawler.py --days 7

# 抓最近 3 天的
python crawler.py --days 3
```

### 所有參數

| 參數 | 用途 | 預設值 |
|---|---|---|
| `--days` | 要抓幾天內的公告，只能填 `3` 或 `7` | `7` |
| `--out` | CSV 檔要存在哪裡 | `checkpoint_cve.csv` |
| `--shot` | 截圖檔名前綴，會存成 `<前綴>_p<頁數>.png`，符合條件的列會加上紅框 | 不截圖 |
| `--show` | 開啟看得到的瀏覽器視窗，可以親眼看機器人在做什麼 | 關閉（背景執行） |

### 範例：抓 7 天內的漏洞，順便截圖佐證

```bash
mkdir -p shots
python crawler.py --days 7 --out shots/cve_7d.csv --shot shots/days7
```

畫面會出現：

```
Local date 2026-09-15 | cutoff 2026-09-08 (7 days) | 2 match(es)
2026-09-08  Critical CVSS 9.8  CVE-2026-85102   Improper validation of certificate data during VPN negotiation ...
2026-09-08  Critical CVSS 9.8  CVE-2026-85103   A heap overflow in the VPN certificate ASN.1 decoding ...
Saved shots/cve_7d.csv
```

- `Local date`：你電腦今天的日期
- `cutoff`：最早要抓到哪一天（今天減掉天數，當天也算在內）
- `match(es)`：總共抓到幾筆

## 📄 輸出的 CSV 長什麼樣子

| 欄位 | 意思 |
|---|---|
| `cve` | 漏洞編號，例如 `CVE-2026-85102` |
| `severity` | Check Point 危險程度（Critical / High） |
| `cvss` | CVSS 分數，越高越危險（滿分 10） |
| `published` | 公告發布日期 |
| `updated` | 最後更新日期 |
| `summary` | 漏洞說明 |
| `link` | 官方公告的詳細網址 |

> CSV 使用 `UTF-8 with BOM` 編碼，直接用 Excel 開也不會變亂碼。

## 📸 驗證截圖

以下截圖是實際執行的結果（本機日期 2026-09-15），**紅框**就是小機器人撿到的紙條：

**最近 7 天**：抓到 2 筆 Critical

![7 天](shots/days7_p1.png)

**最近 3 天**：沒有符合條件的公告（0 筆），畫面上沒有紅框

![3 天](shots/days3_p1.png)

**跨頁測試**（抓 120 天內的資料）：第 2 頁的 3 筆 High 也有抓到，沒有重複

![跨頁](shots/days120_p2.png)

## ✅ 自我檢查

篩選規則（危險程度＋日期）有小測試，改程式後可以跑一下：

```bash
python test_crawler.py
# 印出 ok 就代表篩選規則正常
```

## ❓ 常見問題

**Q：出現 `ModuleNotFoundError: No module named 'DrissionPage'`？**
A：工具箱沒打開，或還沒安裝。先執行 `source .venv/bin/activate`，再執行 `pip install -r requirements.txt`。

**Q：出現 `advisory table not found (blocked or layout changed)`？**
A：小機器人敲了 3 次門都找不到表格。可能是網路不穩、被網站擋下來，或網站改版了。可以加上 `--show` 親眼看看瀏覽器畫面卡在哪裡。

**Q：為什麼 `--days` 只能填 3 或 7？**
A：這是依照需求設定的。如果想抓其他天數，把 `crawler.py` 裡 `choices=(3, 7)` 這一行改掉就可以了。

**Q：有沒有什麼限制？**
A：小機器人假設網站的公告是「**新的排在最前面**」，所以看到舊資料就提早收工。如果哪天網站改了排序方式，可能會漏抓。
