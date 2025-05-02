# -*- coding: utf-8 -*-
"""
CSDN文章处理工具
用于下载和处理CSDN博客文章中的图片，整理文章元数据
"""
import os
import random
import re
from datetime import datetime
import frontmatter
import requests

# 全局变量设置
CWD = os.getcwd()
TARGET_DIR = os.path.join(CWD, 'heian_99', 'download')
IMAGE_DIR = 'image'
OUTPUT_BASE_DIR = 'csdn'


def download_image(url):
    """
    从给定的URL下载图片，并保存到image目录下
    
    参数:
        url: 图片的URL地址
    
    返回:
        成功返回保存后的相对路径，失败返回None
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"下载图片失败。状态码: {response.status_code}")
        return None
    
    # 确保图片保存目录存在
    os.makedirs(IMAGE_DIR, exist_ok=True)
    
    # 从URL提取文件名
    filename = extract_filename_from_url(url)
    
    # 保存图片
    filepath = f'{IMAGE_DIR}/{filename}'
    with open(filepath, 'wb') as f:
        f.write(response.content)
    
    # 返回图片的相对路径
    return f"../../{IMAGE_DIR}/{filename}"


def extract_filename_from_url(url):
    """
    从URL中提取合适的文件名
    
    参数:
        url: 图片的URL
    
    返回:
        提取出的文件名
    """
    # 处理CSDN特定图片
    if 'imgconvert.csdnimg.cn/' in url:
        return url.split('/')[-1]
    
    # 使用正则表达式寻找文件名
    if len(url) > 55:
        matches = re.findall(r'/([\w-]+\.(?:jpg|png|gif|jpeg))', url)
        if matches:
            return matches[-1]
    
    # 默认使用URL最后一部分作为文件名
    filename = url.split('/')[-1]
    
    # 确保文件名有合适的扩展名
    if not re.search(r'\.(?:jpg|png|gif|jpeg)$', filename):
        filename += '.jpg'
    
    return filename


def get_random_title_image():
    """
    随机获取一张标题图片的URL
    
    返回:
        随机标题图片的相对路径
    """
    # 生成数字列表(01-77)
    nums = [str(i + 1).zfill(2) for i in range(77)]
    selected_num = random.choice(nums)
    return f"../../title_pic/{selected_num}.jpg"


def ensure_dir_exists(dirpath):
    """
    确保目录存在，不存在则创建
    
    参数:
        dirpath: 目录路径
    """
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        print(f'创建目录: {dirpath}')


def clean_text(text, remove_spaces=False, remove_brackets=False):
    """
    清理文本，可选择去除空格和括号
    
    参数:
        text: 待处理的文本
        remove_spaces: 是否移除空格
        remove_brackets: 是否移除括号和冒号
        
    返回:
        处理后的文本
    """
    if remove_spaces:
        text = text.replace(' ', '')
    if remove_brackets:
        text = text.replace('[', '').replace(']', '').replace(':', '-')
    return text


def extract_summary(content, max_length=100):
    """
    从文章内容中提取摘要
    
    参数:
        content: 文章内容
        max_length: 摘要最大长度
        
    返回:
        提取的摘要
    """
    summary = content.split('<!--more-->')[-1]
    summary_pattern = re.compile('[\u4e00-\u9fa5，；：！？。、]+')
    chinese_text = ''.join(summary_pattern.findall(summary))
    return chinese_text[:max_length] + '。。。。。。。'


def process_markdown_file(filename):
    """
    处理单个Markdown文件，下载其中的图片并更新元数据
    
    参数:
        filename: 要处理的Markdown文件名
    """
    filepath = os.path.join(TARGET_DIR, filename)
    
    # 读取文件内容
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取并处理YAML前置元数据
    metadata = process_metadata(content, filename)
    
    # 提取图片URL并下载替换
    updated_content = download_and_replace_images(content)
    
    # 将修改后的内容写入新文件
    output_dir = f'{OUTPUT_BASE_DIR}/{metadata["year"]}/'
    ensure_dir_exists(output_dir)
    clean_filename = clean_text(filename, remove_spaces=True)
    
    # 构建新的元数据部分
    metadata_str_new = frontmatter.dumps(metadata["data"])
    
    # 替换原始元数据部分
    content_new = updated_content[:metadata["start"]] + metadata_str_new + updated_content[metadata["end"] + 3:]
    
    # 写入新文件
    with open(os.path.join(output_dir, clean_filename), mode="w", encoding="utf-8") as f:
        f.write(content_new)
    
    print(f"处理完成: {filename}")


def process_metadata(content, filename):
    """
    处理Markdown文件的元数据
    
    参数:
        content: 文件内容
        filename: 文件名
        
    返回:
        包含元数据的字典
    """
    # 提取YAML前置元数据
    metadata_start = content.find('---')
    metadata_end = content.find('---', metadata_start + 3)
    metadata_str = content[metadata_start:metadata_end + 3]
    
    # 解析YAML元数据
    metadata = frontmatter.loads(metadata_str.replace('#', ''))
    
    # 清理和标准化元数据
    title = clean_text(metadata['title'], remove_brackets=True)
    
    # 处理标签
    if metadata.get('tags') is not None:
        tags_list = [tag.strip() for tag in metadata['tags'].replace('#', '').split(' ')]
    else:
        tags_list = ['技术记录']
    
    # 处理分类
    if metadata.get('categories') is not None:
        categories_list = [tag.strip() for tag in metadata['categories'].replace('#', '').split(' ')]
    else:
        categories_list = ['技术记录']
    
    # 更新元数据
    metadata['author'] = "南宫乘风"
    metadata['title'] = title
    metadata['categories'] = categories_list
    metadata['tags'] = tags_list
    metadata['image'] = get_random_title_image()
    
    # 保持原始描述，如果没有则提取摘要
    if not metadata.get('description'):
        metadata['description'] = extract_summary(content)
    
    # 生成slug
    date_obj = datetime.strptime(str(metadata['date']), '%Y-%m-%d %H:%M:%S')
    metadata['slug'] = date_obj.strftime('%Y%m%d%H%M')
    
    # 获取年份用于目录结构
    year = date_obj.year
    
    return {
        "data": metadata,
        "start": metadata_start,
        "end": metadata_end,
        "year": year
    }


def download_and_replace_images(content):
    """
    下载并替换Markdown中的所有图片链接
    
    参数:
        content: Markdown内容
        
    返回:
        更新后的内容
    """
    # 查找所有图片链接
    pattern = r'!\[[^\]]*\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    # 逐个下载并替换图片链接
    updated_content = content
    for url in matches:
        print(f"处理图片: {url}")
        new_url = download_image(url)
        if new_url:
            print(f"替换为: {new_url}")
            # 直接替换URL部分，保留原始的图片描述文本
            updated_content = updated_content.replace(url, new_url)
    
    return updated_content


def list_files(dir_path):
    """
    列出目录中的所有文件
    
    参数:
        dir_path: 目录路径
        
    返回:
        文件名列表
    """
    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f"路径不存在: {dir_path!r}")
    
    return [filename for filename in os.listdir(dir_path) 
            if os.path.isfile(os.path.join(dir_path, filename))]


def main():
    """
    主函数，处理目标目录中的所有Markdown文件
    """
    try:
        # 获取目标目录中的所有文件
        file_list = list_files(TARGET_DIR)
        print(f"找到 {len(file_list)} 个文件需要处理")
        
        # 处理每个文件
        for filename in file_list:
            print(f"开始处理: {filename}")
            process_markdown_file(filename)
            
        print("所有文件处理完成")
    
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")


if __name__ == "__main__":
    main()