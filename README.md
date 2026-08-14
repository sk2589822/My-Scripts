# My Scripts

個人媒體收藏（漫畫、字幕、圖片）的整理工具箱。所有工具統一用 Python 撰寫，相依套件以 PEP 723 內嵌宣告、由 [uv](https://docs.astral.sh/uv/) 於執行時自動安裝。

## 工具

| 腳本 | 用途 |
| --- | --- |
| `format-manga.py` | 把待整理區的漫畫資料夾改名成「作者　標題」格式，先預覽全部結果、按 Enter 才執行 |
| `format-subtitles.py` | 批次統一 `.ass` 字幕樣式；原檔備份到 `subtitle-backup/`，並把影片檔名對齊字幕檔名 |
| `resize-images.py` | 用 ImageMagick 批次把圖片縮到最大高度；原圖經 `Original/` 暫存後丟資源回收桶 |
| `massigra-save-session.py` | 關機前：把 MassiGra 開著的所有圖存成工作階段檔（`massigra-session.json`） |
| `massigra-open-session.py` | 開機後：讀工作階段檔，重新開啟所有圖 |

## 執行方式

- 直接雙擊 `.py`（`.py` 的檔案關聯已指向 `uv run`，相依套件會自動裝好）
- 或在終端機執行：`uv run format-manga.py`

## 慣例

- 每支腳本頂部有「設定區」常數塊，改設定＝改原始碼
- 腳本結尾停住等 Enter，雙擊執行時視窗不會閃退
- 領域詞彙見 [CONTEXT.md](CONTEXT.md)，重大決策見 [docs/adr/](docs/adr/)

## 需求

- Windows + [uv](https://docs.astral.sh/uv/)（Python ≥ 3.13）
- `resize-images.py` 需要 ImageMagick（`magick` 在 PATH 上）
