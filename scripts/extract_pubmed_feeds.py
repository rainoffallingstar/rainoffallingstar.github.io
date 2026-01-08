#!/usr/bin/env python3
"""
从OPML文件中提取PubMed相关的RSS源

支持多个OPML文件：
- 自动扫描subscribe/文件夹下的所有.opml文件
- 批量提取并去重PubMed RSS源
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_pubmed_feeds_from_dir(opml_dir, output_path):
    """
    从指定目录中的所有OPML文件中提取PubMed RSS源

    Args:
        opml_dir: 包含OPML文件的目录路径
        output_path: 输出JSON文件路径

    Returns:
        list: 提取的RSS源列表
    """
    opml_dir = Path(opml_dir)

    # 查找所有OPML文件
    opml_files = sorted(opml_dir.glob("*.opml"))

    if not opml_files:
        print(f"在 {opml_dir} 目录下未找到任何 .opml 文件")
        return []

    print(f"\n开始扫描 {opml_dir} 文件夹...")
    print(f"找到 {len(opml_files)} 个OPML文件:")
    for opml_file in opml_files:
        print(f"  ✓ {opml_file.name}")
    print()

    all_feeds = []
    file_stats = {}

    # 处理每个OPML文件
    for idx, opml_file in enumerate(opml_files, 1):
        print(f"[{idx}/{len(opml_files)}] 处理 {opml_file.name}...", end=" ")

        try:
            tree = ET.parse(opml_file)
            root = tree.getroot()

            feeds_from_file = []

            def find_outlines(element):
                for child in element:
                    # 处理命名空间
                    tag = child.tag
                    if "}" in tag:
                        tag = tag.rsplit("}", 1)[-1] if "}" in tag else tag

                    if tag == "outline":
                        xml_url = child.get("xmlUrl")
                        title = child.get("title", "")
                        text = child.get("text", "")

                        if xml_url and "pubmed" in xml_url.lower():
                            feed = {"url": xml_url, "title": title or text}
                            feeds_from_file.append(feed)
                            all_feeds.append(feed)

                    # 递归查找子元素
                    find_outlines(child)

            find_outlines(root)
            file_stats[opml_file.name] = len(feeds_from_file)
            print(f"✓ 找到 {len(feeds_from_file)} 个PubMed源")

        except Exception as e:
            print(f"✗ 处理失败: {e}")
            file_stats[opml_file.name] = 0

    # 去重 - 基于URL
    print("\n去重处理...")
    seen_urls = set()
    unique_feeds = []

    for feed in all_feeds:
        if feed["url"] not in seen_urls:
            seen_urls.add(feed["url"])
            unique_feeds.append(feed)

    # 显示统计信息
    print("\n" + "=" * 60)
    print("提取结果:")
    for filename, count in file_stats.items():
        print(f"  {filename}: {count} 个PubMed源")

    print(f"\n去重统计:")
    print(f"  去重前: {len(all_feeds)} 个RSS源")
    print(f"  去重后: {len(unique_feeds)} 个唯一RSS源")
    print(f"  去除重复: {len(all_feeds) - len(unique_feeds)} 个")

    # 确保输出目录存在
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 保存为JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique_feeds, f, indent=2, ensure_ascii=False)

    print(f"\n已保存到: {output_path}")
    print("=" * 60)

    return unique_feeds


def main():
    """主函数"""
    # 确定OPML目录和输出路径
    script_dir = Path(__file__).parent

    # 默认目录
    default_opml_dir = script_dir / "subscribe"
    default_output_file = script_dir / "pubmed_feeds.json"

    # 解析命令行参数
    if len(sys.argv) >= 2:
        opml_dir = Path(sys.argv[1])
    else:
        opml_dir = default_opml_dir

    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = default_output_file

    # 确保目录存在
    if not opml_dir.exists():
        print(f"错误: 目录 {opml_dir} 不存在")
        print(f"\n请确保OPML文件位于 {default_opml_dir} 目录下，或指定自定义目录：")
        print(f"  python extract_pubmed_feeds.py <自定义目录>")
        sys.exit(1)

    # 提取RSS源
    extract_pubmed_feeds_from_dir(opml_dir, output_file)


if __name__ == "__main__":
    main()
