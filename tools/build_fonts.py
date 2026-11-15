#!/usr/bin/env python3
"""构建本站自托管的手写字体。

参考站点（astro-air）的视觉核心是手写字形。这里把自由字体处理后放进
``assets/fonts/``，全部为 SIL Open Font License 1.1：

* **Xiaolai**（霞鹜小赖）—— 中文正文字形，毛笔手写风，与参考站
  所用字体同源（SetoFont → KoseFont）。完整字体 22 MB；这里按内容
  实际用字（再加 GB2312 一级常用字）做子集，得到约 850 KB 的 woff2。
* **Excalifont** —— 拉丁字母与数字，笔触与中文手写体协调。
* **LXGW WenKai Mono** 的 ASCII 子集 —— 代码块，保留书写气质。

用法::

    uv run --with fonttools --with brotli python3 tools/build_fonts.py

脚本可重复执行：源字体缓存在 ``tools/.cache/``，产物确定。
``assets/fonts.css`` 由脚本生成，不要手改。
"""

from __future__ import annotations

import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHARSET_FILE = ROOT / "tools" / "font-charset.txt"
CONTENT_DIR = ROOT / "content"

# 正文之外总要有的字符：ASCII、拉丁补充、中文标点与常用符号。
BASE_CHARS = (
    "".join(chr(cp) for cp in range(0x20, 0x7F))
    + "".join(chr(cp) for cp in range(0xA0, 0x100))
    + "　、。〈〉《》「」『』【】〔〕〖〗〘〙–—‘’“”…·‰′″‹›※"
    + "→←↑↓⇆≤≥±×÷°℃ⅠⅡⅢⅣⅦ①②③④⑤⑥⑦⑧⑨⑴⑵⑶⑷⑸⑹⚠❌➢⬆"
)
CACHE_DIR = ROOT / "tools" / ".cache"
FONT_DIR = ROOT / "assets" / "fonts"
CSS_FILE = ROOT / "assets" / "fonts.css"

OFL_URL = "https://raw.githubusercontent.com/lxgw/kose-font/master/OFL.txt"

# 逻辑名 -> (下载地址, 缓存文件名)
SOURCES = {
    "xiaolai": (
        "https://github.com/lxgw/kose-font/releases/download/v3.126/Xiaolai-Regular.ttf",
        "Xiaolai-Regular.ttf",
    ),
    "wenkai-mono": (
        "https://github.com/lxgw/LxgwWenKai/releases/download/v1.530/LXGWWenKaiMono-Regular.ttf",
        "LXGWWenKaiMono-Regular.ttf",
    ),
}

FAMILY_CJK = "Xiaolai"

# 中文字形不做分块。曾按 Unicode 每 512 码位切块，但中文文章的字分散在
# 整个 CJK 区间，一页几乎会命中所有块 —— 请求数涨到 40 多个，总字节不变。
# 单个 ~870 KB 的 woff2（gzip 后更小）+ font-display: swap 更划算。
FAMILY_MONO = "WenKai Mono"

# 手写体拉丁字母（Excalifont）随仓库提供，只做转发声明
EXCALIFONT_RULE = (
    "@font-face {\n"
    '  font-family: "Excalifont";\n'
    "  font-style: normal;\n"
    "  font-weight: 400;\n"
    "  font-display: swap;\n"
    '  src: url("/assets/fonts/excalifont/Excalifont-Regular.woff2") format("woff2");\n'
    "  unicode-range: U+0020-007E, U+00A0-00FF, U+2010-2027, U+2030-205E,\n"
    "    U+20A0-20CF, U+2100-214F, U+2190-21FF, U+2200-22FF;\n"
    "}"
)

# 拉丁与标点：单独成文件，纯英文页面不必下载中文字形
LATIN_LIMIT = 0x2E80


def collect_charset() -> set[str]:
    """汇总站点实际用字 + GB2312 一级常用字。

    GB2312 一级字表覆盖 3755 个最常用汉字，加上它是为了让新写的文章
    大概率不需要重新生成字体。
    """
    chars = set(BASE_CHARS)

    for typ_file in CONTENT_DIR.rglob("*.typ"):
        chars.update(typ_file.read_text(encoding="utf-8"))

    for high in range(0xB0, 0xD8):
        for low in range(0xA1, 0xFF):
            try:
                chars.add(bytes([high, low]).decode("gb2312"))
            except UnicodeDecodeError:
                continue

    return {char for char in chars if char.isprintable() or char == " "}


def download(url: str, cache_name: str) -> pathlib.Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    target = CACHE_DIR / cache_name
    if not target.exists() or target.stat().st_size < 1_000_000:
        print(f"  ↓ {url}")
        urllib.request.urlretrieve(url, target)
    return target


def to_ranges(codepoints: list[int]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = prev = codepoints[0]
    for cp in codepoints[1:]:
        if cp == prev + 1:
            prev = cp
            continue
        ranges.append((start, prev))
        start = prev = cp
    ranges.append((start, prev))
    return ranges


def unicode_range(codepoints: list[int]) -> str:
    return ", ".join(
        f"U+{a:04X}" if a == b else f"U+{a:04X}-{b:04X}" for a, b in to_ranges(codepoints)
    )


def subset_to(source: pathlib.Path, codepoints: list[int], output: pathlib.Path) -> int:
    from fontTools import subset

    subset.main(
        [
            str(source),
            f"--text={''.join(chr(cp) for cp in codepoints)}",
            f"--output-file={output}",
            "--flavor=woff2",
            "--layout-features=*",
            "--no-hinting",
            "--desubroutinize",
            "--drop-tables+=DSIG",
            "--name-IDs=*",
            "--passthrough-tables",
        ]
    )
    return output.stat().st_size


def face(family: str, weight: str, path: str, ranges: str) -> str:
    return (
        "@font-face {\n"
        f'  font-family: "{family}";\n'
        "  font-style: normal;\n"
        f"  font-weight: {weight};\n"
        "  font-display: swap;\n"
        f'  src: url("{path}") format("woff2");\n'
        f"  unicode-range: {ranges};\n"
        "}"
    )


def build_cjk(source: pathlib.Path, codepoints: list[int]) -> list[str]:
    out_dir = FONT_DIR / "xiaolai"
    out_dir.mkdir(parents=True, exist_ok=True)

    latin = [cp for cp in codepoints if cp < LATIN_LIMIT]
    cjk = [cp for cp in codepoints if cp >= LATIN_LIMIT]

    latin_size = subset_to(source, latin, out_dir / "latin.woff2")
    cjk_size = subset_to(source, cjk, out_dir / "cjk.woff2")
    print(
        f"  ✓ {FAMILY_CJK}: latin {latin_size / 1024:.0f} KB ({len(latin)} glyphs), "
        f"cjk {cjk_size / 1e3:.0f} KB ({len(cjk)} glyphs)"
    )

    return [
        face(FAMILY_CJK, "400", "/assets/fonts/xiaolai/latin.woff2", unicode_range(latin)),
        # 手写体只有一个字重，正文与粗体都用它（合成加粗会糊）
        face(FAMILY_CJK, "400 700", "/assets/fonts/xiaolai/cjk.woff2", unicode_range(cjk)),
    ]


def build_mono(source: pathlib.Path) -> str:
    out_dir = FONT_DIR / "mono"
    out_dir.mkdir(parents=True, exist_ok=True)
    cps = (
        list(range(0x20, 0x7F))
        + [0xA0, 0xB0, 0xD7, 0xF7]
        + list(range(0x2000, 0x2070))
        + list(range(0x2190, 0x21A0))
        + list(range(0x2500, 0x2580))
        + [0x3001, 0x3002, 0x300C, 0x300D, 0x300E, 0x300F, 0xFF08, 0xFF09]
    )
    size = subset_to(source, cps, out_dir / "mono.woff2")
    print(f"  ✓ WenKai Mono: {size / 1024:.0f} KB")
    return face(
        FAMILY_MONO,
        "400 700",
        "/assets/fonts/mono/mono.woff2",
        unicode_range(cps),
    )


def main() -> int:
    charset = collect_charset()
    CHARSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHARSET_FILE.write_text("".join(sorted(charset)), encoding="utf-8")

    codepoints = sorted({ord(char) for char in charset})
    print(f"字符集: {len(codepoints)} 个码位（含 GB2312 一级常用字）")

    cjk = download(*SOURCES["xiaolai"])
    mono = download(*SOURCES["wenkai-mono"])

    rules: list[str] = [EXCALIFONT_RULE]
    rules += build_cjk(cjk, codepoints)
    rules.append(build_mono(mono))

    header = (
        "/* 由 tools/build_fonts.py 生成，请勿手改。\n"
        " * Xiaolai (OFL-1.1) —— 中文手写体\n"
        " * LXGW WenKai Mono (OFL-1.1) —— 代码\n"
        " * Excalifont (OFL-1.1) —— 拉丁字母与数字\n"
        " */\n\n"
    )
    CSS_FILE.write_text(header + "\n\n".join(rules) + "\n", encoding="utf-8")
    print(f"  ✓ 写入 {CSS_FILE.relative_to(ROOT)}")

    print(f"  ✓ 写入 {CHARSET_FILE.relative_to(ROOT)}")

    license_file = FONT_DIR / "OFL-Xiaolai.txt"
    if not license_file.exists():
        urllib.request.urlretrieve(OFL_URL, license_file)
        print(f"  ✓ 写入 {license_file.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
