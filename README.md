# CDClaw - CSDN 博客文章爬取工具

## 项目简介

CDClaw 是一个专门用于爬取 CSDN 博客文章的 Python 工具，支持将文章转换为 Markdown 格式并下载相关图片。该工具特别适合需要将 CSDN 博客文章迁移到 Hugo 等静态博客平台的用户。

## 功能特性

- 支持爬取 CSDN 博客文章并转换为 Markdown 格式
- 自动下载文章中的图片并本地化
- 支持生成 Hugo 博客所需的 Front Matter 信息
- 自动处理文章元数据（标题、日期、标签、分类等）
- 支持批量文章处理
- 图片本地化存储，避免外链失效

## 目录结构

```
.
├── fetch_blog.py    # CSDN文章爬取核心模块
├── hugo_local.py    # Hugo格式转换和图片处理模块
├── config.py        # 配置文件（需要自行创建）
├── requirements.txt  # 项目依赖
├── csdn/            # Hugo格式文章输出目录
├── image/           # 下载的图片存储目录
└── heian_99/       # 原始文章存储目录
```

## 环境要求

- Python >= 3.12
- 相关 Python 包依赖（见 requirements.txt）

## 安装说明

1. 克隆项目到本地

```bash
git clone https://github.com/nangongchengfeng/CDClaw.git
cd CDClaw
```

2. 安装依赖包

```bash
pip install -r requirements.txt
```

3. 创建配置文件
   在项目根目录创建`config.py`文件，添加以下内容：

```python
cookie = "YOUR_CSDN_COOKIE_HERE"  # 替换为你的CSDN Cookie
```

## 使用方法

### 1. 爬取 CSDN 文章

```python
# 修改fetch_blog.py中的配置
csdn_user_id = 'your_csdn_id'  # 设置CSDN用户ID
article_id_to_fetch = 'article_id'  # 设置要爬取的文章ID

# 运行爬取脚本
python fetch_blog.py
```

### 2. 处理文章和图片

```python
# 运行Hugo格式转换脚本
python hugo_local.py
```

## 主要模块说明

### fetch_blog.py

- 负责从 CSDN 获取文章内容
- 提取文章标题、发布时间、标签等元数据
- 保存为 Markdown 格式
- 支持处理文章中的代码块和格式

### hugo_local.py

- 处理 Markdown 文件的图片下载
- 转换图片链接为本地路径
- 生成 Hugo 兼容的 Front Matter
- 支持批量处理文章

## 注意事项

1. 使用前需要配置正确的 CSDN Cookie
2. 仅支持使用 Markdown 编辑器编写的 CSDN 文章
3. 图片下载可能受网络条件影响
4. 建议遵守 CSDN 的使用规范和爬虫规则

## 依赖包列表

- beautifulsoup4==4.13.4
- bs4==0.0.2
- frontmatter==3.0.8
- lxml==5.4.0
- python-frontmatter==1.1.0
- requests==2.32.3
- PyYAML==5.1

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 更新日志

### v0.1.0

- 初始版本发布
- 支持基本的文章爬取和转换功能
- 实现图片下载和本地化处理
