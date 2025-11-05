# Podcast Examples

Podcast examples project with RunningHub API integration.

## 项目简介

这个项目演示了如何使用 RunningHub API 生成播客内容。项目包含了完整的API集成示例，展示了如何调用播客生成服务并处理返回结果。

## 安装

### 前置要求
- Python 3.8+
- uv (推荐的Python包管理器)

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/your-username/podcast-examples.git
cd podcast-examples
```

2. 安装依赖：
```bash
uv sync
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的 RunningHub API 密钥
```

## 使用方法

### 基本用法

运行播客生成脚本：

```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 运行播客生成示例
python src/podcast_examples/generate_podcast.py
```

### 配置说明

在 `.env` 文件中配置以下参数：
- `RUNNINGHUB_API_KEY`: 您的 RunningHub API 密钥
- `RUNNINGHUB_BASE_URL`: RunningHub API 基础URL
- `RUNNINGHUB_WEBAPP_ID`: 您的 WebApp ID

## 开发

### 开发环境设置

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
pytest

# 代码格式化
black src/

# 类型检查
mypy src/

# 代码风格检查
flake8 src/
```

### 项目结构

```
podcast-examples/
├── src/
│   └── podcast_examples/
│       ├── __init__.py
│       └── generate_podcast.py
├── tests/
├── output/           # 生成的播客文件存储目录
├── .env             # 环境变量配置文件
├── .gitignore       # Git忽略文件配置
├── pyproject.toml   # 项目配置文件
└── README.md        # 项目说明文档
```

## API 文档

详细的 RunningHub API 文档请参考：[RunningHub API Documentation](https://www.runninghub.cn/docs)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。