# Martian - Markdown to Notion Converter

[![PyPI version](https://badge.fury.io/py/pymartian.svg)](https://badge.fury.io/py/pymartian)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

将 Markdown 和 GitHub Flavored Markdown 转换为 Notion API Blocks 和 RichText 的 Python 库。

这是 TypeScript 版本 [@tryfabric/martian](https://github.com/tryfabric/martian) 的完整 Python 移植，与 Notion API 完美配合。

## ✨ 特性

- ✅ 完全支持所有内联元素（斜体、粗体、删除线、内联代码、超链接、方程式）
- ✅ 列表（有序、无序、待办事项）支持任意深度嵌套
- ✅ 所有标题级别（>= 3级标题统一为3级标题）
- ✅ 代码块，支持语言高亮
- ✅ 引用块
  - 支持 GFM Alerts（[!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION]）
  - 支持 Notion Callouts（Emoji 开头的引用块）
  - 自动映射常见 emoji 和 alert 类型到合适的背景颜色
  - 保留 callout 内的格式和嵌套块
- ✅ 表格
- ✅ 方程式
- ✅ 图片
  - 内联图片会被提取并添加到段落后（Notion 不支持内联图片）
  - 图片URL会被验证，无效的会转为文本供手动修复

## 📦 安装

使用 pip 安装：

```bash
pip install pymartian
```

或者从源码安装：

```bash
git clone https://github.com/xwEric/pymartian.git
cd pymartian
pip install -e .
```

## 🎯 快速开始

```python
from martian import markdown_to_blocks

# 转换 Markdown 为 Notion blocks
markdown = """
# 欢迎使用 Martian

这是一个 **强大** 的转换工具，支持：

- [x] 任务列表
- 代码块
- 表格
- 数学公式

> [!NOTE]
> 支持 GitHub Flavored Markdown alerts！
"""

blocks = markdown_to_blocks(markdown)
print(blocks)
```

## 📖 使用文档

### 核心 API

Martian 提供两个主要函数：

```python
from martian import markdown_to_blocks, markdown_to_rich_text

# 转换为 Notion Blocks（用于页面内容）
blocks = markdown_to_blocks("markdown content", options={})

# 转换为 RichText（用于属性、标题等）
rich_text = markdown_to_rich_text("markdown content", options={})
```

### 示例 1：转换为 Blocks

```python
from martian import markdown_to_blocks

result = markdown_to_blocks("""
hello _world_ 
*** 
## heading2
* [x] todo
""")

print(result)
# [
#   {'object': 'block', 'type': 'paragraph', ...},
#   {'object': 'block', 'type': 'divider', ...},
#   {'object': 'block', 'type': 'heading_2', ...},
#   {'object': 'block', 'type': 'to_do', ...}
# ]
```

### 示例 2：转换为 RichText

```python
from martian import markdown_to_rich_text

result = markdown_to_rich_text("**Hello _world_**")

print(result)
# [
#   {'type': 'text', 'annotations': {'bold': True, ...}, 'text': {'content': 'Hello '}},
#   {'type': 'text', 'annotations': {'bold': True, 'italic': True, ...}, 'text': {'content': 'world'}}
# ]
```

### 使用 Blockquotes

Martian 支持三种类型的 blockquotes：

#### 1. 标准 Blockquotes

```markdown
> This is a regular blockquote
> It can span multiple lines
```

#### 2. GFM Alerts

```markdown
> [!NOTE]
> Important information that users should know

> [!WARNING]
> Critical information that needs attention
```

GFM alerts 会自动转换为 Notion callouts，带有合适的图标和颜色：
- **NOTE** (📘, blue): 用户应该知道的有用信息
- **TIP** (💡, green): 做事情更好的提示
- **IMPORTANT** (☝️, purple): 用户需要知道的关键信息
- **WARNING** (⚠️, yellow): 需要立即注意的紧急信息
- **CAUTION** (❗, red): 关于风险或负面结果的建议

#### 3. Emoji 风格 Callouts（可选）

默认情况下，emoji callouts 是禁用的。可以使用 `enableEmojiCallouts` 选项启用：

```python
from martian import markdown_to_blocks

result = markdown_to_blocks("""
> 📘 **Note:** This is a callout with a blue background
> It supports all markdown formatting
""", options={'enableEmojiCallouts': True})
```

支持的 emoji 颜色映射：
- 📘 (blue): 适合笔记和信息
- 👍 (green): 成功消息和提示
- ❗ (red): 警告和重要通知
- 🚧 (yellow): 进行中或注意通知

### 处理 Notion 的限制

#### 超出限制时截断

默认情况下，包会尝试通过重新分配内容到多个块来解决这些问题。当无法解决时，`martian` 会截断输出以避免请求出错。

如果要禁用这种行为：

```python
options = {
    'notionLimits': {
        'truncate': False,
    },
}

markdown_to_blocks('input', options)
markdown_to_rich_text('input', options)
```

#### 手动处理限制相关的错误

可以设置一个回调函数，当某个项目超过 Notion 限制时调用：

```python
options = {
    'notionLimits': {
        'onError': lambda err: print(f"Error: {err}"),
    },
}

markdown_to_blocks('input', options)
markdown_to_rich_text('input', options)
```

### 处理图片

如果图片URL无效，Notion API会拒绝整个请求。`martian` 通过将无效链接的图片转换为文本来防止这个问题，以便请求成功，你可以稍后修复链接。

如果要禁用这种行为：

```python
options = {
    'strictImageUrls': False,
}

markdown_to_blocks('![](InvalidURL)', options)
```

### 非内联元素的处理

默认情况下，如果提供给 `markdown_to_rich_text` 的文本会产生一个或多个非内联元素，包会忽略这些元素，只解析段落。

你可以通过将 `nonInline` 选项设置为 `'throw'` 来在检测到非内联元素时抛出错误：

```python
markdown_to_rich_text('# Header\nAbc', {
    'nonInline': 'throw',  # 将抛出错误
})
```

## 🔗 与 Notion API 集成

```python
from martian import markdown_to_blocks
from notion_client import Client

# 初始化 Notion 客户端
notion = Client(auth="your_notion_api_token")

# 转换 Markdown
markdown_content = """
# 我的文档

这是一个示例文档。
"""

blocks = markdown_to_blocks(markdown_content)

# 创建 Notion 页面
notion.pages.create(
    parent={"database_id": "your_database_id"},
    properties={
        "title": [{"text": {"content": "新页面"}}]
    },
    children=blocks
)
```

## 🧪 开发和测试

```bash
# 克隆仓库
git clone https://github.com/xwEric/pymartian.git
cd pymartian

# 创建虚拟环境
python3.10 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 代码格式化
black src/ tests/
isort src/ tests/

# 类型检查
mypy src/
```

## 📋 要求

- Python 3.10 或更高版本
- `markdown-it-py>=3.0.0`
- `mdit-py-plugins>=0.4.0`

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

这是 TypeScript 版本 [@tryfabric/martian](https://github.com/tryfabric/martian) 的 Python 移植版本，原始项目由 [Fabric](https://tryfabric.com) 团队构建。

## 📚 相关链接

- [Notion API 文档](https://developers.notion.com/)
- [原始 TypeScript 版本](https://github.com/tryfabric/martian)
- [PyPI 项目页面](https://pypi.org/project/pymartian/)
- [问题跟踪](https://github.com/xwEric/pymartian/issues)

