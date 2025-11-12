#!/usr/bin/env python3
"""
文章内容提取器使用示例
展示如何在skill中调用提取器
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content_extractor import extract_content_from_url, batch_extract_content, extract_from_database


def example_single_extraction():
    """示例：提取单个文章内容"""
    print("=== 示例1: 提取单个文章内容 ===")

    # The Atlantic文章示例
    url = "https://www.theatlantic.com/newsletters/2025/11/baseball-gambling-charges-mlb-cleveland-guardians/684896/"

    print(f"正在提取: {url}")
    result = extract_content_from_url(url)

    if result['success']:
        print(f"标题: {result['title']}")
        print(f"网站类型: {result['site_type']}")
        print(f"内容长度: {len(result['content'])} 字符")
        print(f"内容预览: {result['content'][:200]}...")
    else:
        print(f"提取失败: {result.get('error', '未知错误')}")

    print()


def example_batch_extraction():
    """示例：批量提取文章内容"""
    print("=== 示例2: 批量提取文章内容 ===")

    urls = [
        "https://www.theatlantic.com/newsletters/2025/11/baseball-gambling-charges-mlb-cleveland-guardians/684896/",
        "https://medium.com/@ryanmcnutt/heres-to-the-2025-toronto-blue-jays-d4df71d3f035",
        "https://www.theatlantic.com/health/2025/11/supplement-patches-wellness/684893/"
    ]

    print(f"正在批量提取 {len(urls)} 篇文章...")
    results = batch_extract_content(urls)

    for i, result in enumerate(results, 1):
        status = "成功" if result['success'] else "失败"
        print(f"{i}. {result['site_type']} - {status}")
        if result['success']:
            print(f"   标题: {result['title'][:50]}...")
            print(f"   长度: {len(result['content'])} 字符")
        else:
            print(f"   错误: {result.get('error', '未知错误')}")

    print()


def example_database_extraction():
    """示例：从数据库批量提取"""
    print("=== 示例3: 从数据库批量提取 ===")

    try:
        results = extract_from_database("http://localhost:8000/api/essays")

        print(f"从数据库提取到 {len(results)} 篇文章")

        # 按网站类型统计
        site_counts = {}
        total_content_length = 0

        for result in results:
            site_type = result['site_type']
            site_counts[site_type] = site_counts.get(site_type, 0) + 1
            total_content_length += len(result['content'])

        print(f"网站类型分布:")
        for site_type, count in site_counts.items():
            print(f"  {site_type}: {count} 篇")

        print(f"总内容长度: {total_content_length} 字符")
        print(f"平均长度: {total_content_length // len(results) if results else 0} 字符")

    except Exception as e:
        print(f"数据库提取失败: {e}")

    print()


def example_skill_integration():
    """示例：在skill中集成使用"""
    print("=== 示例4: Skill集成使用示例 ===")

    def process_article_for_skill(url: str) -> dict:
        """
        在skill中处理文章的示例函数

        Args:
            url: 文章URL

        Returns:
            处理结果字典
        """
        # 提取文章内容
        result = extract_content_from_url(url)

        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', '提取失败'),
                'url': url
            }

        # 在这里可以添加更多的处理逻辑
        processed_content = {
            'title': result['title'],
            'content': result['content'],
            'summary': result['content'][:500] + "..." if len(result['content']) > 500 else result['content'],
            'word_count': len(result['content'].split()),
            'site_type': result['site_type'],
            'url': url,
            'extracted_at': "2025-11-12"  # 实际使用时应该用当前时间
        }

        return {
            'success': True,
            'data': processed_content
        }

    # 使用示例
    test_url = "https://medium.com/@ryanmcnutt/heres-to-the-2025-toronto-blue-jays-d4df71d3f035"

    print(f"Skill处理示例:")
    result = process_article_for_skill(test_url)

    if result['success']:
        data = result['data']
        print(f"标题: {data['title']}")
        print(f"字数: {data['word_count']}")
        print(f"网站: {data['site_type']}")
        print(f"摘要: {data['summary'][:100]}...")
    else:
        print(f"处理失败: {result['error']}")

    print()


def main():
    """运行所有示例"""
    print("文章内容提取器使用示例")
    print("=" * 50)
    print()

    # 注意：由于网络连接问题，以下示例可能失败
    # 但代码结构和使用方法是正确的

    try:
        example_single_extraction()
    except Exception as e:
        print(f"示例1执行失败: {e}")

    try:
        example_batch_extraction()
    except Exception as e:
        print(f"示例2执行失败: {e}")

    try:
        example_database_extraction()
    except Exception as e:
        print(f"示例3执行失败: {e}")

    try:
        example_skill_integration()
    except Exception as e:
        print(f"示例4执行失败: {e}")

    print("所有示例演示完成！")
    print()
    print("在实际使用中，请确保：")
    print("1. 网络连接正常")
    print("2. API服务器正在运行（对于数据库示例）")
    print("3. URL地址正确且可访问")


if __name__ == "__main__":
    main()