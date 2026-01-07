#!/usr/bin/env python3
"""
从OPML文件中提取PubMed相关的RSS源
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_pubmed_feeds(opml_path, output_path):
    """
    从OPML文件中提取所有包含'pubmed'的RSS源，保存为JSON列表
    """
    tree = ET.parse(opml_path)
    root = tree.getroot()

    feeds = []

    def find_outlines(element):
        for child in element:
            # 处理命名空间 - 获取最后一个部分作为本地名
            tag = child.tag
            if "}" in tag:
                tag = tag.rsplit("}", 1)[-1] if "}" in tag else tag

            if tag == "outline":
                xml_url = child.get("xmlUrl")
                title = child.get("title", "")
                text = child.get("text", "")

                if xml_url and "pubmed" in xml_url.lower():
                    feeds.append({"url": xml_url, "title": title or text})
                    print(f"  找到: {title or text[:50]}")

            # 递归查找子元素
            find_outlines(child)

    find_outlines(root)

    # 确保输出目录存在
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 保存为JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feeds, f, indent=2, ensure_ascii=False)

    print(f"找到 {len(feeds)} 个PubMed RSS源")
    print(f"已保存到: {output_path}")

    return feeds


if __name__ == "__main__":
    import sys

    opml_file = sys.argv[1] if len(sys.argv) > 1 else "scripts/follow.opml"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "scripts/pubmed_feeds.json"

    extract_pubmed_feeds(opml_file, output_file)
