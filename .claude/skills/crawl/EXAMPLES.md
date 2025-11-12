# 📚 Crawl 技能使用示例

## 🎯 示例目录

| 示例 | 描述 | 复杂度 |
|------|------|--------|
| [示例1](#示例1-提取xtwitter推文) | 提取X/Twitter推文 | ⭐⭐ |
| [示例2](#示例2-提取the-atlantic文章) | 提取The Atlantic文章 | ⭐ |
| [示例3](#示例3-批量处理medium文章) | 批量处理Medium文章 | ⭐⭐⭐ |
| [示例4](#示例4-与数据库集成) | 与数据库集成 | ⭐⭐⭐ |
| [示例5](#示例5-自定义爬虫) | 自定义爬虫 | ⭐⭐⭐⭐ |

---

## 示例1: 提取X/Twitter推文

### 基础版本
```python
from .crawl_manager import extract_x_tweets

# 提取Elon Musk的最新5篇推文
result = extract_x_tweets("elonmusk", 5)
print(result)
```

### 高级版本（自定义配置）
```python
from .crawl_manager import ImprovedCrawlManager

# 自定义配置
config = {
    "output_dir": "output",
    "api_base_url": "http://localhost:8000",
    "max_retries": 5,
    "timeout": 60
}

manager = ImprovedCrawlManager(config)

# 提取多个用户的推文
users = ["elonmusk", "sundarpichai", "satyanadella"]
results = {}

for user in users:
    try:
        result = extract_x_tweets(user, 3, config)
        results[user] = result
        print(f"{user}: {result.get('tweets_extracted', 0)} 条推文")
    except Exception as e:
        print(f"{user} 提取失败: {e}")
```

### 手动版本（完整控制）
```python
import os
import platform
import subprocess
import time
import json
import requests
from datetime import datetime

def manual_extract_tweets(username: str, count: int = 5):
    """手动提取推文的完整流程"""

    # 1. 创建输出目录
    os.makedirs('output', exist_ok=True)

    # 2. 启动Chrome浏览器
    system = platform.system()
    if system == "Windows":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        cmd = [chrome_path, "--remote-debugging-port=9222",
               "--proxy-server=http://127.0.0.1:1087"]
    elif system == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        cmd = [chrome_path, "--remote-debugging-port=9222",
               "--proxy-server=http://127.0.0.1:1087"]

    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)

    # 3. 启动API服务
    try:
        requests.get("http://localhost:8000/api/health", timeout=5)
    except:
        subprocess.Popen(["uv", "run", "python", "essay_manager.py"],
                         cwd="src")
        time.sleep(5)

    # 4. 使用MCP工具提取
    mcp__chrome-devtools__new_page(url=f"https://x.com/{username}", timeout=15000)
    time.sleep(5)

    # 5. 提取推文
    tweets_data = mcp__chrome-devtools__evaluate_script(function=f"""
        () => {{
            const tweets = [];
            const tweetElements = document.querySelectorAll('article');
            const maxTweets = Math.min({count}, tweetElements.length);

            for (let i = 0; i < maxTweets; i++) {{
                const tweet = tweetElements[i];
                const timeLink = tweet.querySelector('a[href*="/status/"]');

                if (timeLink) {{
                    const tweetUrl = timeLink.href;
                    const textElement = tweet.querySelector('[data-testid="tweetText"]');
                    const tweetText = textElement ? textElement.innerText.trim() : '';

                    if (tweetText && tweetText.length > 10) {{
                        tweets.push({{
                            title: tweetText.length > 50 ? tweetText.substring(0, 50) + '...' : tweetText,
                            subtitle: '@{username}的推文',
                            author: '{username}',
                            url: tweetUrl,
                            content: tweetText,
                            entry_time: new Date().toISOString().slice(0, 19).replace('T', ' ')
                        }});
                    }}
                }}
            }}

            return {{ success: true, tweets: tweets }};
        }}
    """)

    # 6. 发送到API
    api_data = {"essays": tweets_data.get("tweets", [])}
    response = requests.post("http://localhost:8000/api/essays",
                           json=api_data,
                           headers={"Content-Type": "application/json"})

    return response.json()

# 使用示例
result = manual_extract_tweets("elonmusk", 5)
print(result)
```

---

## 示例2: 提取The Atlantic文章

### 基础版本
```python
import sys
import os
sys.path.append('C:\\Users\\13802\\code\\podcast-using-skill\\src')
from content_extractor import extract_content_from_url

def extract_atlantic_article():
    """提取The Atlantic文章"""
    os.makedirs('output', exist_ok=True)

    url = "https://www.theatlantic.com/newsletters/2025/11/baseball-gambling-charges-mlb-cleveland-guardians/684896/"

    # 使用内容提取器
    result = extract_content_from_url(url)

    if result['success']:
        print(f"标题: {result['title']}")
        print(f"网站类型: {result['site_type']}")
        print(f"内容长度: {len(result['content'])} 字符")

        # 保存到output目录
        with open('output/atlantic_article.txt', 'w', encoding='utf-8') as f:
            f.write(f"标题: {result['title']}\\n\\n")
            f.write(result['content'])

        return result
    else:
        print(f"提取失败: {result['error']}")
        return None

# 使用示例
result = extract_atlantic_article()
```

### 高级版本（批量处理）
```python
def batch_extract_atlantic_articles(urls: list):
    """批量提取The Atlantic文章"""
    import sys
    import os
    import json
    import requests
    from datetime import datetime

    sys.path.append('C:\\Users\\13802\\code\\podcast-using-skill\\src')
    from content_extractor import batch_extract_content

    os.makedirs('output', exist_ok=True)

    # 批量提取
    results = batch_extract_content(urls)
    successful_extractions = [r for r in results if r['success']]

    print(f"成功提取: {len(successful_extractions)}/{len(urls)} 篇")

    # 准备API数据
    api_data = {"essays": []}

    for result in successful_extractions:
        api_data["essays"].append({
            "title": result['title'],
            "url": result['url'],
            "content": result['content'],
            "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": "The Atlantic",
            "subtitle": result.get('subtitle', '')
        })

    # 保存原始数据
    with open('output/atlantic_articles_raw.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 发送到API
    try:
        response = requests.post(
            "http://localhost:8000/api/essays",
            json=api_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            api_result = response.json()
            print(f"成功写入 {api_result.get('success_count', 0)} 篇文章")
            return api_result
    except Exception as e:
        print(f"API调用失败: {e}")

    return None

# 使用示例
urls = [
    "https://www.theatlantic.com/newsletters/2025/11/baseball-gambling-charges-mlb-cleveland-guardians/684896/",
    "https://www.theatlantic.com/health/2025/11/supplement-patches-wellness/684893/"
]

result = batch_extract_atlantic_articles(urls)
```

---

## 示例3: 批量处理Medium文章

```python
def batch_process_medium_articles():
    """批量处理Medium文章"""
    import sys
    import os
    import json

    sys.path.append('C:\\Users\\13802\\code\\podcast-using-skill\\src')
    from content_extractor import batch_extract_content

    os.makedirs('output', exist_ok=True)

    urls = [
        "https://medium.com/@username/article1",
        "https://medium.com/@username/article2",
        "https://medium.com/@username/article3"
    ]

    # 批量提取
    results = batch_extract_content(urls)
    successful_extractions = [r for r in results if r['success']]

    print(f"成功提取: {len(successful_extractions)}/{len(urls)} 篇")

    # 保存结果到output目录
    for result in successful_extractions:
        filename = f"output/medium_{result['title'][:20].replace(' ', '_')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"标题: {result['title']}\\n")
            f.write(f"URL: {result['url']}\\n")
            f.write(f"网站: {result['site_type']}\\n\\n")
            f.write(result['content'])

    return successful_extractions

# 使用示例
results = batch_process_medium_articles()
```

---

## 示例4: 与数据库集成

```python
def extract_and_store_to_database(urls):
    """提取文章并存储到数据库"""
    import sys
    import os
    import json
    import requests
    from datetime import datetime

    sys.path.append('C:\\Users\\13802\\code\\podcast-using-skill\\src')
    from content_extractor import batch_extract_content

    os.makedirs('output', exist_ok=True)

    # 批量提取
    results = batch_extract_content(urls)

    # 准备API数据
    api_data = {
        "essays": []
    }

    for result in results:
        if result['success']:
            api_data["essays"].append({
                "title": result['title'],
                "url": result['url'],
                "content": result['content'],
                "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "author": result.get('author', ''),
                "subtitle": result.get('subtitle', '')
            })

    # 保存提取数据到output目录（作为备份）
    with open('output/extracted_articles_data.json', 'w', encoding='utf-8') as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    # 发送到API
    try:
        response = requests.post(
            "http://localhost:8000/api/essays",
            json=api_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            api_result = response.json()
            print(f"成功存储 {api_result.get('success_count', 0)} 篇文章")

            # 保存API响应到output目录
            with open('output/api_response.json', 'w', encoding='utf-8') as f:
                json.dump(api_result, f, ensure_ascii=False, indent=2)

            return api_result
        else:
            print(f"存储失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"发送API请求时出错: {e}")
        return None

# 使用示例
urls = [
    "https://www.theatlantic.com/newsletters/2025/11/baseball-gambling-charges-mlb-cleveland-guardians/684896/",
    "https://medium.com/@username/article1"
]

result = extract_and_store_to_database(urls)
```

---

## 示例5: 自定义爬虫

```python
class CustomCrawler:
    """自定义爬虫类"""

    def __init__(self):
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def crawl_website(self, url: str, selectors: dict):
        """
        通用网站爬取

        Args:
            url: 目标URL
            selectors: CSS选择器字典
                {
                    'title': 'h1.title',
                    'content': 'div.content',
                    'author': 'span.author',
                    'date': 'time.date'
                }
        """
        try:
            # 导航到页面
            mcp__chrome-devtools__navigate_page(
                type="url",
                url=url,
                ignoreCache=False,
                timeout=10000
            )

            # 等待页面加载
            time.sleep(3)

            # 提取数据
            extracted_data = mcp__chrome-devtools__evaluate_script(function=f"""
                (selectors) => {{
                    const data = {{}};

                    for (const [key, selector] of Object.entries(selectors)) {{
                        const element = document.querySelector(selector);
                        if (element) {{
                            data[key] = element.innerText.trim();
                        }}
                    }}

                    return data;
                }}
            """, args=[{"selectors": selectors}])

            # 添加元数据
            extracted_data['url'] = url
            extracted_data['crawl_time'] = datetime.now().isoformat()

            # 保存数据
            filename = f"{self.output_dir}/custom_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)

            print(f"数据已保存到: {filename}")
            return extracted_data

        except Exception as e:
            print(f"爬取失败: {e}")
            return None

# 使用示例
def custom_crawl_example():
    """自定义爬取示例"""
    crawler = CustomCrawler()

    # 定义选择器
    selectors = {
        'title': 'h1',
        'content': 'article p',
        'author': '.author-name',
        'date': 'time'
    }

    # 爬取网站
    result = crawler.crawl_website("https://example-news.com/article/123", selectors)
    print(result)

# 运行示例
custom_crawl_example()
```

---

## 🔧 常用工具函数

```python
def save_data(data, filename_prefix: str):
    """保存数据到文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"output/{filename_prefix}_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"数据已保存到: {filename}")
    return filename

def validate_url(url: str) -> bool:
    """验证URL格式"""
    return url.startswith(('http://', 'https://'))

def wait_for_element(selector: str, timeout: int = 10):
    """等待元素出现"""
    mcp__chrome-devtools__wait_for(
        text=selector,
        timeout=timeout * 1000
    )

def take_page_snapshot(filename: str = None):
    """保存页面快照"""
    if not filename:
        filename = f"page_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    mcp__chrome-devtools__take_snapshot(
        verbose=True,
        filePath=f"output/snapshots/{filename}"
    )
```

## 🚨 错误处理示例

```python
def safe_extract_content(url, max_retries=3):
    """安全的内容提取，包含重试机制"""
    for attempt in range(max_retries):
        try:
            result = extract_content_from_url(url)
            if result['success']:
                return result
            else:
                print(f"尝试 {attempt + 1} 失败: {result.get('error')}")
                time.sleep(2)  # 等待2秒后重试
        except Exception as e:
            print(f"尝试 {attempt + 1} 异常: {e}")
            time.sleep(2)

    return {'success': False, 'error': f'经过 {max_retries} 次尝试后仍然失败'}

# 使用示例
result = safe_extract_content("https://example.com/article")
```

---

## 📚 更多资源

- [最佳实践指南](BEST_PRACTICES.md)
- [快速启动指南](QUICK_START.md)
- [核心管理器代码](crawl_manager.py)