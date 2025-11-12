# 🚀 Crawl 技能快速启动指南

## 📋 前置条件检查清单

在开始使用 crawl 技能之前，请确保以下条件已满足：

### ✅ 环境检查
- [ ] Python 3.8+ 已安装
- [ ] uv 包管理器已安装
- [ ] Chrome 浏览器已安装
- [ ] 网络连接正常（如需代理访问，确保代理地址正确）

### ✅ 项目检查
- [ ] 项目目录存在 `src/essay_manager.py`
- [ ] 项目根目录有 `.claude/skills/crawl/` 目录
- [ ] MCP 配置文件包含正确的 chrome-devtools 配置

### ✅ MCP 配置验证
确保 `.claude/mcp.json` 包含以下配置：
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222"
      ],
      "env": {}
    }
  }
}
```

## 🎯 快速开始

### 方法一：使用改进版管理器（推荐）

```python
# 直接复制使用
from output.improved_crawl_manager import extract_x_tweets

# 提取Elon Musk的最新5篇推文
result = extract_x_tweets("elonmusk", 5)
print(result)
```

### 方法二：使用标准模板

```python
# 复制以下代码到你的脚本中
import os
import sys
import platform
import subprocess
import time
import json
import requests
from datetime import datetime

# 1. 确保output目录存在
os.makedirs('output', exist_ok=True)

# 2. 启动Chrome浏览器
system = platform.system()
if system == "Windows":
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    cmd = [chrome_path, "--remote-debugging-port=9222", "--proxy-server=http://127.0.0.1:1087"]
elif system == "Darwin":
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [chrome_path, "--remote-debugging-port=9222", "--proxy-server=http://127.0.0.1:1087"]

subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

# 3. 启动API服务
try:
    requests.get("http://localhost:8000/api/health", timeout=5)
except:
    subprocess.Popen(["uv", "run", "python", "essay_manager.py"], cwd="src")
    time.sleep(5)

# 4. 使用MCP工具进行爬取
# ... 在这里添加你的爬取逻辑
```

## 🛠️ 常用命令

### 检查Chrome是否运行
```bash
curl http://127.0.0.1:9222
```

### 检查API服务状态
```bash
curl http://localhost:8000/api/health
```

### 手动启动API服务
```bash
cd src && uv run python essay_manager.py
```

### 查看日志
```bash
tail -f output/logs/crawl_log_$(date +%Y%m%d).txt
```

## 📊 支持的网站和功能

### 🎯 完全支持
- **X/Twitter** (x.com) - 推文提取
- **The Atlantic** (theatlantic.com) - 文章提取
- **Medium** (medium.com) - 文章提取

### 🔧 部分支持
- LinkedIn (需要登录)
- Reddit (基础提取)
- 新闻网站 (通用提取)

## ⚡ 性能优化建议

### 1. 批量处理
```python
# 推荐：批量提取多个用户
users = ["elonmusk", "sundarpichai", "satyanadella"]
results = {}
for user in users:
    results[user] = extract_x_tweets(user, 3)
```

### 2. 错误重试
```python
# 推荐：使用改进版管理器，自动包含重试机制
manager = ImprovedCrawlManager({"max_retries": 5})
```

### 3. 数据验证
```python
# 推荐：验证数据格式后再发送
if manager.validate_data_format(api_data):
    result = manager.send_to_api(api_data)
```

## 🚨 常见问题和解决方案

### Q1: Chrome启动失败
**解决方案**:
1. 检查Chrome安装路径是否正确
2. 确保9222端口未被占用
3. 尝试手动启动Chrome并添加调试参数

### Q2: MCP连接失败
**解决方案**:
1. 检查`.claude/mcp.json`配置
2. 确保chrome-devtools-mcp包已安装
3. 重启Claude Code

### Q3: API服务启动失败
**解决方案**:
1. 检查`src/essay_manager.py`是否存在
2. 确保uv已安装
3. 检查8000端口是否被占用

### Q4: 数据写入失败
**解决方案**:
1. 检查数据格式是否符合要求
2. 确保API服务正在运行
3. 查看API服务日志

## 📁 文件结构说明

```
output/
├── logs/              # 日志文件
│   └── crawl_log_*.txt
├── data/              # 数据文件
│   ├── *_raw_*.json   # 原始提取数据
│   └── api_response_*.json
├── snapshots/         # 页面快照
│   └── *_page_*.txt
└── reports/           # 执行报告
    └── *_report_*.md
```

## 🔗 相关文档

- [完整文档](SKILL.md)
- [Chrome DevTools MCP 配置](how-to-crawl-with-chrome-dev-mcp.md)
- [改进版管理器源码](../output/improved_crawl_manager.py)

## 💡 最佳实践

1. **使用改进版管理器** - 包含完整的错误处理和日志记录
2. **验证数据格式** - 确保URL字段存在且有效
3. **保存原始数据** - 便于调试和重试
4. **查看执行报告** - 了解任务执行详情
5. **定期清理日志** - 避免日志文件过大

---

🎉 **现在你已经准备好使用 crawl 技能了！**