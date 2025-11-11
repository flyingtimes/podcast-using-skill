# 文章管理系统 API 文档

## 项目介绍

这是一个基于 FastAPI 的文章管理系统，支持批量添加文章数据，自动检查并跳过重复的文章标题。

## 安装和运行

### 1. 安装依赖（使用 uv）

```bash
uv sync
```

### 2. 运行服务器

```bash
cd src
python essay_manager.py
```

服务器将在 `http://localhost:8000` 启动。

### 3. 运行测试

```bash
python test_essay_manager.py
```

## API 接口

### 1. 添加文章

**POST** `/api/essays`

批量添加文章到数据库，自动检查重复标题。

#### 请求格式

```json
{
  "essays": [
    {
      "title": "文章标题",
      "subtitle": "文章副标题（可选）",
      "author": "作者姓名（可选）",
      "entry_time": "2024-01-15 10:30:00"
    }
  ]
}
```

#### 响应格式

```json
{
  "success_count": 2,
  "skipped_count": 1,
  "successful_titles": [
    "Python编程入门",
    "数据结构与算法"
  ],
  "message": "成功添加 2 篇文章，跳过 1 篇重复文章"
}
```

#### 请求示例（curl）

```bash
curl -X POST "http://localhost:8000/api/essays" \
  -H "Content-Type: application/json" \
  -d '{
    "essays": [
      {
        "title": "Python编程入门",
        "subtitle": "零基础学习Python",
        "author": "张三",
        "entry_time": "2024-01-15 10:30:00"
      },
      {
        "title": "数据结构与算法",
        "subtitle": "计算机科学基础",
        "author": "李四",
        "entry_time": "2024-01-16 14:20:00"
      }
    ]
  }'
```

### 2. 获取所有文章

**GET** `/api/essays`

获取数据库中所有文章的列表。

#### 响应格式

```json
{
  "count": 3,
  "essays": [
    {
      "id": 1,
      "title": "Python编程入门",
      "subtitle": "零基础学习Python",
      "author": "张三",
      "entry_time": "2024-01-15T10:30:00",
      "created_at": "2024-01-20T08:30:00"
    }
  ]
}
```

### 3. 健康检查

**GET** `/api/health`

检查服务器是否正常运行。

#### 响应格式

```json
{
  "status": "healthy",
  "message": "文章管理系统运行正常"
}
```

## 数据库

系统使用 SQLite 数据库，数据库文件 `essays.db` 会在首次运行时自动创建在 `src` 目录下。

### 文章表结构

- `id`: 主键，自动递增
- `title`: 文章标题（唯一，不允许重复）
- `subtitle`: 文章副标题
- `author`: 作者姓名
- `entry_time`: 录入时间
- `created_at`: 记录创建时间（自动生成）

## 错误处理

- 如果文章标题已存在，该文章会被跳过，不会影响其他文章的添加
- 系统会返回成功添加的文章数量和跳过的重复文章数量
- 所有的时间字段支持多种格式，系统会自动解析

## 开发说明

### 项目结构

```
.
├── src/
│   ├── essay_manager.py  # FastAPI 主程序
│   └── database.py       # 数据库操作模块
├── test_essay_manager.py # 测试脚本
├── pyproject.toml        # uv 项目配置
└── README_API.md         # API 文档
```

### 扩展开发

- 可以添加更多文章字段，如标签、分类等
- 可以添加文章的更新和删除功能
- 可以添加分页查询和搜索功能