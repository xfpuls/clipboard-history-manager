学习的视频原链接https://www.bilibili.com/video/BV1BvR1BtEFD/


# 剪贴板历史管理器

一个运行在 Windows 上的轻量级剪贴板历史管理工具，常驻系统托盘，自动记录文字和图片复制内容。

![版本](https://img.shields.io/github/v/release/xfpuls/clipboard-history-manager?label=版本&color=5B9BD5)

## 功能

- **实时记录** — 后台监控剪贴板，自动保存文字和图片
- **卡片浏览** — 时间降序排列，自适应高度的卡片展示
- **搜索筛选** — 关键词搜索 + 全部/文字/图片类型筛选
- **置顶删除** — 重要内容置顶，不需要的可删除
- **历史分页** — 15 条/页，分页浏览完整历史
- **全局快捷键** — Ctrl+Shift+V 呼出/隐藏面板
- **窗口置顶** — 面板保持在其他窗口之上
- **开机自启** — 支持设置开机自动启动
- **存储管理** — 可设 1/3/5 天保存期限 + 200/500/1000 数量上限
- **更新检测** — 启动时自动检测新版本

## 运行

双击 `剪贴板历史管理器.exe` 启动，或：

```bash
pip install -r requirements.txt
python main.py
```

## 技术

- Python 3 + PySide6
- SQLite 本地存储
- Windows API 全局热键
- PyInstaller 打包

## 项目结构

```
lishijiil/
├── main.py                  # 入口
├── requirements.txt          # 依赖
└── clipboard_manager/
    ├── app.py               # 主程序
    ├── config.py            # 配置管理
    ├── database.py          # 数据库
    ├── clipboard_monitor.py # 剪贴板监控
    ├── hotkey.py            # 全局热键
    ├── updater.py           # 更新检测
    └── ui/
        ├── styles.py        # 淡蓝色主题
        ├── card_widget.py   # 卡片组件
        ├── main_panel.py    # 主面板
        ├── history_window.py # 历史窗口
        ├── settings_page.py  # 设置页
        └── tray.py          # 系统托盘
```
