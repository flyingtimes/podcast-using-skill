#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawl Manager - 核心爬虫管理器

这个文件包含了crawl技能的核心功能模块，可以直接导入使用。

主要功能:
- 智能浏览器管理
- 统一API集成
- 推文提取专用函数
- 错误处理和重试机制

作者: Claude Code
版本: v2.0
"""

import os
import sys
import platform
import subprocess
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class CrawlManager:
    """基础爬虫管理器"""

    def __init__(self):
        self.output_dir = "output"
        self.api_base_url = "http://localhost:8000"
        self.chrome_port = 9222
        self.proxy_url = "http://127.0.0.1:1087"

        # 确保output目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/logs", exist_ok=True)
        os.makedirs(f"{self.output_dir}/data", exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """日志记录"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)

        # 写入日志文件
        try:
            with open(f"{self.output_dir}/logs/crawl_log_{datetime.now().strftime('%Y%m%d')}.txt",
                     'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except:
            pass

    def start_chrome_browser(self) -> bool:
        """启动Chrome浏览器"""
        system = platform.system()
        self.log(f"检测到操作系统: {system}")

        try:
            # 检查Chrome是否已经运行
            try:
                response = requests.get(f"http://127.0.0.1:{self.chrome_port}", timeout=2)
                self.log("Chrome浏览器已在运行")
                return True
            except:
                pass

            if system == "Windows":
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                cmd = [
                    chrome_path,
                    f"--remote-debugging-port={self.chrome_port}",
                    f"--proxy-server={self.proxy_url}",
                    "--user-data-dir=./userdata"
                ]
            elif system == "Darwin":  # macOS
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                cmd = [
                    chrome_path,
                    f"--remote-debugging-port={self.chrome_port}",
                    f"--proxy-server={self.proxy_url}",
                    "--user-data-dir=./userdata"
                ]
            else:
                self.log(f"不支持的操作系统: {system}", "ERROR")
                return False

            # 启动Chrome浏览器
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log("Chrome浏览器启动成功，等待连接...")
            time.sleep(3)
            return True

        except Exception as e:
            self.log(f"启动Chrome失败: {e}", "ERROR")
            return False

    def check_mcp_connection(self) -> bool:
        """检查MCP工具连接状态"""
        try:
            pages = mcp__chrome-devtools__list_pages()
            self.log(f"MCP工具已连接，当前页面数量: {len(pages)}")
            return True
        except Exception as e:
            self.log(f"MCP工具连接失败: {e}", "ERROR")
            return False

    def start_api_service(self) -> bool:
        """启动API服务"""
        try:
            # 检查API服务是否已经运行
            response = requests.get(f"{self.api_base_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.log("API服务已在运行")
                return True
        except:
            pass

        try:
            self.log("启动API服务...")
            # 启动API服务
            subprocess.Popen(
                ["uv", "run", "python", "essay_manager.py"],
                cwd="src",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 等待API服务启动
            for i in range(10):
                time.sleep(2)
                try:
                    response = requests.get(f"{self.api_base_url}/api/health", timeout=5)
                    if response.status_code == 200:
                        self.log("API服务启动成功")
                        return True
                except:
                    continue

            self.log("API服务启动失败", "ERROR")
            return False

        except Exception as e:
            self.log(f"启动API服务异常: {e}", "ERROR")
            return False

    def validate_data_format(self, data: Dict[str, Any]) -> bool:
        """验证数据格式是否符合API要求"""
        required_fields = ["title", "url"]

        if "essays" not in data:
            self.log("数据验证失败: 缺少 'essays' 字段", "ERROR")
            return False

        for idx, item in enumerate(data.get("essays", [])):
            # 检查必需字段
            for field in required_fields:
                if field not in item or not item[field]:
                    self.log(f"数据验证失败: 第{idx+1}项缺少必需字段 '{field}'", "ERROR")
                    return False

            # 检查URL格式
            if not item["url"].startswith("http"):
                self.log(f"数据验证失败: 第{idx+1}项URL格式不正确 - {item['url']}", "ERROR")
                return False

        self.log(f"数据格式验证通过，共 {len(data['essays'])} 项")
        return True

    def send_to_api(self, data: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """发送数据到API，包含重试机制"""
        if not self.validate_data_format(data):
            return {"success": False, "error": "数据格式验证失败"}

        for attempt in range(max_retries):
            try:
                self.log(f"尝试发送数据到API (第{attempt + 1}次)")

                response = requests.post(
                    f"{self.api_base_url}/api/essays",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    self.log(f"API调用成功: 成功写入 {result.get('success_count', 0)} 篇文章")

                    # 保存API响应
                    response_file = f"{self.output_dir}/data/api_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(response_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                    return result
                else:
                    self.log(f"API调用失败: {response.status_code} - {response.text}", "WARNING")

            except Exception as e:
                self.log(f"API调用异常: {e} (第{attempt + 1}次)", "ERROR")

            if attempt < max_retries - 1:
                self.log(f"等待5秒后重试...")
                time.sleep(5)

        return {"success": False, "error": f"经过{max_retries}次尝试后仍然失败"}


def extract_x_tweets(username: str, count: int = 5) -> Dict[str, Any]:
    """
    提取X/Twitter推文的完整函数

    Args:
        username: 用户名
        count: 提取数量

    Returns:
        Dict: 执行结果
    """
    manager = CrawlManager()

    try:
        manager.log(f"开始提取 @{username} 的推文，目标数量: {count}")

        # 1. 启动Chrome浏览器
        if not manager.start_chrome_browser():
            return {"success": False, "error": "无法启动Chrome浏览器"}

        # 2. 检查MCP连接
        if not manager.check_mcp_connection():
            return {"success": False, "error": "MCP工具连接失败"}

        # 3. 启动API服务
        if not manager.start_api_service():
            return {"success": False, "error": "API服务启动失败"}

        # 4. 导航到用户页面
        manager.log(f"导航到 @{username} 的用户页面")
        mcp__chrome-devtools__new_page(url=f"https://x.com/{username}", timeout=15000)
        time.sleep(5)

        # 5. 提取推文内容
        manager.log("开始提取推文内容...")
        tweets_data = mcp__chrome-devtools__evaluate_script(function=f"""
            () => {{
                const tweets = [];
                const tweetElements = document.querySelectorAll('article');
                const maxTweets = Math.min({count}, tweetElements.length);

                console.log(`找到 ${{tweetElements.length}} 个推文元素，将提取前 ${{maxTweets}} 个`);

                for (let i = 0; i < maxTweets; i++) {{
                    const tweet = tweetElements[i];

                    try {{
                        // 提取推文文本
                        const textElement = tweet.querySelector('[data-testid="tweetText"]');
                        const tweetText = textElement ? textElement.innerText.trim() : '';

                        // 提取时间链接
                        const timeLink = tweet.querySelector('a[href*="/status/"]');

                        if (timeLink && tweetText && tweetText.length > 10) {{
                            const tweetUrl = timeLink.href;
                            const timeElement = timeLink.querySelector('time');
                            const timestamp = timeElement ? timeElement.getAttribute('datetime') || timeElement.innerText : '';

                            tweets.push({{
                                title: tweetText.length > 50 ? tweetText.substring(0, 50) + '...' : tweetText,
                                subtitle: '@{username}的推文 - ' + (timestamp || new Date().toISOString()),
                                author: '{username}',
                                url: tweetUrl,
                                content: tweetText,
                                entry_time: new Date().toISOString().slice(0, 19).replace('T', ' ')
                            }});
                        }}
                    }} catch (e) {{
                        console.log(`处理第${{i+1}}条推文时出错:`, e);
                    }}
                }}

                return {{
                    success: true,
                    tweets: tweets,
                    totalFound: tweetElements.length
                }};
            }}
        """)

        if not tweets_data.get('success'):
            return {"success": False, "error": "推文提取失败"}

        tweets = tweets_data.get('tweets', [])
        manager.log(f"成功提取 {len(tweets)} 条推文")

        # 6. 保存原始数据
        raw_data_file = f"{manager.output_dir}/data/{username}_tweets_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(raw_data_file, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, ensure_ascii=False, indent=2)
        manager.log(f"原始数据已保存到: {raw_data_file}")

        # 7. 准备API数据
        api_data = {"essays": tweets}

        # 8. 发送到API
        result = manager.send_to_api(api_data)

        # 9. 返回最终结果
        final_result = {
            "success": result.get('success', False),
            "username": username,
            "tweets_extracted": len(tweets),
            "tweets_written": result.get('success_count', 0),
            "files": {
                "raw_data": raw_data_file
            },
            "api_response": result,
            "message": f"成功提取 {len(tweets)} 条推文，写入 {result.get('success_count', 0)} 条到数据库"
        }

        manager.log(f"任务完成: {final_result['message']}")
        return final_result

    except Exception as e:
        error_msg = f"执行过程中出错: {e}"
        manager.log(error_msg, "ERROR")
        return {"success": False, "error": error_msg}


# 工具函数
def validate_url(url: str) -> bool:
    """验证URL格式"""
    return url.startswith(('http://', 'https://'))

def save_data(data: Any, filename_prefix: str, output_dir: str = "output") -> str:
    """保存数据到文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/{filename_prefix}_{timestamp}.json"

    os.makedirs(output_dir, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"数据已保存到: {filename}")
    return filename

def check_environment() -> bool:
    """检查运行环境"""
    try:
        # 检查Chrome是否可访问
        response = requests.get("http://127.0.0.1:9222", timeout=2)
        chrome_available = True
    except:
        chrome_available = False

    try:
        # 检查API服务是否可访问
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        api_available = response.status_code == 200
    except:
        api_available = False

    return chrome_available and api_available


# 批量处理函数
def batch_extract_tweets(usernames: List[str], count: int = 5) -> Dict[str, Any]:
    """批量提取多个用户的推文"""
    results = {}
    successful_users = []
    failed_users = []

    for username in usernames:
        try:
            result = extract_x_tweets(username, count)
            results[username] = result

            if result.get('success'):
                successful_users.append(username)
            else:
                failed_users.append(username)

            # 用户间延迟，避免请求过快
            time.sleep(2)

        except Exception as e:
            failed_users.append(username)
            results[username] = {"success": False, "error": str(e)}

    summary = {
        "total_users": len(usernames),
        "successful": len(successful_users),
        "failed": len(failed_users),
        "successful_users": successful_users,
        "failed_users": failed_users,
        "results": results
    }

    return summary


# 使用示例
if __name__ == "__main__":
    # 示例：提取Elon Musk的推文
    result = extract_x_tweets("elonmusk", 5)
    print("执行结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))