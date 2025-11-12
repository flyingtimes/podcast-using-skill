# 文章内容提取器使用说明

## 概述

这个文章内容提取器专门用于从The Atlantic和Medium网站提取文章内容。支持单个URL提取和批量处理。

## 支持的网站

- **The Atlantic** (theatlantic.com) - 新闻、评论文章
- **Medium** (medium.com) - 博客、技术文章

## 使用方法

### 1. 基本使用

```python
from content_extractor import ArticleContentExtractor

# 创建提取器实例
extractor = ArticleContentExtractor()

# 提取单个文章
result = extractor.extract_article_content("https://www.theatlantic.com/...")

print(f"标题: {result['title']}")
print(f"内容: {result['content']}")
print(f"网站类型: {result['site_type']}")
print(f"是否成功: {result['success']}")
```

### 2. 便利函数

```python
from content_extractor import extract_content_from_url, batch_extract_content

# 提取单个文章
result = extract_content_from_url("https://medium.com/@username/article-id")

# 批量提取文章
urls = [
    "https://www.theatlantic.com/...",
    "https://medium.com/@username/..."
]
results = batch_extract_content(urls)
```

### 3. 从数据库批量提取

```python
from content_extractor import extract_from_database

# 从本地API数据库批量提取
results = extract_from_database("http://localhost:8000/api/essays")
```

### 4. 在skill中使用

```python
# 在skill中直接调用
from content_extractor import extract_content_from_url

def process_article(url):
    result = extract_content_from_url(url)
    if result['success']:
        return result['content']
    else:
        return None
```

## 返回格式

每个提取结果包含以下字段：

```python
{
    'title': '文章标题',
    'content': '文章内容',
    'site_type': 'theatlantic|medium|unknown',
    'url': '原始URL',
    'success': True/False,
    'error': '错误信息（如果失败）'
}
```

## 特性

### 网站类型自动检测
- 根据URL自动识别网站类型
- 使用针对特定网站的优化提取策略

### 多重提取策略
- 主要内容区域提取
- 段落标签提取
- 通用内容提取作为备用

### 错误处理
- 网络超时处理
- 连接错误处理
- HTML解析错误处理

### 内容清理
- 移除HTML标签
- 清理多余空白
- 过滤无用内容

## 性能

- 支持批量处理
- 自动延迟避免请求过快
- 内存高效的内容处理

## 测试结果

基于数据库中的10篇文章测试：

- **总文章数**: 10篇
- **The Atlantic文章**: 5篇
- **Medium文章**: 5篇
- **数据库总内容长度**: 29,388字符
- **平均文章长度**: 2,939字符

### 内容质量分布
- 长篇文章 (>2000字符): 7篇 (70%)
- 中等文章 (1000-2000字符): 1篇 (10%)
- 短篇文章 (500-1000字符): 1篇 (10%)
- 很短文章 (<=500字符): 1篇 (10%)

## 文件结构

```
src/
├── content_extractor.py      # 主要提取器类
├── simple_content_extractor.py # 简化版本
├── test_extractor.py          # 测试程序
└── README_extractor.md        # 本说明文档
```

## 注意事项

1. **网络连接**: 需要稳定的网络连接来访问目标网站
2. **请求频率**: 批量处理时会自动添加延迟避免被限制
3. **网站变化**: 如果网站结构变化，可能需要更新正则表达式
4. **编码问题**: 程序已处理常见的编码问题

## 故障排除

### 常见问题

1. **提取失败**: 检查网络连接和URL是否正确
2. **内容为空**: 可能是网站结构变化或需要更新提取规则
3. **编码错误**: 程序已自动处理，如果仍有问题请检查环境设置

### 调试模式

```python
# 启用详细日志
extractor = ArticleContentExtractor()
result = extractor.extract_article_content(url, timeout=30)

# 检查错误信息
if not result['success']:
    print(f"提取失败: {result['error']}")
```

## 扩展支持

要支持新网站，需要：

1. 在`detect_site_type()`方法中添加网站识别逻辑
2. 添加专用的内容提取方法（如`_extract_sitename_content()`）
3. 更新主提取逻辑调用新方法

## 版本信息

- 版本: 1.0
- 更新日期: 2025-11-12
- 兼容性: Python 3.7+
- 依赖: requests, re, urllib.parse