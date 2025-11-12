# 📋 Crawl 技能最佳实践指南

## 🎯 目录

| 实践 | 描述 | 重要性 |
|------|------|--------|
| [环境配置](#环境配置最佳实践) | 开发环境设置 | ⭐⭐⭐⭐⭐ |
| [性能优化](#性能优化指南) | 提升执行效率 | ⭐⭐⭐⭐ |
| [错误处理](#错误处理策略) | 健壮性保障 | ⭐⭐⭐⭐⭐ |
| [数据质量](#数据质量管理) | 确保数据准确性 | ⭐⭐⭐⭐ |
| [安全合规](#安全与合规) | 合法合规使用 | ⭐⭐⭐⭐⭐ |

---

## 🔧 环境配置最佳实践

### 1. 系统要求检查
```python
def check_system_requirements():
    """检查系统要求"""
    import platform
    import subprocess
    import os

    requirements = {
        "python_version": "3.8+",
        "chrome_installed": False,
        "uv_installed": False,
        "disk_space": "1GB+"
    }

    # 检查Python版本
    python_version = platform.python_version()
    print(f"Python版本: {python_version}")

    # 检查Chrome安装
    system = platform.system()
    if system == "Windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                requirements["chrome_installed"] = True
                break
    elif system == "Darwin":
        if os.path.exists("/Applications/Google Chrome.app"):
            requirements["chrome_installed"] = True

    # 检查uv安装
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        requirements["uv_installed"] = True
    except:
        pass

    return requirements

# 使用示例
requirements = check_system_requirements()
print("系统要求检查结果:", requirements)
```

### 2. 配置文件管理
```python
# config.py - 推荐的配置结构
DEFAULT_CONFIG = {
    # Chrome配置
    "chrome": {
        "port": 9222,
        "proxy_url": "http://127.0.0.1:1087",
        "user_data_dir": "./userdata",
        "headless": False,
        "window_size": "1920,1080"
    },

    # API配置
    "api": {
        "base_url": "http://localhost:8000",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 5
    },

    # 输出配置
    "output": {
        "base_dir": "output",
        "log_level": "INFO",
        "save_snapshots": True,
        "compress_data": False
    },

    # 爬取配置
    "crawl": {
        "default_count": 5,
        "request_delay": 2,
        "page_load_timeout": 15,
        "element_wait_timeout": 10
    }
}

def load_config(custom_config: dict = None):
    """加载配置"""
    config = DEFAULT_CONFIG.copy()

    if custom_config:
        # 深度合并配置
        for section, values in custom_config.items():
            if section in config:
                config[section].update(values)
            else:
                config[section] = values

    return config
```

### 3. 环境变量配置
```bash
# .env 文件示例
CHROME_PORT=9222
PROXY_URL=http://127.0.0.1:1087
API_BASE_URL=http://localhost:8000
LOG_LEVEL=INFO
OUTPUT_DIR=output
```

```python
# 环境变量加载
import os
from dotenv import load_dotenv

load_dotenv()

ENV_CONFIG = {
    "chrome": {
        "port": int(os.getenv("CHROME_PORT", 9222)),
        "proxy_url": os.getenv("PROXY_URL", "http://127.0.0.1:1087")
    },
    "api": {
        "base_url": os.getenv("API_BASE_URL", "http://localhost:8000"),
        "timeout": int(os.getenv("API_TIMEOUT", 30))
    }
}
```

---

## ⚡ 性能优化指南

### 1. 并发处理
```python
import concurrent.futures
import threading
from queue import Queue

class ConcurrentCrawler:
    """并发爬虫"""

    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.results = []

    def crawl_user(self, username: str, count: int = 5):
        """爬取单个用户"""
        try:
            result = extract_x_tweets(username, count)
            return {"username": username, "result": result}
        except Exception as e:
            return {"username": username, "error": str(e)}

    def crawl_multiple_users(self, usernames: list, count: int = 5):
        """并发爬取多个用户"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            futures = [
                executor.submit(self.crawl_user, username, count)
                for username in usernames
            ]

            # 收集结果
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                self.results.append(result)

        return self.results

# 使用示例
crawler = ConcurrentCrawler(max_workers=3)
usernames = ["elonmusk", "sundarpichai", "satyanadella", "tim_cook", "satyanadella"]
results = crawler.crawl_multiple_users(usernames, 3)

for result in results:
    if "error" not in result:
        print(f"{result['username']}: {result['result'].get('tweets_extracted', 0)} 条推文")
    else:
        print(f"{result['username']}: 爬取失败 - {result['error']}")
```

### 2. 缓存机制
```python
import pickle
import hashlib
from datetime import datetime, timedelta

class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: str = "output/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_duration = timedelta(hours=1)  # 缓存1小时

    def _get_cache_key(self, username: str, count: int) -> str:
        """生成缓存键"""
        key = f"{username}_{count}_{datetime.now().strftime('%Y%m%d_%H')}"
        return hashlib.md5(key.encode()).hexdigest()

    def _is_cache_valid(self, cache_file: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_file):
            return False

        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - file_time < self.cache_duration

    def get_cached_result(self, username: str, count: int):
        """获取缓存结果"""
        cache_key = self._get_cache_key(username, count)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        if self._is_cache_valid(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        return None

    def save_result(self, username: str, count: int, result):
        """保存结果到缓存"""
        cache_key = self._get_cache_key(username, count)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

# 使用示例
def extract_with_cache(username: str, count: int = 5):
    """带缓存的推文提取"""
    cache = CacheManager()

    # 尝试从缓存获取
    cached_result = cache.get_cached_result(username, count)
    if cached_result:
        print(f"从缓存获取 {username} 的推文")
        return cached_result

    # 缓存未命中，执行爬取
    print(f"爬取 {username} 的推文...")
    result = extract_x_tweets(username, count)

    # 保存到缓存
    cache.save_result(username, count, result)

    return result
```

### 3. 批量处理优化
```python
def batch_process_optimized(items: list, batch_size: int = 10, delay: float = 1.0):
    """优化的批量处理"""
    results = []
    total_items = len(items)

    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]
        print(f"处理批次 {i//batch_size + 1}/{(total_items-1)//batch_size + 1}")

        batch_results = []
        for item in batch:
            try:
                result = extract_x_tweets(item, 3)
                batch_results.append({"item": item, "result": result})
            except Exception as e:
                batch_results.append({"item": item, "error": str(e)})

        results.extend(batch_results)

        # 批次间延迟
        if i + batch_size < total_items:
            time.sleep(delay)

    return results
```

---

## 🛡️ 错误处理策略

### 1. 分层错误处理
```python
class CrawlError(Exception):
    """爬虫基础异常"""
    pass

class ChromeError(CrawlError):
    """Chrome相关错误"""
    pass

class APIError(CrawlError):
    """API相关错误"""
    pass

class DataValidationError(CrawlError):
    """数据验证错误"""
    pass

def robust_extract_tweets(username: str, count: int = 5, max_retries: int = 3):
    """健壮的推文提取"""
    for attempt in range(max_retries):
        try:
            # 1. 环境检查
            if not check_environment():
                raise ChromeError("环境检查失败")

            # 2. 数据提取
            result = extract_x_tweets(username, count)

            # 3. 数据验证
            if not validate_result(result):
                raise DataValidationError("数据验证失败")

            return result

        except ChromeError as e:
            print(f"Chrome错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                restart_chrome()
                time.sleep(5)

        except APIError as e:
            print(f"API错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                restart_api_service()
                time.sleep(10)

        except Exception as e:
            print(f"未知错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(10)

    raise CrawlError(f"经过 {max_retries} 次尝试后仍然失败")

def validate_result(result: dict) -> bool:
    """验证结果有效性"""
    if not isinstance(result, dict):
        return False

    if 'success' not in result:
        return False

    if result.get('success') and 'tweets_extracted' in result:
        return result['tweets_extracted'] > 0

    return False
```

### 2. 监控和告警
```python
import logging
from dataclasses import dataclass
from typing import List

@dataclass
class CrawlMetrics:
    """爬虫指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tweets: int = 0
    average_response_time: float = 0.0
    error_rate: float = 0.0

class CrawlMonitor:
    """爬虫监控"""

    def __init__(self):
        self.metrics = CrawlMetrics()
        self.response_times = []

    def record_request(self, success: bool, response_time: float, tweets_count: int = 0):
        """记录请求"""
        self.metrics.total_requests += 1
        self.response_times.append(response_time)

        if success:
            self.metrics.successful_requests += 1
            self.metrics.total_tweets += tweets_count
        else:
            self.metrics.failed_requests += 1

        # 更新指标
        self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests
        self.metrics.average_response_time = sum(self.response_times) / len(self.response_times)

    def check_health(self) -> bool:
        """健康检查"""
        if self.metrics.error_rate > 0.5:  # 错误率超过50%
            return False

        if self.metrics.average_response_time > 60:  # 平均响应时间超过60秒
            return False

        return True

    def get_status_report(self) -> str:
        """获取状态报告"""
        return f"""
爬虫状态报告:
- 总请求数: {self.metrics.total_requests}
- 成功请求数: {self.metrics.successful_requests}
- 失败请求数: {self.metrics.failed_requests}
- 错误率: {self.metrics.error_rate:.2%}
- 平均响应时间: {self.metrics.average_response_time:.2f}秒
- 总推文数: {self.metrics.total_tweets}
- 健康状态: {'正常' if self.check_health() else '异常'}
"""

# 全局监控器
monitor = CrawlMonitor()

def monitored_extract_tweets(username: str, count: int = 5):
    """带监控的推文提取"""
    start_time = time.time()

    try:
        result = extract_x_tweets(username, count)
        response_time = time.time() - start_time

        success = result.get('success', False)
        tweets_count = result.get('tweets_extracted', 0)

        monitor.record_request(success, response_time, tweets_count)

        # 健康检查告警
        if not monitor.check_health():
            logging.warning("爬虫健康状态异常")

        return result

    except Exception as e:
        response_time = time.time() - start_time
        monitor.record_request(False, response_time)

        logging.error(f"推文提取失败: {e}")
        raise
```

---

## 📊 数据质量管理

### 1. 数据验证框架
```python
from pydantic import BaseModel, validator
from typing import Optional, List

class TweetData(BaseModel):
    """推文数据模型"""
    title: str
    subtitle: Optional[str] = None
    author: str
    url: str
    content: str
    entry_time: str

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('标题不能为空')
        if len(v) > 500:
            raise ValueError('标题长度不能超过500字符')
        return v.strip()

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL必须以http://或https://开头')
        return v

    @validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('内容不能为空')
        if len(v) < 10:
            raise ValueError('内容长度不能少于10字符')
        return v.strip()

class CrawlResult(BaseModel):
    """爬取结果模型"""
    success: bool
    username: str
    tweets_extracted: int
    tweets_written: int
    files: dict
    api_response: dict
    message: str

def validate_tweet_data(data: dict) -> TweetData:
    """验证推文数据"""
    try:
        return TweetData(**data)
    except Exception as e:
        raise DataValidationError(f"数据验证失败: {e}")

def validate_api_response(response: dict) -> bool:
    """验证API响应"""
    required_fields = ['success_count', 'skipped_count', 'successful_titles']

    for field in required_fields:
        if field not in response:
            return False

    return response['success_count'] >= 0
```

### 2. 数据清洗
```python
import re
from html import unescape

class DataCleaner:
    """数据清洗器"""

    @staticmethod
    def clean_text(text: str) -> str:
        """清洗文本"""
        if not text:
            return ""

        # HTML解码
        text = unescape(text)

        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)

        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\-"\']', '', text)

        # 去除首尾空白
        text = text.strip()

        return text

    @staticmethod
    def clean_url(url: str) -> str:
        """清洗URL"""
        if not url:
            return ""

        # 移除查询参数中的追踪信息
        url = re.sub(r'[?&](utm_|ref|source|fbclid)=[^&]*', '', url)

        # 移除末尾的#
        url = url.split('#')[0]

        return url

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """提取标签"""
        return re.findall(r'#\w+', text)

    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """提取提及"""
        return re.findall(r'@\w+', text)

def clean_tweet_data(tweet_data: dict) -> dict:
    """清洗推文数据"""
    cleaner = DataCleaner()

    cleaned_data = tweet_data.copy()

    # 清洗文本字段
    if 'title' in cleaned_data:
        cleaned_data['title'] = cleaner.clean_text(cleaned_data['title'])

    if 'content' in cleaned_data:
        cleaned_data['content'] = cleaner.clean_text(cleaned_data['content'])

        # 提取标签和提及
        cleaned_data['hashtags'] = cleaner.extract_hashtags(cleaned_data['content'])
        cleaned_data['mentions'] = cleaner.extract_mentions(cleaned_data['content'])

    # 清洗URL
    if 'url' in cleaned_data:
        cleaned_data['url'] = cleaner.clean_url(cleaned_data['url'])

    return cleaned_data
```

### 3. 数据去重
```python
class DataDeduplicator:
    """数据去重器"""

    def __init__(self):
        self.seen_urls = set()
        self.seen_titles = set()

    def is_duplicate_by_url(self, url: str) -> bool:
        """基于URL判断重复"""
        return url in self.seen_urls

    def is_duplicate_by_title(self, title: str) -> bool:
        """基于标题判断重复"""
        return title in self.seen_titles

    def add_to_seen(self, url: str, title: str):
        """添加到已见记录"""
        self.seen_urls.add(url)
        self.seen_titles.add(title)

    def filter_duplicates(self, items: List[dict]) -> List[dict]:
        """过滤重复项"""
        filtered_items = []

        for item in items:
            url = item.get('url', '')
            title = item.get('title', '')

            if not self.is_duplicate_by_url(url) and not self.is_duplicate_by_title(title):
                filtered_items.append(item)
                self.add_to_seen(url, title)
            else:
                print(f"跳过重复项: {title[:50]}...")

        return filtered_items

# 使用示例
deduplicator = DataDeduplicator()

# 假设这是从API获取的数据
raw_data = {"essays": [...]}

# 过滤重复项
unique_tweets = deduplicator.filter_duplicates(raw_data["essays"])
print(f"去重后: {len(unique_tweets)} 条唯一推文")
```

---

## 🛡️ 安全与合规

### 1. 请求频率控制
```python
import time
import random
from threading import Lock

class RateLimiter:
    """请求频率限制器"""

    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
        self.lock = Lock()

    def wait(self):
        """等待直到可以发起下一个请求"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                # 添加随机抖动
                sleep_time += random.uniform(0, sleep_time * 0.1)
                time.sleep(sleep_time)

            self.last_request_time = time.time()

# 全局频率限制器
rate_limiter = RateLimiter(requests_per_second=0.5)  # 每2秒最多1次请求

def rate_limited_extract_tweets(username: str, count: int = 5):
    """频率限制的推文提取"""
    rate_limiter.wait()
    return extract_x_tweets(username, count)
```

### 2. User-Agent轮换
```python
class UserAgentRotator:
    """User-Agent轮换器"""

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        self.current_index = 0

    def get_user_agent(self) -> str:
        """获取下一个User-Agent"""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent

user_agent_rotator = UserAgentRotator()
```

### 3. 数据隐私保护
```python
import hashlib
import re

class PrivacyProtector:
    """隐私保护器"""

    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """哈希敏感数据"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    @staticmethod
    def mask_email(text: str) -> str:
        """遮蔽邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, lambda m: m.group()[0] + '***@' + m.group().split('@')[1], text)

    @staticmethod
    def mask_phone(text: str) -> str:
        """遮蔽电话号码"""
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        return re.sub(phone_pattern, lambda m: m.group()[:3] + '-***-' + m.group()[-4:], text)

    @staticmethod
    def anonymize_content(content: str) -> str:
        """匿名化内容"""
        content = PrivacyProtector.mask_email(content)
        content = PrivacyProtector.mask_phone(content)
        return content

def anonymize_tweet_data(tweet_data: dict) -> dict:
    """匿名化推文数据"""
    anonymized = tweet_data.copy()

    if 'content' in anonymized:
        anonymized['content'] = PrivacyProtector.anonymize_content(anonymized['content'])

    return anonymized
```

### 4. 合规检查清单
```python
def compliance_check(url: str, content: str) -> dict:
    """合规检查"""
    issues = []

    # 检查是否包含版权信息
    if '©' in content or 'copyright' in content.lower():
        issues.append("包含版权信息")

    # 检查是否包含个人隐私信息
    if re.search(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', content):  # 信用卡号
        issues.append("可能包含信用卡号")

    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', content):  # 社会保险号
        issues.append("可能包含社会保险号")

    # 检查robots.txt（这里简化处理）
    if 'private' in url.lower() or 'admin' in url.lower():
        issues.append("访问私有页面")

    return {
        "compliant": len(issues) == 0,
        "issues": issues
    }

def is_crawling_allowed(url: str) -> bool:
    """检查是否允许爬取"""
    # 简化的实现，实际应该检查robots.txt
    blocked_domains = ['mail.google.com', 'facebook.com/messages']

    for domain in blocked_domains:
        if domain in url:
            return False

    return True
```

---

## 📈 性能监控和优化

### 1. 性能指标收集
```python
import psutil
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PerformanceMetrics:
    """性能指标"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, int]
    execution_time: float
    success_rate: float

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.start_time = None
        self.metrics_history: List[PerformanceMetrics] = []

    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()

    def collect_metrics(self, success_count: int, total_count: int) -> PerformanceMetrics:
        """收集性能指标"""
        # 系统资源使用情况
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        # 网络IO
        network_io = psutil.net_io_counters()._asdict()

        # 执行时间和成功率
        execution_time = time.time() - self.start_time if self.start_time else 0
        success_rate = success_count / total_count if total_count > 0 else 0

        metrics = PerformanceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage=disk_usage,
            network_io=network_io,
            execution_time=execution_time,
            success_rate=success_rate
        )

        self.metrics_history.append(metrics)
        return metrics

    def get_performance_report(self) -> str:
        """获取性能报告"""
        if not self.metrics_history:
            return "暂无性能数据"

        latest = self.metrics_history[-1]
        avg_cpu = sum(m.cpu_percent for m in self.metrics_history) / len(self.metrics_history)
        avg_memory = sum(m.memory_percent for m in self.metrics_history) / len(self.metrics_history)

        return f"""
性能报告:
- CPU使用率: {latest.cpu_percent:.1f}% (平均: {avg_cpu:.1f}%)
- 内存使用率: {latest.memory_percent:.1f}% (平均: {avg_memory:.1f}%)
- 磁盘使用率: {latest.disk_usage:.1f}%
- 执行时间: {latest.execution_time:.2f}秒
- 成功率: {latest.success_rate:.2%}
"""

# 使用示例
perf_monitor = PerformanceMonitor()
perf_monitor.start_monitoring()

# 执行爬取任务...
# result = extract_x_tweets("elonmusk", 5)

# 收集性能指标
# metrics = perf_monitor.collect_metrics(
#     success_count=result.get('tweets_written', 0),
#     total_count=result.get('tweets_extracted', 0)
# )
# print(perf_monitor.get_performance_report())
```

---

## 🎯 最佳实践总结

### ✅ 推荐做法
1. **使用改进版管理器** - 包含完整的错误处理和日志记录
2. **启用缓存机制** - 避免重复请求，提高效率
3. **控制请求频率** - 避免被网站限制
4. **验证数据格式** - 确保数据质量
5. **监控性能指标** - 及时发现问题
6. **保护用户隐私** - 匿名化敏感信息
7. **遵守robots.txt** - 合法合规爬取

### ❌ 避免做法
1. **忽略错误处理** - 导致程序崩溃
2. **过度频繁请求** - 可能被IP封禁
3. **保存原始敏感数据** - 隐私泄露风险
4. **忽略资源限制** - 可能导致系统崩溃
5. **不验证数据格式** - 导致API写入失败

### 📋 检查清单
在部署爬虫任务前，请确认：

- [ ] 环境配置正确
- [ ] 错误处理完善
- [ ] 请求频率合理
- [ ] 数据验证有效
- [ ] 日志记录完整
- [ ] 性能监控启用
- [ ] 隐私保护到位
- [ ] 合规检查通过

---

## 📚 更多资源

- [完整示例](EXAMPLES.md)
- [快速启动](QUICK_START.md)
- [核心管理器](crawl_manager.py)