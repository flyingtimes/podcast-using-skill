# Podcast Examples 项目信息

## 项目概述

这是一个演示如何使用 anthropic skills 生成播客内容的 Python 项目。项目使用现代 Python 开发最佳实践，包括 uv 包管理器、类型注解和完整的开发工具链。

## 技术栈

- **语言**: Python 3.8+
- **包管理器**: uv
- **主要依赖**:
  - requests: HTTP 请求库
  - python-dotenv: 环境变量管理
- **开发工具**:
  - pytest: 测试框架
  - black: 代码格式化
  - flake8: 代码风格检查
  - mypy: 类型检查

## 项目结构

```
podcast-examples/
├── src/podcast_examples/    # 主要源代码
├── tests/                   # 测试文件（待创建）
├── output/                  # 生成的播客文件存储
├── .env                     # 环境变量配置（受版本控制忽略）
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略文件配置
├── pyproject.toml          # 项目配置和依赖管理
├── uv.lock                 # 依赖锁定文件
└── README.md               # 项目文档
```

## API 集成

项目集成了 RunningHub API 服务，提供以下功能：
- 播客内容生成
- 音频处理
- WebApp 集成

## 环境配置

项目使用 `.env` 文件管理敏感配置：
- `RUNNINGHUB_API_KEY`: API 访问密钥
- `RUNNINGHUB_BASE_URL`: API 服务地址
- `RUNNINGHUB_WEBAPP_ID`: 主应用 ID
- `audio_webappId`: 音频处理应用 ID

## 开发指南

### 安装和设置

1. 使用 uv 安装依赖：`uv sync`
2. 复制 `.env.example` 到 `.env` 并配置 API 密钥
3. 激活虚拟环境：`source .venv/bin/activate`

### 开发工作流

1. 运行测试：`pytest`
2. 代码格式化：`black src/`
3. 类型检查：`mypy src/`
4. 代码风格检查：`flake8 src/`

## 注意事项

- `.env` 文件包含敏感信息，已被 `.gitignore` 排除
- `output/` 目录用于存储生成的文件，也被版本控制忽略
- 项目使用 uv 作为推荐的包管理器，支持快速的依赖安装和解析

## 待办事项

- [ ] 创建完整的测试套件
- [ ] 添加更多的播客生成示例
- [ ] 实现错误处理和重试机制
- [ ] 添加日志记录功能
- [ ] 创建配置验证功能