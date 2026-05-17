# Bug 修复记录

## 第 1 天 — 2026/05/16

| # | 时间 | 问题 | 根因 | 修复 |
|---|------|------|------|------|
| 1 | 18:00 | 卡片文字显示不全 | 卡片固定高度 58px + 单行截断 | 改为自适应高度，最多 4 行，超出省略号，悬停看全文 |
| 2 | 18:10 | 设置页面文字截断 | 标签没开 word wrap，没滚动条 | 全改为 `WrapLabel` + `QScrollArea` |
| 3 | 18:30 | 托盘右键菜单无反应 | `TrayManager` 非 QObject，菜单无父对象被 GC | 改为继承 `QObject`，菜单 parent=self |
| 4 | 19:00 | 窗口置顶切换闪烁，之后关闭按钮失效 | `setWindowFlags` + `show()` 重建了原生窗口，信号连接断开 | 改用 `hide()` → 改 flags → `show()` 三步走 |
| 5 | 19:10 | ✕ 关闭只是隐藏界面，进程残留 | `closeEvent` 只是 hide 到托盘，`app.quit()` 未触发 | `closeEvent` 改为直接调用 `_quit()` → `os._exit(0)` |
| 6 | 19:15 | 双击 exe 不显示面板 | 启动后没调 `_show_panel()` | `ClipboardApp.__init__` 末尾加上 `_show_panel()` |
| 7 | 19:15 | 窗口置顶默认开启 | 初始 `WindowStaysOnTopHint` + 按钮 checked=True | 改为默认关闭，按钮 unchecked |
| 8 | 21:00 | 点击卡片 Ctrl+V 粘贴失效 | 卡片文字 QLabel 拦截了鼠标点击事件，卡片收不到点击信号 | 标签设 `WA_TransparentForMouseEvents` 让点击穿透 |
| 9 | 21:40 | 2 秒自动刷新导致卡片点击时可能被重建 | 定时器轮询重建所有卡片，有竞态 | 去掉定时器，改为剪贴板新增时事件驱动刷新 |
| 10 | 22:00 | Qt 自定义信号传 dict 不稳定 | `Signal(dict)` + `emit(record)` 链条过长 | 卡片改为 QPushButton + `mouseReleaseEvent` 直接 Python 回调 |

## 第 2 天 — 2026/05/17

| # | 时间 | 问题 | 根因 | 修复 |
|---|------|------|------|------|
| 11 | 23:15 | 连续点不同卡片，粘贴永远是第一条（**核心 bug**） | `main_panel.py` 未导入 `QApplication`，pyperclip 失败后 Qt 回退报 `NameError` 被 `try/except` 静默吞掉，剪贴板始终不更新 | 补上 `QApplication` 导入，双写机制完整生效 |

---

**总计：11 个 bug，跨越 2 天，核心 bug #11 因静默异常被 try 吞掉，诊断耗时最长。**
