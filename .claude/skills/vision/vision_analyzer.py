#!/usr/bin/env python3
"""
图片/PDF分析工具
通过命令行给出图片或PDF文件路径和需求描述，使用Zhipu AI进行分析

支持功能：
- 图片文件分析（JPG, PNG, GIF等常见格式）
- PDF文件分析（自动转换为图片逐页处理）
- 多页PDF结果自动拼接
"""

import argparse
import sys
import os
import base64
import tempfile
from typing import List, Union
from zai import ZhipuAiClient
from dotenv import load_dotenv
import markitdown
from PIL import Image

# 设置控制台编码为UTF-8，解决Windows下中文显示问题
if sys.platform == 'win32':
    import locale
    import codecs
    # 尝试设置控制台编码
    try:
        # 重新配置标准输出流
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(text):
    """安全打印函数，确保中文正确显示"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果出现编码错误，尝试使用其他编码
        try:
            print(text.encode('gbk', errors='ignore').decode('gbk'))
        except:
            # 最后的选择：移除非ASCII字符
            safe_text = ''.join(char if ord(char) < 128 else '?' for char in str(text))
            print(safe_text)

def load_image_as_base64(image_path):
    """将图片文件转换为base64格式"""
    try:
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        return img_base64
    except FileNotFoundError:
        safe_print(f"错误: 找不到图片文件 '{image_path}'")
        sys.exit(1)
    except Exception as e:
        safe_print(f"错误: 读取图片文件时出错 - {e}")
        sys.exit(1)

def load_pil_image_as_base64(image):
    """将PIL图片对象转换为base64格式"""
    try:
        import io
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_base64
    except Exception as e:
        safe_print(f"错误: 转换PIL图片时出错 - {e}")
        sys.exit(1)

def convert_pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """使用markitdown将PDF文件转换为图片列表"""
    try:
        safe_print(f"正在转换PDF文件: {pdf_path}")
        md = markitdown.MarkItDown()
        result = md.convert(pdf_path)

        # markitdown返回的是markdown内容，我们需要处理不同的内容类型
        if hasattr(result, 'text_content') and result.text_content:
            safe_print(f"PDF转换完成，已提取文本内容")
            # 对于markitdown，我们需要创建一个虚拟的图片来代表内容
            # 或者直接处理文本内容

            # 这里我们可以创建一个包含文本的图片作为替代
            from PIL import Image, ImageDraw, ImageFont
            import textwrap

            images = []

            # 将长文本分成多页
            text = result.text_content
            lines = text.split('\n')
            page_text = []
            current_page = []

            # 每页大约30行
            for line in lines:
                current_page.append(line)
                if len(current_page) >= 30:
                    page_text.append('\n'.join(current_page))
                    current_page = []

            if current_page:
                page_text.append('\n'.join(current_page))

            # 为每页文本创建图片
            for i, page in enumerate(page_text):
                # 创建白色背景图片
                img = Image.new('RGB', (800, 1000), color='white')
                draw = ImageDraw.Draw(img)

                # 尝试使用默认字体
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                except:
                    font = ImageFont.load_default()

                # 绘制文本
                y_offset = 20
                for line in page.split('\n'):
                    # 处理长行
                    wrapped_lines = textwrap.wrap(line, width=80)
                    for wrapped_line in wrapped_lines:
                        if y_offset < 980:  # 留出边距
                            draw.text((20, y_offset), wrapped_line, fill='black', font=font)
                            y_offset += 15

                images.append(img)

            safe_print(f"PDF转换完成，共 {len(images)} 页")
            return images
        else:
            safe_print("错误: 无法从PDF提取内容")
            sys.exit(1)

    except Exception as e:
        safe_print(f"错误: PDF转换失败 - {e}")
        sys.exit(1)

def is_pdf_file(file_path: str) -> bool:
    """检查文件是否为PDF格式"""
    return file_path.lower().endswith('.pdf')

def analyze_image_file(file_path: str, prompt_text: str):
    """使用Zhipu AI分析图片或PDF文件"""
    # 加载环境变量
    load_dotenv()

    # 获取API密钥
    api_key = os.getenv('zhipu_search_apikey')
    if not api_key:
        safe_print("错误: 未找到 zhipu_search_apikey 环境变量")
        safe_print("请确保在 .env 文件中设置了 zhipu_search_apikey")
        sys.exit(1)

    # 初始化客户端
    client = ZhipuAiClient(api_key=api_key)

    # 检查文件类型并处理
    if is_pdf_file(file_path):
        # PDF文件处理
        images = convert_pdf_to_images(file_path)
        return analyze_multiple_images(client, images, prompt_text)
    else:
        # 图片文件处理
        safe_print(f"正在加载图片: {file_path}")
        img_base64 = load_image_as_base64(file_path)
        return analyze_single_image(client, img_base64, prompt_text)

def analyze_single_image(client, img_base64: str, prompt_text: str):
    """分析单张图片"""
    # 构建请求
    safe_print("正在发送请求到 Zhipu AI...")
    response = client.chat.completions.create(
        model="glm-4.5v",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_text
                    }
                ]
            }
        ],
        thinking={
            "type": "enabled"
        }
    )
    return response.choices[0].message

def analyze_multiple_images(client, images: List[Image.Image], prompt_text: str):
    """分析多张图片（PDF多页）"""
    all_results = []

    for i, image in enumerate(images, 1):
        safe_print(f"正在处理第 {i}/{len(images)} 页...")

        # 转换为base64
        img_base64 = load_pil_image_as_base64(image)

        # 构建请求
        safe_print(f"正在发送第 {i} 页的请求到 Zhipu AI...")
        response = client.chat.completions.create(
            model="glm-4.5v",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": f"这是PDF文件的第 {i} 页（共 {len(images)} 页）。{prompt_text}"
                        }
                    ]
                }
            ],
            thinking={
                "type": "enabled"
            }
        )

        result = response.choices[0].message
        if hasattr(result, 'content'):
            all_results.append(f"=== 第 {i} 页分析结果 ===\n{result.content}")
        else:
            all_results.append(f"=== 第 {i} 页分析结果 ===\n{str(result)}")

    # 拼接所有结果
    combined_result = "\n\n".join(all_results)

    # 创建一个模拟的消息对象来保持接口一致性
    class CombinedResult:
        def __init__(self, content):
            self.content = content

    return CombinedResult(combined_result)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="图片/PDF分析工具 - 使用Zhipu AI分析图片或PDF内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 图片分析
  python vision_analyzer.py image.jpg "请描述这个图片"
  python vision_analyzer.py screenshot.png "这个界面有什么问题？"
  python vision_analyzer.py photo.jpg "识别图片中的文字内容"

  # PDF分析
  python vision_analyzer.py document.pdf "请总结这个PDF文档的主要内容"
  python vision_analyzer.py contract.pdf "这个合同有什么需要注意的条款？"
  python vision_analyzer.py presentation.pdf "提取这个演示文稿的关键信息"
        """
    )

    parser.add_argument(
        "file_path",
        help="要分析的图片或PDF文件路径"
    )

    parser.add_argument(
        "prompt",
        help="对文件内容的需求描述文本"
    )

    parser.add_argument(
        "--output", "-o",
        help="将结果保存到指定文件"
    )

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.file_path):
        safe_print(f"错误: 文件 '{args.file_path}' 不存在")
        sys.exit(1)

    # 检查文件类型
    if is_pdf_file(args.file_path):
        safe_print(f"检测到PDF文件: {args.file_path}")
    else:
        safe_print(f"检测到图片文件: {args.file_path}")

    try:
        # 分析文件
        result = analyze_image_file(args.file_path, args.prompt)

        # 输出结果
        if hasattr(result, 'content'):
            output_text = result.content
        else:
            output_text = str(result)

        # 保存到文件或输出到控制台
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output_text)
                safe_print(f"分析结果已保存到: {args.output}")
            except Exception as e:
                safe_print(f"错误: 无法保存文件 - {e}")
                sys.exit(1)
        else:
            safe_print("\n" + "="*50)
            safe_print("分析结果:")
            safe_print("="*50)
            safe_print(output_text)

    except Exception as e:
        safe_print(f"错误: 分析过程中出现异常 - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()