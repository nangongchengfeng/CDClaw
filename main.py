# -*- coding: utf-8 -*-
# @Time    : 2023/4/10 15:00
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : main_optimized.py
# @Software: PyCharm
# 使用 CSDN API 获取文章，特使条件，必须使用 md 语法编辑器（富文本编辑器不行）

import os
import re
import uuid
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup

# 假设你的 cookie 存储在 config.py 文件中
# from config import cookie
# 为了示例能运行，这里定义一个假的 cookie，请替换为你自己的
from config import cookie

# --- 常量 ---
BASE_URL = "https://blog.csdn.net"
API_BASE_URL = "https://blog-console-api.csdn.net"
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'Cookie': cookie, # 从 config 或直接定义加载 Cookie
}
DOWNLOAD_DIR = 'download' # 定义下载子目录名称

# --- 辅助函数 ---

def _make_request(url: str, method: str = 'GET', headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Optional[requests.Response]:
    """
    发送 HTTP 请求的辅助函数。

    Args:
        url (str): 请求的 URL.
        method (str): HTTP 方法 (GET, POST, etc.). Defaults to 'GET'.
        headers (Optional[Dict[str, str]]): 请求头. Defaults to None (使用 DEFAULT_HEADERS).
        params (Optional[Dict[str, Any]]): URL 查询参数. Defaults to None.
        data (Optional[Dict[str, Any]]): 请求体数据 (用于 POST). Defaults to None.
        timeout (int): 请求超时时间（秒）. Defaults to 10.

    Returns:
        Optional[requests.Response]: requests 的响应对象，如果发生错误则返回 None.
    """
    final_headers = DEFAULT_HEADERS.copy()
    if headers:
        final_headers.update(headers)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=final_headers,
            params=params,
            data=data,
            timeout=timeout
        )
        response.raise_for_status()  # 对非 2xx 状态码抛出异常
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {url} - {e}")
        return None
    except Exception as e:
        print(f"请求时发生未知错误: {url} - {e}")
        return None

def get_article_publish_time(html_content: str) -> Optional[str]:
    """
    从文章 HTML 内容中解析发布时间。

    Args:
        html_content (str): 文章页面的 HTML 文本。

    Returns:
        Optional[str]: 格式化的时间字符串 (YYYY-MM-DD HH:MM:SS) 或 None。
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml') # 使用 lxml 解析器
        # 定位到包含时间的 span 标签，根据 CSDN 可能的结构调整选择器
        time_span = soup.select_one('.bar-content .time')
        if not time_span:
             # 尝试其他可能的选择器
             time_span = soup.select_one('span.time') # 更通用的选择器

        if time_span:
            time_value = time_span.get_text(strip=True)
            # 使用正则表达式提取标准时间格式
            match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', time_value)
            if match:
                return match.group(0)
            else:
                 # 尝试匹配仅日期格式
                 match_date = re.search(r'\d{4}-\d{2}-\d{2}', time_value)
                 if match_date:
                     return f"{match_date.group(0)} 00:00:00" # 如果只有日期，补充时间
                 print(f"警告: 在 '{time_value}' 中未找到标准时间格式 YYYY-MM-DD HH:MM:SS")
                 return None # 或者返回原始 time_value
        else:
            print("警告: 未在 HTML 中找到时间 span 标签。")
            return None
    except Exception as e:
        print(f"解析时间时出错: {e}")
        return None


def get_article_title(html_content: str) -> Optional[str]:
    """
    从文章 HTML 内容中解析标题，并移除 "-CSDN博客" 后缀。

    Args:
        html_content (str): 文章页面的 HTML 文本。

    Returns:
        Optional[str]: 清理后的文章标题或 None。
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml') # 使用 lxml 解析器
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            raw_title = title_tag.string.strip()
            # 清理标题，移除可能的后缀和非法字符
            cleaned_title = raw_title.removesuffix("-CSDN博客").strip()
            # 替换文件名中的非法字符
            cleaned_title = re.sub(r'[\\/*?:"<>|]', '_', cleaned_title)
            cleaned_title = cleaned_title.replace(" ", "_") # 将空格替换为下划线
            return cleaned_title
        else:
            print("警告: 未在 HTML 中找到 title 标签。")
            return None
    except Exception as e:
        print(f"解析标题时出错: {e}")
        return None

# --- 核心功能函数 ---

def fetch_and_save_article_md(csdn_user_id: str, article_id: str):
    """
    获取指定 CSDN 文章的 Markdown 内容并保存到本地文件。

    Args:
        csdn_user_id (str): CSDN 用户 ID (用于创建目录)。
        article_id (str): CSDN 文章 ID。
    """
    print(f"开始处理文章 ID: {article_id}")

    # 1. 获取文章页面 HTML 以提取标题和时间
    article_url = f"{BASE_URL}/{csdn_user_id}/article/details/{article_id}"
    print(f"正在访问文章页面: {article_url}")
    response_html = _make_request(article_url)

    if not response_html or not response_html.text:
        print(f"错误: 无法获取文章页面 HTML: {article_url}")
        return

    html_content = response_html.text

    # 2. 解析标题和时间
    article_title = get_article_title(html_content)
    publish_time = get_article_publish_time(html_content)

    if not article_title:
        print(f"错误: 无法解析文章标题，使用文章 ID 作为文件名。")
        article_title = f"article_{article_id}" # 提供一个备用标题
    if not publish_time:
        print(f"警告: 无法解析发布时间，Markdown 头信息中将缺少日期。")
        publish_time = "YYYY-MM-DD HH:MM:SS" # 提供一个占位符

    print(f"获取到标题: {article_title}")
    print(f"获取到时间: {publish_time}")

    # 3. 调用 API 获取 Markdown 内容和其他元数据
    api_url = f"{API_BASE_URL}/v1/editor/getArticle"
    params = {"id": article_id}
    print(f"正在调用 API 获取 Markdown: {api_url} (参数: id={article_id})")
    response_api = _make_request(api_url, params=params) # GET 请求通常用 params

    if not response_api:
        print(f"错误: 调用 API 失败: {api_url}")
        return

    try:
        api_data = response_api.json()
    except requests.exceptions.JSONDecodeError:
        print(f"错误: API 响应不是有效的 JSON: {api_url}")
        print(f"响应内容: {response_api.text[:200]}...") # 打印部分响应内容帮助调试
        return

    # 4. 解析 API 返回的数据
    if api_data.get('code') != 200 or 'data' not in api_data:
        print(f"错误: API 返回错误或数据格式不正确。")
        print(f"API 响应: {api_data}")
        return

    article_data = api_data['data']
    markdown_content = article_data.get('markdowncontent', '')
    tags = article_data.get('tags', '')
    categories = article_data.get('categories', '')
    description = article_data.get('description', '')
    # API 返回的 title 可能与 HTML 中的 title 不同，这里可以选择使用哪个
    # title_from_api = article_data.get('title', article_title) # 可以用 API 的 title 覆盖

    if not markdown_content:
        print(f"警告: API 未返回 Markdown 内容。文章可能不是 Markdown 格式或获取失败。")
        # 可以选择是停止还是创建一个空文件或只包含头信息的文件
        # return # 如果没有内容则不保存

    # 5. 构建 Markdown 文件头部 (Front Matter)
    markdown_header = f"""---
title: {article_title}
date: {publish_time}
tags: [{tags}] # 通常 tags 是列表形式
categories: [{categories}] # categories 也常是列表
description: "{description}"
---
\n\n""" # description 加引号避免特殊字符问题，加换行

    # 移除 CSDN 的目录标记
    content_without_toc = markdown_content.replace("@[toc]", "").strip()

    # 6. 准备保存路径并创建目录
    # 使用 csdn_user_id 和 download 目录名构建路径
    save_dir = os.path.join('.', csdn_user_id, DOWNLOAD_DIR)
    os.makedirs(save_dir, exist_ok=True) # 递归创建目录，如果存在则忽略

    # 文件名使用清理后的标题
    file_path = os.path.join(save_dir, f"{article_title}.md")

    # 7. 写入文件
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_header)
            f.write(content_without_toc)
        print(f"成功: 文章已保存到: {file_path}")
    except IOError as e:
        print(f"错误: 写入文件失败: {file_path} - {e}")
    except Exception as e:
        print(f"错误: 保存文件时发生未知错误: {file_path} - {e}")


# --- 主程序入口 ---

def main():
    """
    主执行函数
    """
    csdn_user_id = 'heian_99'  # CSDN 用户ID
    article_id_to_fetch = '147592515' # 需要下载的文章ID

    # 检查 Cookie 是否已配置
    if cookie == "YOUR_CSDN_COOKIE_HERE" or not cookie:
         print("错误：请在代码中或 config.py 文件里设置你的 CSDN Cookie！")
         return

    # 创建用户根目录 (可选，fetch_and_save_article_md 中也会创建)
    # user_dir = f'./{csdn_user_id}'
    # if not os.path.exists(user_dir):
    #     try:
    #         os.mkdir(user_dir)
    #     except OSError as e:
    #         print(f"创建目录 {user_dir} 失败: {e}")
    #         return # 如果根目录创建失败，则退出

    # 调用核心函数下载文章
    fetch_and_save_article_md(csdn_user_id, article_id_to_fetch)
    print("-" * 20)
    print("处理完成。")


if __name__ == '__main__':
    main()
