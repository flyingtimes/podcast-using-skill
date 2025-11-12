---
name: crawl
description: 根据用户需求，使用基于chrome-devtools 工具的方式来从浏览器中获取用户需要的内容，支持文章内容提取和批量处理
allowed-tools: Read, Grep, Glob, Write, Search, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__list_pages, mcp__chrome-devtools__new_page, mcp__chrome-devtools__click, mcp__chrome-devtools__fill, mcp__chrome-devtools__wait_for, Bash, Task
---

# crawl

## Reference
请先参考学习[how-to-crawl-with-chrome-dev-mcp.md](how-to-crawl-with-chrome-dev-mcp.md)

## Instructions
1、使用python脚本程序，先判断当前是在macos还是windows环境
2、则根据当前的操作系统环境，开启新浏览器实例
3、检查mcp工具chrome-devtools是否就绪，如果还未就绪请重新连接mcp工具。请注意项目级的mcp配置中的配置应该是这样的：
```
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
```
4、你只能使用chrome-devtols来获取浏览器中的信息，请调用mcp工具完成用户给出的任务

## 核心功能

### 1. 文章内容提取
使用集成的文章内容提取器，支持以下网站：
- **The Atlantic** (theatlantic.com)
- **Medium** (medium.com)

**使用方法：**
```python
# 导入文章内容提取器
import sys
sys.path.append('C:\\Users\\13802\\code\\podcast-using-skill\\src')
from content_extractor import extract_content_from_url, batch_extract_content

# 提取单个文章
def extract_single_article(url):
    """提取单个文章内容"""
    result = extract_content_from_url(url)
    if result['success']:
        return {
            'title': result['title'],
            'content': result['content'],
            'site_type': result['site_type'],
            'url': url
        }
    else:
        return {'error': result.get('error', '提取失败')}

# 批量提取文章
def extract_multiple_articles(urls):
    """批量提取多个文章内容"""
    results = batch_extract_content(urls)
    return [result for result in results if result['success']]
```

### 2. 网页爬取和数据收集
- 使用Chrome DevTools导航到指定页面
- 提取页面内容、表单数据、链接等
- 支持表单填写和交互操作

**使用方法：**
```python
# 基本爬取流程
def crawl_website(url):
    """基本网页爬取"""
    # 1. 导航到页面
    mcp__chrome-devtools__navigate_page(
        type="url",
        url=url,
        ignoreCache=False,
        timeout=10000
    )

    # 2. 获取页面快照
    mcp__chrome-devtools__take_snapshot(
        verbose=True,
        filePath="page_snapshot.txt"
    )

    # 3. 提取内容
    content = mcp__chrome-devtools__evaluate_script(function="""
        () => {
            const title = document.title;
            const paragraphs = Array.from(document.querySelectorAll('p'))
                .map(p => p.textContent.trim())
                .filter(text => text.length > 20)
                .join('\\n\\n');
            return { title, content: paragraphs };
        }
    """)

    return content
```

### 3. 表单交互和自动化
- 自动填写表单
- 点击按钮和链接
- 等待页面加载

**使用方法：**
```python
# 表单填写示例
def fill_form(url, form_data):
    """填写网页表单"""
    # 导航到页面
    mcp__chrome-devtools__navigate_page(type="url", url=url)

    # 等待页面加载
    mcp__chrome-devtools__wait_for(text="表单", timeout=5000)

    # 填写表单字段
    for field_name, value in form_data.items():
        # 查找表单字段
        field_info = mcp__chrome-devtools__evaluate_script(function="""
            (fieldName) => {
                const selectors = [
                    `input[name="${fieldName}"]`,
                    `#${fieldName}`,
                    `[data-field="${fieldName}"]`,
                    `input[placeholder*="${fieldName}"]`
                ];

                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        return {
                            uid: element.uid || 'unknown',
                            tag: element.tagName,
                            type: element.type
                        };
                    }
                }
                return null;
            }
        """, args=[{"uid": field_name}])

        if field_info and field_info.get('uid'):
            mcp__chrome-devtools__fill(uid=field_info['uid'], value=value)

    # 提交表单
    mcp__chrome-devtools__click(uid="submit_button")
```

## 支持的操作类型

### 1. 网站特定操作
- **新闻网站爬取**: 提取文章标题、内容、作者、发布时间
- **电商网站数据收集**: 产品信息、价格、评论
- **社交媒体**: 帖子内容、用户信息、互动数据
- **学术网站**: 论文标题、摘要、作者信息

### 2. 数据导出
- JSON格式导出
- CSV格式导出
- 文本文件导出
- 数据库存储（集成现有API）

## 使用示例

### 示例1: 提取The Atlantic文章
```python
def extract_atlantic_article():
    """提取The Atlantic文章"""
    url = "https://www.theatlantic.com/newsletters/2025/11/baseball-gambling-charges-mlb-cleveland-guardians/684896/"

    # 使用内容提取器
    result = extract_content_from_url(url)

    if result['success']:
        print(f"标题: {result['title']}")
        print(f"网站类型: {result['site_type']}")
        print(f"内容长度: {len(result['content'])} 字符")

        # 保存到文件
        with open('atlantic_article.txt', 'w', encoding='utf-8') as f:
            f.write(f"标题: {result['title']}\\n\\n")
            f.write(result['content'])

        return result
    else:
        print(f"提取失败: {result['error']}")
        return None
```

### 示例2: 批量处理Medium文章
```python
def batch_process_medium_articles():
    """批量处理Medium文章"""
    urls = [
        "https://medium.com/@username/article1",
        "https://medium.com/@username/article2",
        "https://medium.com/@username/article3"
    ]

    # 批量提取
    results = batch_extract_content(urls)

    successful_extractions = [r for r in results if r['success']]

    print(f"成功提取: {len(successful_extractions)}/{len(urls)} 篇")

    # 保存结果
    for result in successful_extractions:
        filename = f"medium_{result['title'][:20].replace(' ', '_')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"标题: {result['title']}\\n")
            f.write(f"URL: {result['url']}\\n")
            f.write(f"网站: {result['site_type']}\\n\\n")
            f.write(result['content'])

    return successful_extractions
```

### 示例3: 与数据库集成
```python
def extract_and_store_to_database(urls):
    """提取文章并存储到数据库"""
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
                "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    # 发送到API
    import requests
    response = requests.post(
        "http://localhost:8000/api/essays",
        json=api_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        api_result = response.json()
        print(f"成功存储 {api_result['success_count']} 篇文章")
        return api_result
    else:
        print(f"存储失败: {response.status_code}")
        return None
```

## 错误处理

### 常见错误和解决方案
1. **网络连接超时**: 增加timeout时间或重试
2. **Chrome DevTools未就绪**: 检查.mcp.json配置和浏览器启动
3. **页面加载失败**: 检查URL有效性和网络连接
4. **内容提取失败**: 验证网站结构是否有变化

### 错误处理模板
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
```

## 性能优化

### 1. 批量处理优化
- 使用适当的延迟避免请求过快
- 并行处理多个URL（在合理范围内）
- 缓存重复请求的结果

### 2. 内存管理
- 及时清理大型数据结构
- 分批处理大量数据
- 监控内存使用情况

## 扩展功能

### 添加新网站支持
要支持新网站，需要：
1. 在`src/content_extractor.py`中添加网站检测逻辑
2. 实现专用内容提取方法
3. 测试并验证提取效果

### 自定义数据处理
- 实现特定的数据清洗逻辑
- 添加数据格式转换功能
- 集成第三方数据处理工具

## 注意事项

1. **合法合规**: 确保爬取行为符合网站的使用条款
2. **请求频率**: 避免过于频繁的请求导致被限制
3. **数据质量**: 验证提取的数据准确性和完整性
4. **错误处理**: 妥善处理各种异常情况
5. **资源管理**: 及时释放浏览器资源

## 更新日志

- **v1.0**: 基础Chrome DevTools爬取功能
- **v1.1**: 集成文章内容提取器
- **v1.2**: 添加The Atlantic和Medium网站专门支持
- **v1.3**: 增强批量处理和数据库集成功能
