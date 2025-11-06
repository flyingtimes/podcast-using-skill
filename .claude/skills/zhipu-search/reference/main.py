#!/usr/bin/env python3
"""
zhipu-search技能主程序
根据用户给出的搜索关键语句，调用zhipu的搜索引擎得到搜索结果
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any

def load_env():
    """加载环境变量"""
    # 获取项目根目录 (项目根目录是技能目录的上上级目录)
    skill_dir = os.path.dirname(__file__)  # .claude/skills/zhipu-search
    skills_dir = os.path.dirname(skill_dir)  # .claude/skills
    claude_dir = os.path.dirname(skills_dir)  # .claude
    project_root = os.path.dirname(claude_dir)  # 项目根目录

    env_path = os.path.join(project_root, '.env')

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

def analyze_time_keywords(query: str) -> str:
    """
    分析查询中的时间关键词，如果有时间相关的关键词则计算准确日期
    """
    today = datetime.now()

    # 时间关键词映射
    time_patterns = {
        r'今天|今日': today,
        r'昨天|昨日': today - timedelta(days=1),
        r'明天|明日': today + timedelta(days=1),
        r'后天': today + timedelta(days=2),
        r'前天': today - timedelta(days=2),
        r'本周|这周': today,
        r'下周': today + timedelta(weeks=1),
        r'上周': today - timedelta(weeks=1),
        r'本月|这个月': today,
        r'下月|下个月': today.replace(day=1) + timedelta(days=32),
        r'上月|上个月': today.replace(day=1) - timedelta(days=1),
    }

    modified_query = query

    # 检查并替换时间关键词
    for pattern, date_obj in time_patterns.items():
        if re.search(pattern, query):
            formatted_date = date_obj.strftime("%Y年%m月%d日")
            modified_query = re.sub(pattern, formatted_date, query)
            break

    # 处理具体的年份表述
    year_match = re.search(r'(\d{4})年', query)
    if year_match:
        year = year_match.group(1)
        # 如果查询中提到了年份，保持原样
        pass
    else:
        # 如果没有明确年份，添加当前年份
        current_year = today.year
        if '年' not in modified_query and '月' in modified_query and '日' in modified_query:
            modified_query = f"{current_year}年" + modified_query

    return modified_query

def setup_environment():
    """验证并安装依赖"""
    try:
        import zai
        print(f"zai-sdk已安装，版本: {zai.__version__}")
        return True
    except ImportError:
        print("zai-sdk未安装，正在安装...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "uv", "add", "zai-sdk"],
                                  capture_output=True, text=True, check=True)
            print("zai-sdk安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"zai-sdk安装失败: {e}")
            try:
                # 备选方案：使用pip
                result = subprocess.run([sys.executable, "-m", "pip", "install", "zai-sdk"],
                                      capture_output=True, text=True, check=True)
                print("zai-sdk安装成功（使用pip）")
                return True
            except subprocess.CalledProcessError as e:
                print(f"zai-sdk安装失败: {e}")
                return False

def search_with_zhipu(query: str) -> Dict[str, Any]:
    """
    使用智谱搜索引擎进行搜索
    """
    try:
        from zai import ZhipuAiClient

        # 获取API密钥
        api_key = os.getenv('zhipu_search_apikey')
        if not api_key:
            return {"error": "未找到zhipu_search_apikey环境变量"}

        # 创建客户端
        client = ZhipuAiClient(api_key=api_key)

        # 执行搜索
        response = client.web_search.web_search(
            search_engine="search_pro",
            search_query=query,
            count=10,  # 返回10条结果
            content_size="high"  # 获取较详细的摘要
        )

        return {"success": True, "data": response}

    except Exception as e:
        return {"error": f"搜索失败: {str(e)}"}

def save_results(query: str, results: Dict[str, Any]):
    """
    保存搜索结果到output目录
    """
    os.makedirs("output", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/search_results_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "original_query": query,
        "results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)

    print(f"搜索结果已保存到: {filename}")
    return filename

def format_search_results(results: Dict[str, Any]) -> str:
    """
    格式化搜索结果用于显示
    """
    if "error" in results:
        return f"搜索出错: {results['error']}"

    if not results.get("success") or "data" not in results:
        return "搜索结果为空"

    data = results["data"]

    # 根据实际的API响应结构调整解析逻辑
    if hasattr(data, 'search_result') and data.search_result:
        formatted_output = "搜索结果：\n\n"
        for i, result in enumerate(data.search_result, 1):
            title = getattr(result, 'title', '无标题')
            content = getattr(result, 'content', '无内容')
            link = getattr(result, 'link', '无链接')
            media = getattr(result, 'media', '无来源')
            publish_date = getattr(result, 'publish_date', '无日期')

            formatted_output += f"{i}. 【{title}】\n"
            formatted_output += f"   来源: {media}\n"
            formatted_output += f"   日期: {publish_date}\n"
            formatted_output += f"   链接: {link}\n"
            formatted_output += f"   摘要: {content[:200]}{'...' if len(content) > 200 else ''}\n\n"

        return formatted_output
    else:
        return "未找到有效的搜索结果"

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python main.py <搜索关键词>")
        sys.exit(1)

    original_query = " ".join(sys.argv[1:])
    print(f"原始查询: {original_query}")

    # 加载环境变量
    load_env()

    # 分析时间关键词
    modified_query = analyze_time_keywords(original_query)
    print(f"处理后查询: {modified_query}")

    # 验证并安装依赖
    if not setup_environment():
        print("环境设置失败")
        sys.exit(1)

    # 执行搜索
    print("正在搜索...")
    results = search_with_zhipu(modified_query)

    # 保存结果
    save_results(original_query, results)

    # 格式化并显示结果
    formatted_results = format_search_results(results)
    print("\n" + "="*50)
    print(formatted_results)

if __name__ == "__main__":
    main()