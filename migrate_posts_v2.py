#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移剩余的 Jekyll 博客文章到 Tufted Blog
从 commit 751b948 获取原始文章并转换为 Typst 格式
"""

import os
import re
import subprocess
from pathlib import Path

# 需要迁移的文章列表
POSTS_TO_MIGRATE = [
    "2016-4-20-城府.md",
    "2017-07-02-吃瓜群众视角下的议论文.md",
    "2018-05-23-解剖学复习材料.md",
    "2018-06-01-有机.md",
    "2018-09-19-脑出⾎后⾎肿周围脑组织神经细胞⾃噬现象的观察.md",
    "2018-09-27-心动的物理学原理.md",
    "2018-10-06-从单标记到多标记的免疫荧光技术.md",
    "2018-12-19-马尾记.md",
    "2019-01-14-The basic principal of physiology.md",
    "2019-02-14-免疫胶体金电镜技术的操作与原理.md",
    "2020-01-03-Pathology Lecture Notes.md",
    "2020-05-20-医大毕业考中心题库.md",
    "2020-08-23-生物竞赛路标系统2.0.md",
    "2021-05-20-临床问诊指北.md",
    "2021-08-24-肾肿瘤论文检索与阅读.md",
    "2021-11-22-Automated Classification of Papillary Renal Cell Carcinoma and Chromophobe Renal Cell Carcinoma Based on a Small Computed Tomography Imaging Dataset Using Deep Learning.md",
    "2021-11-30-japan prince.md",
    "2021-12-01-The collection.md",
    "2021-12-05-thelastlibrary.md",
    "2021-12-05-利用casaos将deepin打造为一个简易的nas系统.md",
    "2021-12-05-英语语料库.md",
    "2022-01-08-mskcc分子分型实验步骤翻译（部分）.md",
    "2022-03-09-新冠肺炎预试验.md",
    "2022-04-09-面试非专业问题指北.md",
    "2022-05-18-Paired Mass Distance(PMD) analysis for MS based non-targeted analysis.md",
    "2022-06-18-在DL领域中乳腺超声数据的处理探究.md",
    "2022-09-03-打包属于自己数据的PASCAL-VOC-2012目标检测数据集.md",
    "2022-09-20-awesom-eGNNwithmedical.md",
]

def get_original_post(filename):
    """从 commit 751b948 获取原始文章内容"""
    try:
        result = subprocess.run(
            ["git", "show", f"751b948:_posts/{filename}"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"[ERROR] Cannot get {filename}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception getting {filename}: {e}")
        return None

def convert_markdown_to_typst(content, title):
    """将 Markdown 内容转换为 Typst 格式"""
    lines = content.split('\n')

    # 跳过 YAML front matter
    in_front_matter = False
    start_index = 0
    dash_count = 0

    for i, line in enumerate(lines):
        if line.strip() == "---":
            dash_count += 1
            if dash_count == 1:
                start_index = i + 1
            elif dash_count == 2:
                # 找到第二个 ---，这才是正文开始
                lines = lines[i+1:]
                break

    content = '\n'.join(lines)

    # 标题转换
    content = re.sub(r'^####\s+(.+)$', r'=== \1', content, flags=re.MULTILINE)
    content = re.sub(r'^###\s+(.+)$', r'== \1', content, flags=re.MULTILINE)
    content = re.sub(r'^##\s+(.+)$', r'= \1', content, flags=re.MULTILINE)

    # 粗体转换（避免重复转换）
    content = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', content)

    # 链接转换
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'#link("\2")[\1]', content)

    # 图片转换 - 添加 imgs/ 前缀
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'#image("imgs/\2")', content)

    # 代码块转换 - 使用 #block.raw
    content = re.sub(r'```(\w+)?', r'#block.raw("', content)
    content = re.sub(r'```', r'")', content)

    return content

def sanitize_filename(filename):
    """清理文件名，用于创建目录"""
    # 移除 .md 扩展名
    name = filename.replace('.md', '')
    return name

def extract_title(filename):
    """从文件名提取标题"""
    name = filename.replace('.md', '')
    # 移除日期前缀 YYYY-MM-DD-
    parts = name.split('-', 3)
    if len(parts) > 3:
        return parts[3]
    return name

def migrate_post(filename):
    """迁移单篇文章"""
    print(f"Processing: {filename}")

    # 获取原始内容
    content = get_original_post(filename)
    if not content:
        return False

    # 创建目录名
    dir_name = sanitize_filename(filename)
    output_dir = Path(f"content/Blog/{dir_name}")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 提取标题
    title = extract_title(filename)

    # 转换内容
    typst_content = convert_markdown_to_typst(content, title)

    # 创建 index.typ 文件
    index_file = output_dir / "index.typ"

    # 写入文件头部 - 使用变量避免常量突变问题
    header = f'''#import "../../../config.typ": template, tufted
#show: template.with(title: "{title}").with(lang: "zh")

== {title}

'''

    index_file.write_text(header + typst_content, encoding="utf-8")

    print(f"[OK] Created: {index_file}")
    return True

def main():
    """主迁移流程"""
    print("=" * 60)
    print("Migrating remaining Jekyll blog posts to Tufted Blog")
    print("=" * 60)

    success_count = 0
    fail_count = 0

    for filename in POSTS_TO_MIGRATE:
        if migrate_post(filename):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"Migration complete!")
    print(f"Success: {success_count} posts")
    print(f"Failed: {fail_count} posts")
    print("=" * 60)

    if fail_count == 0:
        print("\nNext steps:")
        print("  1. Check converted files")
        print("  2. Copy images if needed")
        print("  3. Run: python build.py build --force")
        print("  4. Local preview")

if __name__ == "__main__":
    main()
