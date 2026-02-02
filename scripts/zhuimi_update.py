#!/usr/bin/env python3
"""
追觅 - 文献追踪与AI评分主脚本
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml
from openai import OpenAI
from tqdm import tqdm

# =============================================================================
# 配置
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = SCRIPT_DIR / "config" / "zhuimi_config.yaml"
FEEDS_FILE = SCRIPT_DIR / "pubmed_feeds.json"
ANALYZED_DB = SCRIPT_DIR / ".zhuimi_analyzed.json"
CONTENT_DIR = PROJECT_ROOT / "content" / "ZhuiMi"


def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f)
    # 默认配置
    return {
        "rss": {"days_window": 1, "max_feeds": 50},
        "ai": {"model": "gpt-4o-mini", "max_tokens": 150, "temperature": 0.3},
        "report": {"sort_by": "recommendation", "max_articles": 50},
    }


def normalize_api_url(base_url):
    """
    规范化API URL，确保有正确的后缀
    """
    url = base_url.rstrip("/")

    # 如果已经包含完整路径，直接返回
    if "chat/completions" in url:
        return url

    # 如果没有/v1，添加它
    if not url.endswith("/v1"):
        url = url + "/v1"

    return url


def get_openai_client():
    """创建OpenAI客户端"""
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    normalized_url = normalize_api_url(base_url)

    return OpenAI(base_url=normalized_url, api_key=os.getenv("OPENAI_API_KEY", ""))


# =============================================================================
# RSS 抓取
# =============================================================================


def load_pubmed_feeds():
    """加载预处理好的PubMed源列表"""
    with open(FEEDS_FILE, encoding="utf-8") as f:
        return json.load(f)


def parse_rss_date(date_str):
    """解析RSS日期字符串"""
    try:
        from email.utils import parsedate_to_datetime

        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now(timezone.utc)


def extract_doi(entry):
    """从文章条目中提取DOI"""
    # 尝试从link中提取DOI
    link = entry.get("link", "")
    doi_match = re.search(r"10\.\d{4,9}/[^\s]+", link)
    if doi_match:
        return doi_match.group(0)

    # 尝试从其他字段提取
    for key in ["dc_identifier", "prism_doi"]:
        if key in entry:
            doi_match = re.search(r"10\.\d{4,9}/[^\s]+", entry[key])
            if doi_match:
                return doi_match.group(0)

    return None


def fetch_articles(feed_urls, days=1, max_articles=50):
    """
    从RSS源抓取最近N天的文章

    Args:
        feed_urls: RSS源URL列表
        days: 抓取最近几天的文章
        max_articles: 最多抓取文章数量

    Returns:
        list: 文章列表
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    articles = []
    seen = set()  # 去重

    for url in feed_urls:
        if len(articles) >= max_articles:
            break

        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if len(articles) >= max_articles:
                    break

                try:
                    pub_date = parse_rss_date(entry.get("published", ""))
                    if pub_date >= cutoff:
                        title = entry.get("title", "")
                        link = entry.get("link", "")
                        abstract = entry.get("summary", entry.get("description", ""))

                        # 过滤掉摘要为空的文章
                        if not abstract or abstract.strip() == "":
                            continue

                        # 使用link去重
                        if link in seen:
                            continue
                        seen.add(link)

                        articles.append(
                            {
                                "title": title,
                                "abstract": abstract,
                                "link": link,
                                "doi": extract_doi(entry),
                                "pub_date": pub_date,
                            }
                        )
                except Exception as e:
                    # 跳过解析失败的文章
                    continue
        except Exception as e:
            print(f"  [WARNING] 抓取RSS失败 {url}: {e}")
            continue

    print(f"  [INFO] 从 {len(feed_urls)} 个源抓取到 {len(articles)} 篇文章")
    return articles


# =============================================================================
# 去重逻辑
# =============================================================================


def get_article_id(article):
    """
    生成文章唯一ID，优先使用 DOI

    Args:
        article: 文章字典，包含 title, link, doi 等字段

    Returns:
        str: 文章唯一ID
    """
    # 优先使用 DOI（最稳定的唯一标识）
    doi = article.get("doi")
    if doi:
        return f"doi:{doi}"

    # 其次使用链接（去除查询参数，避免 URL 参数变化）
    link = article.get("link", "")
    if link:
        # 去除 URL 中的查询参数和片段
        link = link.split("?")[0].split("#")[0]
        return f"link:{hashlib.md5(link.encode('utf-8')).hexdigest()}"

    # 最后才使用标题（最不稳定）
    title = article.get("title", "").strip()
    if title:
        # 标题规范化：转小写，去除特殊字符
        title_normalized = re.sub(r"[^\w\s]", "", title.lower().strip())
        return f"title:{hashlib.md5(title_normalized.encode('utf-8')).hexdigest()}"

    # 如果都没有，使用一个基于时间戳的 ID
    return f"unknown:{datetime.now(timezone.utc).isoformat()}"


def load_analyzed_articles():
    """加载已分析文章列表"""
    if ANALYZED_DB.exists():
        with open(ANALYZED_DB, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_analyzed_articles(article_ids):
    """保存已分析文章列表"""
    with open(ANALYZED_DB, "w", encoding="utf-8") as f:
        json.dump(list(article_ids), f, indent=2)


# =============================================================================
# AI 评分
# =============================================================================


def parse_scores(response_text):
    """
    解析AI返回的评分文本和推荐理由

    Args:
        response_text: AI返回的文本

    Returns:
        tuple: (评分字典, 推荐理由)
    """
    scores = {
        "research": 0,
        "social": 0,
        "blood": 0,
        "recommendation": 0,
    }

    # 解析各种可能的格式
    patterns = {
        "research": r"(?:Research|研究)[\s:：]+(\d+)",
        "social": r"(?:Social|社会)[\s:：]+(\d+)",
        "blood": r"(?:Blood|血液)[\s:：]+(\d+)",
        "recommendation": r"(?:Recommendation|推荐)[\s:：]+(\d+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            try:
                scores[key] = int(match.group(1))
            except (ValueError, IndexError):
                pass

    # 解析推荐理由（查找 Reason 或 理由 后面的内容）
    reason = ""
    reason_patterns = [
        r"(?:Reason|理由)[\s:：]+\n*(.+?)(?=\n\n|\n*$|$)",
        r"(?:Reason|理由)[\s:：]+(.+)",
    ]
    for pattern in reason_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
        if match:
            reason = match.group(1).strip()
            # 限制长度
            if len(reason) > 300:
                reason = reason[:300] + "..."
            break

    return scores, reason


def score_article(article, client, model):
    """
    使用AI对文章进行4维度评分并生成推荐理由

    Args:
        article: 文章字典
        client: OpenAI客户端
        model: 模型名称

    Returns:
        tuple: (评分字典, 推荐理由)
    """
    abstract = article.get("abstract", "")[:2000]  # 限制长度

    prompt = f"""Given the following article abstract, provide scores (0-100) for:

1. Research Score: Innovation, methodological rigor, data reliability
2. Social Impact Score: Public attention, policy relevance
3. Blood Disease Relevance: Relevance to hematological diseases, including applicability and reference value for hematology research (可借鉴性)
4. Recommendation Score: Overall recommendation for reading

Then provide a brief recommendation reason (1-2 sentences in Chinese, explain why this article is worth reading).

Abstract: {abstract}

Respond in this format:
Research: XX
Social: XX
Blood: XX
Recommendation: XX

Reason: [推荐理由，中文]
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical research expert specializing in hematology.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.3,
        )

        result_text = response.choices[0].message.content
        scores, reason = parse_scores(result_text)

        return scores, reason

    except Exception as e:
        print(f"  [ERROR] AI评分失败: {e}")
        # 返回默认分数和空理由
        return (
            {
                "research": 50,
                "social": 50,
                "blood": 50,
                "recommendation": 50,
            },
            "评分失败，请手动查看",
        )


def should_include_article(article):
    """
    判断文章是否应该包含在报告中

    Args:
        article: 文章字典（包含 scores）

    Returns:
        bool: True 表示应该包含，False 表示应该过滤
    """
    scores = article.get("scores", {})

    # 过滤：推荐度为0
    if scores.get("recommendation", 0) == 0:
        return False

    # 过滤：血液相关性为0
    if scores.get("blood", 0) == 0:
        return False

    return True


# =============================================================================
# Typst 文件生成
# =============================================================================


def save_daily_articles(date_str, articles):
    """
    保存当天所有文章到每日数据库

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        articles: 文章列表
    """
    daily_db_path = CONTENT_DIR / f".zhuimi_daily_{date_str}.json"
    # Remove pub_date field before saving to avoid datetime serialization error
    for article in articles:
        article.pop("pub_date", None)
    with open(daily_db_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def load_daily_articles(date_str):
    """
    加载当天所有文章

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)

    Returns:
        list: 当天的文章列表，如果数据库不存在返回空列表
    """
    daily_db_path = CONTENT_DIR / f".zhuimi_daily_{date_str}.json"
    if daily_db_path.exists():
        with open(daily_db_path, encoding="utf-8") as f:
            return json.load(f)
    return []


def rebuild_daily_db_from_report(date_str):
    """
    从Typst报告中重建每日数据库

    当存在报告但没有数据库时，尝试从报告解析文章数据

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)

    Returns:
        list: 解析出的文章列表，如果解析失败返回空列表
    """
    report_path = CONTENT_DIR / date_str / "index.typ"
    if not report_path.exists():
        return []

    try:
        with open(report_path, encoding="utf-8") as f:
            content = f.read()

        articles = []
        # 按文章分割 (以 == # 开头的标题)
        article_blocks = re.split(r"\n== #\d+\. ", content)[1:]  # 跳过第一个空块

        for block in article_blocks:
            article = {}

            # 提取标题 (第一行)
            lines = block.strip().split("\n")
            if lines:
                # 反转义所有Typst特殊字符
                title_text = lines[0].strip()
                article["title"] = (
                    title_text.replace("\\@", "@")
                    .replace("\\#", "#")
                    .replace("\\<", "<")
                    .replace("\\>", ">")
                    .replace("\\[", "[")
                    .replace("\\]", "]")
                    .replace("\\(", "(")
                    .replace("\\)", ")")
                    .replace("\\{", "{")
                    .replace("\\}", "}")
                    .replace("\\*", "*")
                )

            # 提取评分
            scores = {}
            research_match = re.search(r"\*\*研究分数\*\*: #(\d+)", block)
            if research_match:
                scores["research"] = int(research_match.group(1))
            social_match = re.search(r"\*\*社会影响\*\*: #(\d+)", block)
            if social_match:
                scores["social"] = int(social_match.group(1))
            blood_match = re.search(r"\*\*血液相关性\*\*: #(\d+)", block)
            if blood_match:
                scores["blood"] = int(blood_match.group(1))
            rec_match = re.search(r"\*\*推荐度\*\*: #(\d+)", block)
            if rec_match:
                scores["recommendation"] = int(rec_match.group(1))
            article["scores"] = scores

            # 提取DOI
            doi_match = re.search(r"\*\*DOI\*\*: #(.+?)$", block, re.MULTILINE)
            if doi_match:
                doi = doi_match.group(1).strip()
                article["doi"] = doi if doi != "N/A" else None

            # 提取链接
            link_match = re.search(r'#link\("([^"]+)"\)', block)
            if link_match:
                article["link"] = link_match.group(1)

            # 提取推荐理由
            reason_match = re.search(
                r"推荐理由: (.+?)(?:\n\n|\n摘要:)", block, re.DOTALL
            )
            if reason_match:
                # 反转义所有Typst特殊字符
                reason_text = reason_match.group(1).strip()
                article["reason"] = (
                    reason_text.replace("\\@", "@")
                    .replace("\\#", "#")
                    .replace("\\<", "<")
                    .replace("\\>", ">")
                    .replace("\\[", "[")
                    .replace("\\]", "]")
                    .replace("\\(", "(")
                    .replace("\\)", ")")
                    .replace("\\{", "{")
                    .replace("\\}", "}")
                    .replace("\\*", "*")
                )

            # 提取摘要
            abstract_match = re.search(
                r"摘要: (.+?)(?:\n\n---|\n---)", block, re.DOTALL
            )
            if abstract_match:
                # 反转义所有Typst特殊字符
                abstract_text = abstract_match.group(1).strip()
                article["abstract"] = (
                    abstract_text.replace("\\@", "@")
                    .replace("\\#", "#")
                    .replace("\\<", "<")
                    .replace("\\>", ">")
                    .replace("\\[", "[")
                    .replace("\\]", "]")
                    .replace("\\(", "(")
                    .replace("\\)", ")")
                    .replace("\\{", "{")
                    .replace("\\}", "}")
                    .replace("\\*", "*")
                )

            # pub_date 无法从报告中恢复，设为 None
            article["pub_date"] = None

            # 验证必要字段
            if article.get("title") and article.get("link") and article.get("scores"):
                articles.append(article)

        return articles

    except Exception as e:
        print(f"  [ERROR] 从报告重建数据库失败: {e}")
        return []


def load_existing_articles(date_str):
    """
    加载当天已存在的文章（已废弃，使用 load_daily_articles 代替）

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)

    Returns:
        list: 已存在的文章列表，如果文件不存在返回空列表
    """
    # 直接使用新的每日数据库函数
    return load_daily_articles(date_str)


def generate_daily_report(date_str, scored_articles, append_mode=False):
    """
    生成每日报告的Typst文件

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        scored_articles: 已评分的文章列表
        append_mode: 是否为追加模式
    """
    dir_path = CONTENT_DIR / date_str
    dir_path.mkdir(parents=True, exist_ok=True)

    # 追加模式：加载现有文章
    if append_mode:
        existing_articles = load_existing_articles(date_str)
        # 合并现有文章和新文章（通过链接去重）
        seen_links = {a["link"] for a in existing_articles}
        for article in scored_articles:
            if article["link"] not in seen_links:
                existing_articles.append(article)
                seen_links.add(article["link"])
        scored_articles = existing_articles

    # 按推荐度排序
    sort_key = scored_articles[0]["scores"].keys()
    config = load_config()
    sort_by = config.get("report", {}).get("sort_by", "recommendation")

    sorted_articles = sorted(
        scored_articles, key=lambda x: x["scores"].get(sort_by, 0), reverse=True
    )

    content = f"""#import "../../../config.typ": template, tufted
#show: template.with(title: "追觅 - {date_str}")

= 追觅 - {date_str}

生成时间: #{datetime.now().strftime("%Y-%m-%d %H:%M")}

分析文章数量: #{len(sorted_articles)}

"""

    for i, article in enumerate(sorted_articles, 1):
        title = article["title"]
        scores = article["scores"]
        doi = article.get("doi", "N/A")
        link = article["link"]
        abstract = article.get("abstract", "")[:1000]  # 限制摘要长度

        # 转义内容，处理Typst特殊字符和HTML标签
        # 需要转义的字符：# $ < > [ ] ( ) @ 等

        # 辅助函数：处理LaTeX数学符号，转换为纯文本
        def clean_math_symbols(text):
            """将LaTeX数学符号转换为纯文本"""
            if not text:
                return text
            # 处理常见的数学符号模式
            text = text.replace(r"$3^{\prime}$", "3'")
            text = text.replace(r"$5^{\prime}$", "5'")
            text = text.replace(r"$3'$", "3'")
            text = text.replace(r"$5'$", "5'")
            text = text.replace(r"$\alpha$", "alpha")
            text = text.replace(r"$\beta$", "beta")
            text = text.replace(r"$\gamma$", "gamma")
            # 处理其他可能的$符号（转义剩余的）
            text = text.replace("$", "\\$")
            
            # 处理 LaTeX 下标和上标标记（如 B_{c}^{+}）
            # 先处理上标：^{...}
            import re
            # 处理上标 ^{xxx}  为 ^xxx
            text = re.sub(r'\^\{([^}]*)\}', r'^\1', text)
            # 处理下标 _{xxx} 为 _xxx  
            text = re.sub(r'_\{([^}]*)\}', r'_\1', text)
            
            # 处理Unicode上标和下标字符（常见于科学文献）
            # 上标：⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻ ⁼ ⁽ ⁾
            text = text.replace("⁰", "^0")
            text = text.replace("¹", "^1")
            text = text.replace("²", "^2")
            text = text.replace("³", "^3")
            text = text.replace("⁴", "^4")
            text = text.replace("⁵", "^5")
            text = text.replace("⁶", "^6")
            text = text.replace("⁷", "^7")
            text = text.replace("⁸", "^8")
            text = text.replace("⁹", "^9")
            text = text.replace("⁺", "^+")
            text = text.replace("⁻", "^-")
            text = text.replace("⁼", "^=")
            text = text.replace("⁽", "^(")
            text = text.replace("⁾", "^)")
            # 下标：₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉ ₊ ₋ ₌ ₍ ₎
            text = text.replace("₀", "_0")
            text = text.replace("₁", "_1")
            text = text.replace("₂", "_2")
            text = text.replace("₃", "_3")
            text = text.replace("₄", "_4")
            text = text.replace("₅", "_5")
            text = text.replace("₆", "_6")
            text = text.replace("₇", "_7")
            text = text.replace("₈", "_8")
            text = text.replace("₉", "_9")
            text = text.replace("₊", "_+")
            text = text.replace("₋", "_-")
            text = text.replace("₌", "_=")
            text = text.replace("₍", "_(")
            text = text.replace("₎", "_)")
            
            return text

        # 标题转义
        title_escaped = (
            clean_math_symbols(title)
            .replace("*", "\\*")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace("@", "\\@")
            .replace("#", "\\#")
            .replace("<", "\\<")
            .replace(">", "\\>")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )
        # 摘要转义
        abstract_text = (
            clean_math_symbols(abstract)
            .replace("*", "\\*")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace("@", "\\@")
            .replace("#", "\\#")
            .replace("<", "\\<")
            .replace(">", "\\>")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )
        # 推荐理由转义
        reason = article.get("reason", "")
        reason_text = (
            clean_math_symbols(reason)
            .replace("*", "\\*")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace("@", "\\@")
            .replace("#", "\\#")
            .replace("<", "\\<")
            .replace(">", "\\>")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("(", "\\(")
            .replace(")", "\\)")
            if reason
            else ""
        )

        content += f'''
== #{i}. {title_escaped}

- **研究分数**: #{scores.get("research", "N/A")}
- **社会影响**: #{scores.get("social", "N/A")}
- **血液相关性**: #{scores.get("blood", "N/A")}
- **推荐度**: #{scores.get("recommendation", "N/A")}
- **DOI**: #{doi}
- **链接**: #link("{link}")[查看原文]

推荐理由: {reason_text}

摘要: {abstract_text}

---

'''

    with open(dir_path / "index.typ", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [INFO] 生成报告: {dir_path / 'index.typ'}")


def update_index_page():
    """更新主页索引"""
    reports = sorted(CONTENT_DIR.glob("*/index.typ"), reverse=True)

    content = """#import "../../config.typ": template, tufted
#show: template.with(title: "追觅")

= 追觅

每日文献追踪与AI评分报告。

== 历史报告

"""

    for report_path in reports:
        date_str = report_path.parent.name
        content += f'- #link("/ZhuiMi/{date_str}/")[{date_str}]\n'

    with open(CONTENT_DIR / "index.typ", "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [INFO] 更新索引: {CONTENT_DIR / 'index.typ'}")


# =============================================================================
# 主流程
# =============================================================================


def main():
    """主函数"""
    print("=" * 60)
    print("追觅 - 文献追踪与AI评分")
    print("=" * 60)

    # 加载配置
    config = load_config()

    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] 未设置 OPENAI_API_KEY 环境变量")
        return 1

    # 加载PubMed源
    print("\n[STEP 1] 加载RSS源...")
    feeds = load_pubmed_feeds()
    feed_urls = [f["url"] for f in feeds]
    print(f"  [INFO] 加载 {len(feed_urls)} 个PubMed RSS源")

    # 加载已分析文章
    print("\n[STEP 2] 加载去重数据库...")
    analyzed_ids = load_analyzed_articles()
    print(f"  [INFO] 已分析文章数: {len(analyzed_ids)}")

    # 抓取新文章
    print("\n[STEP 3] 抓取最新文章...")
    days_window = config.get("rss", {}).get("days_window", 1)
    max_articles = config.get("report", {}).get("max_articles", 50)
    articles = fetch_articles(feed_urls, days=days_window, max_articles=max_articles)

    # 过滤已分析文章
    print("\n[STEP 4] 过滤已分析文章...")
    new_articles = [a for a in articles if get_article_id(a) not in analyzed_ids]
    print(f"  [INFO] 新文章数: {len(new_articles)}")

    if not new_articles:
        # 检查当天是否已有报告
        today = datetime.now().strftime("%Y-%m-%d")
        today_report_path = CONTENT_DIR / today / "index.typ"
        if today_report_path.exists():
            print("\n[INFO] 没有新文章，当天报告已存在")
            return 0
        else:
            print("\n[INFO] 没有新文章，且当天报告不存在")
            return 0

    # AI评分
    print("\n[STEP 5] AI评分中...")
    client = get_openai_client()
    model = os.getenv("OPENAI_MODEL", config.get("ai", {}).get("model", "gpt-4o-mini"))

    scored_articles = []
    for article in tqdm(new_articles, desc="  AI评分进度"):
        scores, reason = score_article(article, client, model)
        scored_articles.append({**article, "scores": scores, "reason": reason})
        analyzed_ids.add(get_article_id(article))

    # 立即保存去重数据库（避免中途退出导致丢失）
    print(f"  [INFO] 保存去重数据库...")
    save_analyzed_articles(analyzed_ids)

    # 过滤不符合条件的文章
    print("\n[STEP 6] 过滤不符合条件的文章...")
    filtered_articles = [a for a in scored_articles if should_include_article(a)]
    filtered_count = len(scored_articles) - len(filtered_articles)
    if filtered_count > 0:
        print(f"  [INFO] 过滤了 {filtered_count} 篇不符合条件的文章")

    if not filtered_articles:
        # 检查当天是否已有报告（可能有之前符合条件的文章）
        today = datetime.now().strftime("%Y-%m-%d")
        today_report_path = CONTENT_DIR / today / "index.typ"
        if today_report_path.exists():
            print("\n[INFO] 本次新增文章均不符合条件，当天报告保持不变")
            return 0
        else:
            print("\n[INFO] 没有符合条件的文章，且当天报告不存在")
            return 0

    # 生成报告
    print("\n[STEP 7] 生成Typst报告...")
    today = datetime.now().strftime("%Y-%m-%d")
    today_report_path = CONTENT_DIR / today / "index.typ"

    # 检查当天报告是否已存在，加载已有文章
    append_mode = today_report_path.exists()
    if append_mode:
        print(f"  [INFO] 检测到当天报告已存在，启用追加模式")
        # 加载当天已有文章
        existing_articles = load_daily_articles(today)

        # 降级处理：如果有报告但没有数据库，尝试从报告重建
        if not existing_articles:
            print(f"  [INFO] 未找到每日数据库文件，尝试从报告重建...")
            existing_articles = rebuild_daily_db_from_report(today)
            if existing_articles:
                print(f"  [INFO] 成功从报告重建 {len(existing_articles)} 篇文章")
                # 保存重建的数据库
                save_daily_articles(today, existing_articles)
            else:
                print(f"  [WARNING] 从报告重建失败，将覆盖旧报告")
                print(f"  [INFO] 如需保留旧文章，请手动备份或删除旧报告后重新运行")
                # 跳过追加，只保留新文章
                all_articles = filtered_articles
                # 保存数据库并生成报告
                save_daily_articles(today, all_articles)
                generate_daily_report(today, all_articles, append_mode=False)

                # 更新索引
                print("\n[STEP 8] 更新索引页面...")
                update_index_page()

                print("\n" + "=" * 60)
                print(
                    f"[OK] 完成！分析了 {len(scored_articles)} 篇文章，筛选后 {len(filtered_articles)} 篇"
                )
                print("=" * 60)
                return 0

        # 合并文章（通过链接去重，新文章覆盖旧文章）
        seen = {a["link"]: a for a in existing_articles}
        for article in filtered_articles:
            seen[article["link"]] = article
        all_articles = list(seen.values())
        print(f"  [INFO] 合并后共 {len(all_articles)} 篇文章")
    else:
        all_articles = filtered_articles

    # 保存每日数据库
    save_daily_articles(today, all_articles)

    # 生成报告
    generate_daily_report(today, all_articles, append_mode=False)

    # 更新索引
    print("\n[STEP 8] 更新索引页面...")
    update_index_page()

    print("\n" + "=" * 60)
    print(
        f"[OK] 完成！分析了 {len(scored_articles)} 篇文章，筛选后 {len(filtered_articles)} 篇"
    )
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
