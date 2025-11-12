#!/usr/bin/env python3
"""
文章内容提取器 - 最终版本
支持The Atlantic和Medium网站的文章内容自动提取
可在skill中直接调用
"""

import requests
import time
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


class ArticleContentExtractor:
    """
    文章内容提取器

    支持的网站:
    - The Atlantic (theatlantic.com)
    - Medium (medium.com)
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def detect_site_type(self, url: str) -> str:
        """
        检测网站类型

        Args:
            url: 文章URL

        Returns:
            'theatlantic', 'medium', 或 'unknown'
        """
        domain = urlparse(url).netloc.lower()

        if 'theatlantic.com' in domain:
            return 'theatlantic'
        elif 'medium.com' in domain:
            return 'medium'
        else:
            return 'unknown'

    def extract_article_content(self, url: str, timeout: int = 10) -> Dict[str, str]:
        """
        提取文章内容

        Args:
            url: 文章URL
            timeout: 请求超时时间（秒）

        Returns:
            包含title和content的字典，格式: {'title': str, 'content': str}
        """
        site_type = self.detect_site_type(url)

        try:
            # 请求页面
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            # 解析HTML内容
            title, content = self._parse_html_content(response.text, site_type)

            return {
                'title': title,
                'content': content,
                'site_type': site_type,
                'url': url,
                'success': bool(content)
            }

        except requests.exceptions.Timeout:
            return self._create_error_result(url, site_type, "请求超时")
        except requests.exceptions.ConnectionError:
            return self._create_error_result(url, site_type, "连接错误")
        except Exception as e:
            return self._create_error_result(url, site_type, f"提取失败: {str(e)}")

    def _create_error_result(self, url: str, site_type: str, error_msg: str) -> Dict[str, str]:
        """创建错误结果"""
        return {
            'title': '',
            'content': '',
            'site_type': site_type,
            'url': url,
            'success': False,
            'error': error_msg
        }

    def _parse_html_content(self, html: str, site_type: str) -> Tuple[str, str]:
        """
        解析HTML内容

        Args:
            html: HTML内容
            site_type: 网站类型

        Returns:
            (title, content) 元组
        """
        title = ''
        content = ''

        # 提取标题
        title = self._extract_title(html)

        # 根据网站类型提取内容
        if site_type == 'theatlantic':
            content = self._extract_theatlantic_content(html)
        elif site_type == 'medium':
            content = self._extract_medium_content(html)
        else:
            content = self._extract_generic_content(html)

        return title, content

    def _extract_title(self, html: str) -> str:
        """提取文章标题"""
        title_patterns = [
            r'<title[^>]*>([^<]+)</title>',
            r'<h1[^>]*class="[^"]*headline[^"]*"[^>]*>([^<]+)</h1>',
            r'<h1[^>]*data-testid="[^"]*storyTitle[^"]*"[^>]*>([^<]+)</h1>',
            r'<h1[^>]*itemprop="headline"[^>]*>([^<]+)</h1>',
            r'<h1[^>]*class="[^"]*graf-title[^"]*"[^>]*>([^<]+)</h1>'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                title = re.sub(r'\s+', ' ', match.group(1).strip())
                # 清理标题中的特殊字符
                title = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\'/]', '', title)
                if len(title) > 10:  # 确保标题有意义
                    break

        return title

    def _extract_theatlantic_content(self, html: str) -> str:
        """提取The Atlantic文章内容"""
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*data-testid="articleContent"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*article-content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*story-body[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*itemprop="articleBody"[^>]*>(.*?)</div>'
        ]

        return self._extract_with_patterns(html, content_patterns)

    def _extract_medium_content(self, html: str) -> str:
        """提取Medium文章内容"""
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*data-field="body"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*post-body[^"]*"[^>]*>(.*?)</div>',
            r'<section[^>]*data-field="body"[^>]*>(.*?)</section>',
            r'<div[^>]*class="[^"]*grafLayout[^"]*"[^>]*>(.*?)</div>'
        ]

        # 尝试提取graf元素（Medium特有的段落标记）
        content = self._extract_with_patterns(html, content_patterns)

        if len(content) < 500:
            # 尝试提取所有graf元素
            graf_pattern = r'<[^>]*class="[^"]*graf[^"]*"[^>]*>(.*?)</[^>]*>'
            graf_elements = re.findall(graf_pattern, html, re.DOTALL | re.IGNORECASE)
            if graf_elements:
                graf_content = self._clean_paragraphs(graf_elements)
                if len(graf_content) > len(content):
                    content = graf_content

        return content

    def _extract_generic_content(self, html: str) -> str:
        """通用内容提取"""
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*post-content[^"]*"[^>]*>(.*?)</div>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*role="main"[^>]*>(.*?)</div>'
        ]

        return self._extract_with_patterns(html, content_patterns)

    def _extract_with_patterns(self, html: str, patterns: List[str]) -> str:
        """使用正则模式列表提取内容"""
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                content_html = match.group(1)
                content = self._clean_html(content_html)
                if len(content) > 200:
                    return content

        # 如果没找到内容，尝试提取所有段落
        return self._extract_all_paragraphs(html)

    def _extract_all_paragraphs(self, html: str) -> str:
        """提取所有段落作为内容"""
        paragraph_patterns = [
            r'<p[^>]*>(.*?)</p>',
            r'<div[^>]*class="[^"]*paragraph[^"]*"[^>]*>(.*?)</div>'
        ]

        all_paragraphs = []
        for pattern in paragraph_patterns:
            paragraphs = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            all_paragraphs.extend(paragraphs)

        if all_paragraphs:
            return self._clean_paragraphs(all_paragraphs[:30])  # 取前30个段落

        return ''

    def _clean_paragraphs(self, paragraphs: List[str]) -> str:
        """清理段落列表"""
        cleaned_paragraphs = []
        for p in paragraphs:
            cleaned = self._clean_html(p).strip()
            if len(cleaned) > 30:  # 过滤短段落
                cleaned_paragraphs.append(cleaned)

        return '\\n\\n'.join(cleaned_paragraphs)

    def _clean_html(self, html: str) -> str:
        """清理HTML标签，保留纯文本"""
        # 移除script和style标签
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # 移除注释
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

        # 移除所有HTML标签
        html = re.sub(r'<[^>]+>', ' ', html)

        # 清理多余的空白字符
        html = re.sub(r'\s+', ' ', html)
        html = re.sub(r'\n\s*\n', '\n\n', html)

        return html.strip()

    def batch_extract_from_urls(self, urls: List[str], delay: float = 1.0) -> List[Dict[str, str]]:
        """
        批量提取文章内容

        Args:
            urls: URL列表
            delay: 请求间隔（秒）

        Returns:
            提取结果列表
        """
        results = []

        for i, url in enumerate(urls, 1):
            print(f"正在处理第 {i}/{len(urls)} 篇文章: {url}")

            try:
                result = self.extract_article_content(url)
                results.append(result)

                if result.get('success'):
                    content_length = len(result.get('content', ''))
                    print(f"  成功提取，内容长度: {content_length} 字符")
                else:
                    print(f"  提取失败: {result.get('error', '未知错误')}")

            except Exception as e:
                print(f"  处理失败: {e}")
                results.append({
                    'url': url,
                    'title': '',
                    'content': '',
                    'success': False,
                    'error': str(e)
                })

            # 添加延迟避免请求过快
            if i < len(urls) and delay > 0:
                time.sleep(delay)

        return results

    def extract_from_database_essays(self, api_url: str = "http://localhost:8000/api/essays") -> List[Dict[str, str]]:
        """
        从数据库API获取文章并提取内容

        Args:
            api_url: 文章API地址

        Returns:
            提取结果列表
        """
        try:
            # 获取数据库中的文章
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()
            essays = data.get('essays', [])

            print(f"从数据库获取到 {len(essays)} 篇文章")

            # 提取URL列表
            urls = [essay['url'] for essay in essays]

            # 批量提取
            return self.batch_extract_from_urls(urls)

        except Exception as e:
            print(f"从数据库获取文章失败: {e}")
            return []


# 便利函数，便于在skill中调用
def extract_content_from_url(url: str) -> Dict[str, str]:
    """
    从单个URL提取文章内容的便利函数

    Args:
        url: 文章URL

    Returns:
        提取结果字典
    """
    extractor = ArticleContentExtractor()
    return extractor.extract_article_content(url)


def batch_extract_content(urls: List[str]) -> List[Dict[str, str]]:
    """
    批量提取文章内容的便利函数

    Args:
        urls: URL列表

    Returns:
        提取结果列表
    """
    extractor = ArticleContentExtractor()
    return extractor.batch_extract_from_urls(urls)


def extract_from_database(api_url: str = "http://localhost:8000/api/essays") -> List[Dict[str, str]]:
    """
    从数据库批量提取文章内容的便利函数

    Args:
        api_url: 文章API地址

    Returns:
        提取结果列表
    """
    extractor = ArticleContentExtractor()
    return extractor.extract_from_database_essays(api_url)


if __name__ == "__main__":
    # 测试代码
    extractor = ArticleContentExtractor()

    # 测试URL
    test_urls = [
        "https://www.theatlantic.com/newsletters/2025/11/baseball-gambling-charges-mlb-cleveland-guardians/684896/",
        "https://medium.com/@ryanmcnutt/heres-to-the-2025-toronto-blue-jays-d4df71d3f035"
    ]

    print("测试文章内容提取器...")
    print("=" * 50)

    for url in test_urls:
        print(f"\\n测试URL: {url}")
        result = extractor.extract_article_content(url)

        print(f"网站类型: {result.get('site_type', 'unknown')}")
        print(f"标题: {result.get('title', 'N/A')}")
        print(f"内容长度: {len(result.get('content', ''))} 字符")
        print(f"提取状态: {'成功' if result.get('success') else '失败'}")

        if result.get('error'):
            print(f"错误信息: {result['error']}")

    print("\\n" + "=" * 50)
    print("测试完成！")