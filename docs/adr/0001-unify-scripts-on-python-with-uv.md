---
status: accepted
---

# 全面統一為 Python（以 uv 管理相依）

本 repo 原本 4 個工具橫跨 4 種語言（Python、PowerShell、JavaScript、Batch）。2026-08 決定全部統一為 Python：既有 Python 腳本保留，PowerShell 與 JavaScript 工具改寫為 Python，相依套件以 PEP 723 內嵌中繼資料宣告、由 uv 於執行時自動安裝。理由：單一心智模型（維護與新增腳本不再切換語言）、環境管理交給 uv（免手動 venv／pip）。

## Considered Options

- **全 PowerShell**——唯一能零相依的選項（Win32 功能全部內建），移植量也最小之一，但作者寫起來最不順手，被否決。（決策過程中曾一度選定，隨後反悔改為 Python。）
- **全 JavaScript（Node）**——作者最順手的語言，檔案／文字處理完全勝任；敗在 Win32 桌面 API（視窗標題、資源回收桶、剪貼簿）需要第三方原生套件或借道 PowerShell。
- **維持多語言現狀**——被一致性與「單純好看」的目標否決。

## Consequences

- Win32 功能改由 pywin32（視窗標題、剪貼簿）與 send2trash（資源回收桶）提供——repo 從零第三方相依變為有相依，由 uv 管理。
- 執行腳本的機器需要有 uv 與 Python（≥3.13）。
