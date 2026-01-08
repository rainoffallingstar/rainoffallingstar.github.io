#!/usr/bin/env python3
"""
从OPML文件中提取PubMed相关的RSS源

支持多种使用方式：
1. 自动扫描subscribe/文件夹下的所有.opml文件
2. 指定目录扫描：python extract_pubmed_feeds.py /path/to/opml/dir
3. 指定文件列表：python extract_pubmed_feeds.py file1.opml file2.opml
"""

import json
import sys
import xml.etree.ElementTree as ET
from glob import glob
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


def extract_pubmed_feeds_from_files(opml_files, output_path):
    """
    从指定的OPML文件列表中提取PubMed RSS源

    Args:
        opml_files: OPML文件路径列表
        output_path: 输出JSON文件路径

    Returns:
        list: 提取的RSS源列表
    """
    if not opml_files:
        print("错误: 未提供任何OPML文件")
        return []

    print(f"\n处理 {len(opml_files)} 个OPML文件:")
    for idx, opml_file in enumerate(opml_files, 1):
        print(f"  {idx}. {Path(opml_file).name}")

    all_feeds = []
    file_stats = {}

    # 处理每个OPML文件
    for idx, opml_file in enumerate(opml_files, 1):
        opml_path = Path(opml_file)
        print(f"\n[{idx}/{len(opml_files)}] 处理 {opml_path.name}...", end=" ")

        try:
            tree = ET.parse(opml_path)
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
            file_stats[opml_path.name] = len(feeds_from_file)
            print(f"✓ 找到 {len(feeds_from_file)} 个PubMed源")

        except Exception as e:
            print(f"✗ 处理失败: {e}")
            file_stats[opml_path.name] = 0

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
        # 检查第一个参数是否为目录
        first_arg = Path(sys.argv[1])

        # 如果只有一个参数且为目录，则扫描目录
        if len(sys.argv) == 2 and first_arg.is_dir():
            opml_dir = first_arg
            output_file = default_output_file

        # 如果有多个参数，或第一个参数是文件
        else:
            # 检查是否包含输出文件参数（倒数第二个是目录，倒数一个是文件）
            if (
                len(sys.argv) >= 3
                and not Path(sys.argv[-1]).is_dir()
                and not sys.argv[-1].endswith(".opml")
            ):
                # 最后一个参数是输出文件
                opml_files = sys.argv[1:-1]
                output_file = Path(sys.argv[-1])
            else:
                # 所有参数都是OPML文件
                opml_files = sys.argv[1:]
                output_file = default_output_file

            # 展开通配符
            expanded_files = []
            for pattern in opml_files:
                expanded_files.extend(glob(pattern))
            opml_files = expanded_files

            # 验证所有文件存在
            missing_files = [f for f in opml_files if not Path(f).exists()]
            if missing_files:
                print(f"错误: 以下文件不存在:")
                for f in missing_files:
                    print(f"  - {f}")
                sys.exit(1)

            # 如果只有一个文件且是目录
            if len(opml_files) == 1 and Path(opml_files[0]).is_dir():
                opml_dir = Path(opml_files[0])
                return extract_pubmed_feeds_from_dir(opml_dir, output_file)

            # 处理文件列表
            return extract_pubmed_feeds_from_files(opml_files, output_file)
    else:
        # 无参数，使用默认目录
        opml_dir = default_opml_dir
        output_file = default_output_file

    # 确保目录存在
    if not opml_dir.exists():
        print(f"错误: 目录 {opml_dir} 不存在")
        print(f"\n请确保OPML文件位于 {default_opml_dir} 目录下，或指定自定义目录：")
        print(f"  python extract_pubmed_feeds.py <目录路径>")
        print(f"或指定文件列表：")
        print(f"  python extract_pubmed_feeds.py file1.opml file2.opml")
        sys.exit(1)

    # 提取RSS源
    extract_pubmed_feeds_from_dir(opml_dir, output_file)


if __name__ == "__main__":
    main()
