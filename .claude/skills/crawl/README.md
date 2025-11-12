# 📁 Crawl 技能文件结构

## 🗂️ 文件组织

crawl 技能已按照模块化原则重新组织，每个文件都有明确的职责和合理的长度限制。

```
.claude/skills/crawl/
├── README.md                 # 本文件 - 文件结构说明
├── SKILL.md                  # 主技能文档 (112行) ⭐
├── QUICK_START.md            # 快速启动指南 (~150行)
├── EXAMPLES.md               # 详细使用示例 (~400行)
├── BEST_PRACTICES.md         # 最佳实践指南 (~600行)
├── crawl_manager.py          # 核心管理器代码 (~300行)
└── how-to-crawl-with-chrome-dev-mcp.md  # Chrome DevTools MCP 配置
```

## 📋 文件职责

| 文件 | 主要内容 | 目标长度 | 用途 |
|------|----------|----------|------|
| **SKILL.md** | 技能概述、核心功能、快速入门 | <200行 | ⭐ 主要入口 |
| **QUICK_START.md** | 环境配置、快速启动、常见问题 | <200行 | 新手指南 |
| **EXAMPLES.md** | 详细代码示例、使用案例 | <500行 | 参考文档 |
| **BEST_PRACTICES.md** | 性能优化、错误处理、安全合规 | <700行 | 进阶指南 |
| **crawl_manager.py** | 核心功能实现、工具函数 | <400行 | 直接使用 |
| **README.md** | 文件结构说明、导航指南 | <100行 | 结构说明 |

## 🎯 使用路径

### 新手用户
1. **SKILL.md** → 了解技能概述
2. **QUICK_START.md** → 快速开始使用
3. **crawl_manager.py** → 直接使用核心功能

### 进阶用户
1. **EXAMPLES.md** → 查看详细示例
2. **BEST_PRACTICES.md** → 优化性能和稳定性
3. **crawl_manager.py** → 自定义和扩展

### 开发者
1. **BEST_PRACTICES.md** → 了解最佳实践
2. **EXAMPLES.md** → 学习实现细节
3. **crawl_manager.py** → 查看源码实现

## 🚀 快速导航

### 想要快速开始？
→ [QUICK_START.md](QUICK_START.md)

### 想要查看示例？
→ [EXAMPLES.md](EXAMPLES.md)

### 想要了解最佳实践？
→ [BEST_PRACTICES.md](BEST_PRACTICES.md)

### 想要直接使用代码？
→ [crawl_manager.py](crawl_manager.py)

### 想要了解技能概述？
→ [SKILL.md](SKILL.md)

## 📈 文件统计

| 文件 | 当前行数 | 目标行数 | 状态 |
|------|----------|----------|------|
| SKILL.md | 112 | <200 | ✅ 符合要求 |
| QUICK_START.md | ~150 | <200 | ✅ 符合要求 |
| EXAMPLES.md | ~400 | <500 | ✅ 符合要求 |
| BEST_PRACTICES.md | ~600 | <700 | ✅ 符合要求 |
| crawl_manager.py | ~300 | <400 | ✅ 符合要求 |
| README.md | ~80 | <100 | ✅ 符合要求 |

## 🔄 更新维护

### 添加新功能时
1. 更新 `crawl_manager.py` 中的核心代码
2. 在 `EXAMPLES.md` 中添加使用示例
3. 如需要，在 `BEST_PRACTICES.md` 中添加最佳实践
4. 更新 `SKILL.md` 中的功能描述

### 修复问题时
1. 优先更新相关文档
2. 确保示例代码保持最新
3. 更新版本信息和更新日志

## 📚 相关资源

- **项目根目录**: `../../../`
- **源代码目录**: `../../../src/`
- **输出目录**: `../../../output/`
- **改进版管理器**: `../../../output/improved_crawl_manager.py`

---

**文件重组完成时间**: 2025-11-12
**重组版本**: v2.0
**文件总数**: 7个
**总行数**: ~2000行（分散在多个文件中）

🎉 **现在文档结构更加清晰，便于维护和使用！**