# /// script
# requires-python = ">=3.6"
# dependencies = []
# ///

"""
Tufted Blog Template 构建脚本

这是一个跨平台的构建脚本，用于将 Typst (.typ) 文件编译为 HTML 和 PDF，
并复制静态资源到输出目录。

支持增量编译：只重新编译修改后的文件，加快构建速度。

用法:
    uv run build.py build       # 完整构建 (HTML + PDF + 资源)
    uv run build.py html        # 仅构建 HTML 文件
    uv run build.py pdf         # 仅构建 PDF 文件
    uv run build.py assets      # 仅复制静态资源
    uv run build.py clean       # 清理生成的文件
    uv run build.py preview     # 启动本地预览服务器（默认端口 8000）
    uv run build.py preview -p 3000  # 使用自定义端口
    uv run build.py --help      # 显示帮助信息

增量编译选项:
    --force, -f                 # 强制完整重建，忽略增量检查

预览服务器选项:
    --port, -p PORT             # 指定服务器端口号（默认: 8000）

也可以直接使用 Python 运行:
    python build.py build
    python build.py build --force
    python build.py preview -p 3000
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import List, Optional, Set

# ============================================================================
# 配置
# ============================================================================

CONTENT_DIR = Path("content")  # 源文件目录
SITE_DIR = Path("_site")  # 输出目录
ASSETS_DIR = Path("assets")  # 静态资源目录
CONFIG_FILE = Path("config.typ")  # 全局配置文件

# 需要注入到 HTML <head> 中的标签
HEAD_INJECTION = (
    '<link rel="icon" href="/assets/favicon.ico">'
    '<script src="/assets/copy-code.js"></script>'
    '<script src="/assets/line-numbers.js"></script>'
    '<script src="/assets/format-headings.js"></script>'
)


# ============================================================================
# 增量编译辅助函数
# ============================================================================


def get_file_mtime(path: Path) -> float:
    """
    获取文件的修改时间戳。

    参数:
        path: 文件路径

    返回:
        float: 修改时间戳，文件不存在返回 0
    """
    try:
        return path.stat().st_mtime
    except (OSError, FileNotFoundError):
        return 0.0


def is_dep_file(path: Path) -> bool:
    """
    判断一个文件是否被追踪为依赖）。

    content/ 下的普通页面文件不被视为模板文件，因为它们是独立的页面，
    不应该相互依赖。

    参数:
        path: 文件路径

    返回:
        bool: 是否是依赖文件
    """
    try:
        resolved_path = path.resolve()
        project_root = Path(__file__).parent.resolve()
        content_dir = (project_root / CONTENT_DIR).resolve()

        # config.typ 是依赖文件
        if resolved_path == (project_root / CONFIG_FILE).resolve():
            return True

        # 检查是否在 content/ 目录下
        try:
            relative_to_content = resolved_path.relative_to(content_dir)
            # content/_* 目录下的文件视为依赖文件
            parts = relative_to_content.parts
            if len(parts) > 0 and parts[0].startswith("_"):
                return True
            # content/ 下的其他文件不是依赖文件
            return False
        except ValueError:
            # 不在 content/ 目录下，视为依赖文件（如 config.typ）
            return True

    except Exception:
        return True


def find_typ_dependencies(typ_file: Path) -> Set[Path]:
    """
    解析 .typ 文件中的依赖（通过 #import 和 #include 导入的文件）。

    只追踪 .typ 文件的依赖，忽略 content/ 下的普通页面文件。
    其他资源文件（如 .md, .bib, 图片等）通过 copy_content_assets 处理。

    参数:
        typ_file: .typ 文件路径

    返回:
        Set[Path]: 依赖的 .typ 文件路径集合
    """
    dependencies: Set[Path] = set()

    try:
        content = typ_file.read_text(encoding="utf-8")
    except Exception:
        return dependencies

    # 获取文件所在目录，用于解析相对路径
    base_dir = typ_file.parent

    patterns = [
        r'#import\s+"([^"]+)"',
        r"#import\s+'([^']+)'",
        r'#include\s+"([^"]+)"',
        r"#include\s+'([^']+)'",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            dep_path_str = match.group(1)

            # 跳过包导入（如 @preview/xxx）
            if dep_path_str.startswith("@"):
                continue

            # 解析相对路径
            if dep_path_str.startswith("/"):
                # 相对于项目根目录的路径
                dep_path = Path(dep_path_str.lstrip("/"))
            else:
                # 相对于当前文件的路径
                dep_path = base_dir / dep_path_str

            # 规范化路径，只追踪 .typ 文件
            try:
                dep_path = dep_path.resolve()
                if dep_path.exists() and dep_path.suffix == ".typ" and is_dep_file(dep_path):
                    dependencies.add(dep_path)
            except Exception:
                pass

    return dependencies


def get_all_dependencies(typ_file: Path, visited: Optional[Set[Path]] = None) -> Set[Path]:
    """
    递归获取 .typ 文件的所有依赖（包括传递依赖）。

    参数:
        typ_file: .typ 文件路径
        visited: 已访问的文件集合（用于避免循环依赖）

    返回:
        Set[Path]: 所有依赖文件路径集合
    """
    if visited is None:
        visited = set()

    # 避免循环依赖
    abs_path = typ_file.resolve()
    if abs_path in visited:
        return set()
    visited.add(abs_path)

    all_deps: Set[Path] = set()
    direct_deps = find_typ_dependencies(typ_file)

    for dep in direct_deps:
        all_deps.add(dep)
        # 只对 .typ 文件递归查找依赖
        if dep.suffix == ".typ":
            all_deps.update(get_all_dependencies(dep, visited))

    return all_deps


def needs_rebuild(source: Path, target: Path, extra_deps: Optional[List[Path]] = None) -> bool:
    """
    判断是否需要重新构建。

    当以下任一条件满足时需要重建：
    1. 目标文件不存在
    2. 源文件比目标文件新
    3. 任何额外依赖文件比目标文件新
    4. 源文件的任何导入依赖比目标文件新
    5. 源文件同目录下的任何非 .typ 文件比目标文件新（如 .md, .bib, 图片等）

    参数:
        source: 源文件路径
        target: 目标文件路径
        extra_deps: 额外的依赖文件列表（如 config.typ）

    返回:
        bool: 是否需要重新构建
    """
    # 目标不存在，需要构建
    if not target.exists():
        return True

    target_mtime = get_file_mtime(target)

    # 源文件更新了
    if get_file_mtime(source) > target_mtime:
        return True

    # 检查额外依赖
    if extra_deps:
        for dep in extra_deps:
            if dep.exists() and get_file_mtime(dep) > target_mtime:
                return True

    # 检查源文件的导入依赖
    for dep in get_all_dependencies(source):
        if get_file_mtime(dep) > target_mtime:
            return True

    # 检查源文件同目录下的非 .typ 资源文件（如 .md, .bib, 图片等）
    # 只检查同一目录，不递归子目录，避免过度重编译
    source_dir = source.parent
    for item in source_dir.iterdir():
        if item.is_file() and item.suffix != ".typ":
            if get_file_mtime(item) > target_mtime:
                return True

    return False


def find_common_dependencies() -> List[Path]:
    """
    查找所有文件的公共依赖（如 config.typ）。

    返回:
        List[Path]: 公共依赖文件路径列表
    """
    common_deps = []

    # config.typ 是全局配置，修改后所有页面都需要重建
    if CONFIG_FILE.exists():
        common_deps.append(CONFIG_FILE)

    # 可以在这里添加其他公共依赖
    # 例如：查找 content/_* 目录下的模板文件
    if CONTENT_DIR.exists():
        for item in CONTENT_DIR.iterdir():
            if item.is_dir() and item.name.startswith("_"):
                for typ_file in item.rglob("*.typ"):
                    common_deps.append(typ_file)

    return common_deps


# ============================================================================
# 辅助函数
# ============================================================================


def find_typ_files() -> List[Path]:
    """
    查找 content/ 目录下所有 .typ 文件，排除路径中包含以下划线开头的目录的文件。

    返回:
        List[Path]: .typ 文件路径列表
    """
    typ_files = []
    for typ_file in CONTENT_DIR.rglob("*.typ"):
        # 检查路径中是否有以下划线开头的目录
        parts = typ_file.relative_to(CONTENT_DIR).parts
        if not any(part.startswith("_") for part in parts):
            typ_files.append(typ_file)
    return typ_files


def get_html_output_path(typ_file: Path) -> Path:
    """
    获取 .typ 文件对应的 HTML 输出路径。

    参数:
        typ_file: .typ 文件路径 (相对于 content/)

    返回:
        Path: HTML 文件输出路径 (在 _site/ 目录下)
    """
    relative_path = typ_file.relative_to(CONTENT_DIR)
    return SITE_DIR / relative_path.with_suffix(".html")


def get_pdf_output_path(typ_file: Path) -> Path:
    """
    获取 .typ 文件对应的 PDF 输出路径。

    参数:
        typ_file: .typ 文件路径 (相对于 content/)

    返回:
        Path: PDF 文件输出路径 (在 _site/ 目录下)
    """
    relative_path = typ_file.relative_to(CONTENT_DIR)
    return SITE_DIR / relative_path.with_suffix(".pdf")


def inject_head_tags(html_path: Path):
    """
    向 HTML 文件的 </head> 标签前注入 favicon 和脚本标签。

    参数:
        html_path: HTML 文件路径
    """
    try:
        content = html_path.read_text(encoding="utf-8")
        modified_content = content.replace("</head>", HEAD_INJECTION + "</head>")
        html_path.write_text(modified_content, encoding="utf-8")
    except Exception as e:
        print(f"  [WARNING] 注入 HTML 标签失败: {html_path} - {e}")


def run_typst_command(args: List[str]) -> bool:
    """
    运行 typst 命令。

    参数:
        args: typst 命令参数列表

    返回:
        bool: 命令是否成功执行
    """
    try:
        result = subprocess.run(["typst"] + args, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            print(f"  [ERROR] Typst error: {result.stderr.strip()}")
            return False
        return True
    except FileNotFoundError:
        print("  [ERROR] 错误: 未找到 typst 命令。请确保已安装 Typst 并添加到 PATH 环境变量中。")
        print("  [INFO] 安装说明: https://typst.app/open-source/#download")
        return False
    except Exception as e:
        print(f"  [ERROR] 执行 typst 命令时出错: {e}")
        return False


# ============================================================================
# 构建命令
# ============================================================================


def build_html(force: bool = False):
    """
    编译所有 .typ 文件为 HTML（文件名中包含 PDF 的除外）。

    参数:
        force: 是否强制重建所有文件
    """
    typ_files = find_typ_files()

    # 排除标记为 PDF 的文件
    html_files = [f for f in typ_files if "pdf" not in f.stem.lower()]

    if not html_files:
        print("  [WARNING] 未找到任何 HTML 文件。")
        return True

    print("正在构建 HTML 文件...")

    # 获取公共依赖
    common_deps = find_common_dependencies()

    success_count = 0
    skip_count = 0
    fail_count = 0

    for typ_file in html_files:
        html_output = get_html_output_path(typ_file)

        # 增量编译检查
        if not force and not needs_rebuild(typ_file, html_output, common_deps):
            skip_count += 1
            continue

        html_output.parent.mkdir(parents=True, exist_ok=True)

        # 编译 HTML
        args = [
            "compile",
            "--root",
            ".",
            "--font-path",
            str(ASSETS_DIR),
            "--features",
            "html",
            "--format",
            "html",
            str(typ_file),
            str(html_output),
        ]

        if run_typst_command(args):
            # 注入 head 标签
            inject_head_tags(html_output)
            success_count += 1
        else:
            print(f"  [ERROR] {typ_file} 编译失败")
            fail_count += 1

    status_parts = []
    if success_count > 0:
        status_parts.append(f"编译: {success_count}")
    if skip_count > 0:
        status_parts.append(f"跳过: {skip_count}")
    if fail_count > 0:
        status_parts.append(f"失败: {fail_count}")

    status_str = ", ".join(status_parts) if status_parts else "无文件需要处理"
    print(f"[OK] HTML 构建完成。{status_str}")
    return fail_count == 0


def build_pdf(force: bool = False):
    """
    编译文件名包含 "PDF" 的 .typ 文件为 PDF。

    参数:
        force: 是否强制重建所有文件
    """
    typ_files = find_typ_files()
    pdf_files = [f for f in typ_files if "pdf" in f.stem.lower()]

    if not pdf_files:
        return True

    print("正在构建 PDF 文件...")

    # 获取公共依赖
    common_deps = find_common_dependencies()

    success_count = 0
    skip_count = 0
    fail_count = 0

    for typ_file in pdf_files:
        pdf_output = get_pdf_output_path(typ_file)

        # 增量编译检查
        if not force and not needs_rebuild(typ_file, pdf_output, common_deps):
            skip_count += 1
            continue

        pdf_output.parent.mkdir(parents=True, exist_ok=True)

        # 编译 PDF
        args = ["compile", "--root", ".", "--font-path", str(ASSETS_DIR), str(typ_file), str(pdf_output)]

        if run_typst_command(args):
            success_count += 1
        else:
            print(f"  [ERROR] {typ_file} 编译失败")
            fail_count += 1

    status_parts = []
    if success_count > 0:
        status_parts.append(f"编译: {success_count}")
    if skip_count > 0:
        status_parts.append(f"跳过: {skip_count}")
    if fail_count > 0:
        status_parts.append(f"失败: {fail_count}")

    status_str = ", ".join(status_parts) if status_parts else "无文件需要处理"
    print(f"[OK] PDF 构建完成。{status_str}")
    return fail_count == 0


def copy_assets() -> bool:
    """
    复制静态资源到输出目录。
    """
    if not ASSETS_DIR.exists():
        print(f"  [WARNING] 静态资源目录 {ASSETS_DIR} 不存在。")
        return True

    target_dir = SITE_DIR / "assets"

    try:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(ASSETS_DIR, target_dir)
        return True
    except Exception as e:
        print(f"  [ERROR] 复制静态资源失败: {e}")
        return False


def copy_content_assets(force: bool = False) -> bool:
    """
    复制 content 目录下的非 .typ 文件（如图片）到输出目录。
    支持增量复制：只复制修改过的文件。

    参数:
        force: 是否强制复制所有文件
    """
    if not CONTENT_DIR.exists():
        print(f"  [WARNING] 内容目录 {CONTENT_DIR} 不存在，跳过。")
        return True

    try:
        copy_count = 0
        skip_count = 0

        for item in CONTENT_DIR.rglob("*"):
            # 跳过目录和 .typ 文件
            if item.is_dir() or item.suffix == ".typ":
                continue

            # 跳过以下划线开头的路径
            relative_path = item.relative_to(CONTENT_DIR)
            if any(part.startswith("_") for part in relative_path.parts):
                continue

            # 计算目标路径
            target_path = SITE_DIR / relative_path

            # 增量复制检查
            if not force and target_path.exists():
                if get_file_mtime(item) <= get_file_mtime(target_path):
                    skip_count += 1
                    continue

            # 创建目标目录
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件
            shutil.copy2(item, target_path)
            copy_count += 1

        return True
    except Exception as e:
        print(f"  [ERROR] 复制内容资源文件失败: {e}")
        return False


def clean() -> bool:
    """
    清理生成的文件。
    """
    print("正在清理生成的文件...")

    if not SITE_DIR.exists():
        print(f"  输出目录 {SITE_DIR} 不存在，无需清理。")
        return True

    try:
        # 删除 _site 目录下的所有内容
        for item in SITE_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        print(f"  [OK] 已清理 {SITE_DIR}/ 目录。")
        return True
    except Exception as e:
        print(f"  [ERROR] 清理失败: {e}")
        return False


def preview(port: int = 8000, open_browser_flag: bool = True) -> bool:
    """
    启动本地预览服务器。

    首先尝试使用 uvx livereload（支持实时刷新），
    如果失败则回退到 Python 内置的 http.server。

    参数:
        port: 服务器端口号，默认为 8000
        open_browser_flag: 是否自动打开浏览器，默认为 True
    """
    if not SITE_DIR.exists():
        print(f"  [WARNING] 输出目录 {SITE_DIR} 不存在，请先运行 build 命令。")
        return False

    print("正在启动本地预览服务器（按 Ctrl+C 停止）...")
    print()

    if open_browser_flag:

        def open_browser():
            time.sleep(1.5)  # 等待服务器启动
            url = f"http://localhost:{port}"
            print(f"  🚀 正在打开浏览器: {url}")
            webbrowser.open(url)

        # 在后台线程中打开浏览器
        threading.Thread(target=open_browser, daemon=True).start()

    # 首先尝试 uvx livereload
    try:
        result = subprocess.run(
            ["uvx", "livereload", str(SITE_DIR), "-p", str(port)],
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("  未找到 uv，尝试 Python http.server...")
    except KeyboardInterrupt:
        print("\n服务器已停止。")
        return True

    # 回退到 Python http.server
    try:
        print("使用 Python 内置 http.server...")
        result = subprocess.run(
            [sys.executable, "-m", "http.server", str(port), "--directory", str(SITE_DIR)],
            check=False,
        )
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n服务器已停止。")
        return True
    except Exception as e:
        print(f"  [ERROR] 启动服务器失败: {e}")
        return False


def build(force: bool = False):
    """
    完整构建：HTML + PDF + 资源。

    参数:
        force: 是否强制重建所有文件
    """
    print("-" * 60)
    if force:
        print("[INFO] Starting full build...")
    else:
        print("[INFO] Starting incremental build...")
    print("-" * 60)

    # 确保输出目录存在
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    print()
    results.append(build_html(force))
    results.append(build_pdf(force))
    print()

    results.append(copy_assets())
    results.append(copy_content_assets(force))

    print("-" * 60)
    if all(results):
        print("[OK] 所有构建任务完成！")
        print(f"  📂 输出目录: {SITE_DIR.absolute()}")
    else:
        print("[WARNING] 构建完成，但有部分任务失败。")
    print("-" * 60)

    return all(results)


# ============================================================================
# 命令行接口
# ============================================================================


def create_parser():
    """
    创建命令行参数解析器。
    """
    parser = argparse.ArgumentParser(
        prog="build.py",
        description="Tufted Blog Template 构建脚本 - 将 content 中的 Typst 文件编译为 HTML 和 PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
构建脚本默认只重新编译修改过的文件，可使用 -f/--force 选项强制完整重建：
    uv run build.py build --force
    或 python build.py build -f

使用 preview 命令启动本地预览服务器：
    uv run build.py preview
    或 python build.py preview -p 3000  # 使用自定义端口

更多信息请参阅 README.md
""",
    )

    subparsers = parser.add_subparsers(dest="command", title="可用命令", metavar="<command>")

    build_parser = subparsers.add_parser("build", help="完整构建 (HTML + PDF + 资源)")
    build_parser.add_argument("-f", "--force", action="store_true", help="强制完整重建")

    html_parser = subparsers.add_parser("html", help="仅构建 HTML 文件")
    html_parser.add_argument("-f", "--force", action="store_true", help="强制完整重建")

    pdf_parser = subparsers.add_parser("pdf", help="仅构建 PDF 文件")
    pdf_parser.add_argument("-f", "--force", action="store_true", help="强制完整重建")

    subparsers.add_parser("assets", help="仅复制静态资源")
    subparsers.add_parser("clean", help="清理生成的文件")

    preview_parser = subparsers.add_parser("preview", help="启动本地预览服务器")
    preview_parser.add_argument(
        "-p", "--port", type=int, default=8000, help="服务器端口号（默认: 8000）"
    )
    preview_parser.add_argument(
        "--no-open", action="store_false", dest="open_browser", help="不自动打开浏览器"
    )
    preview_parser.set_defaults(open_browser=True)

    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # 确保在项目根目录运行
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # 获取 force 参数
    force = getattr(args, "force", False)

    # 执行对应的命令
    commands = {
        "build": lambda: build(force),
        "html": lambda: (SITE_DIR.mkdir(parents=True, exist_ok=True), build_html(force))[1],
        "pdf": lambda: (SITE_DIR.mkdir(parents=True, exist_ok=True), build_pdf(force))[1],
        "assets": lambda: (SITE_DIR.mkdir(parents=True, exist_ok=True), copy_assets())[1],
        "clean": clean,
        "preview": lambda: preview(getattr(args, "port", 8000), getattr(args, "open_browser", True)),
    }

    success = commands[args.command]()
    sys.exit(0 if success else 1)
