# rainoffallingstar's Blog

基于 [Tufted-Blog-Template](https://github.com/Yousa-Mirage/Tufted-Blog-Template) 的个人博客，使用 Typst 编写内容，Python 自动构建并部署到 GitHub Pages。

站点地址：**https://blog.rainoffallingstar.com**

## 技术栈

- 内容编写: [Typst](https://typst.app/)
- 静态站点生成: Tufted（`tufted-lib/`，随上游同步）
- 构建工具: Python + Typst CLI
- 部署: GitHub Actions + GitHub Pages

## 本地运行

### 环境要求

```bash
typst --version
python --version
```

### 常用命令

```bash
# 完整构建（HTML + PDF + 资源）
python build.py build

# 强制重建
python build.py build --force

# 仅构建 HTML / PDF
python build.py html
python build.py pdf

# 本地预览（默认 8000 端口）
python build.py preview

# 清理构建产物
python build.py clean

# 重新生成手写字体子集（改字/加生僻字后执行）
uv run --with fonttools --with brotli python3 tools/build_fonts.py
```

### 字体

正文用 [霞鹜小赖](https://github.com/lxgw/kose-font)（毛笔手写风的
中文）、Excalifont（拉丁字母与数字）、霞鹜文楷 Mono（代码），三者均为
SIL OFL 1.1，随仓库自带、不依赖 CDN。

完整的中文字体有 20 多 MB，`tools/build_fonts.py` 会按 `content/` 的
实际用字加上 GB2312 一级常用字做子集（约 870 KB）。构建时若发现字体子集
里没有的字符，会打印提示 —— 把新字补进去并重跑脚本即可。

## 目录结构

```text
.
├── content/           # 网站内容（Typst）
│   ├── Blog/
│   ├── About/
│   ├── Links/
│   ├── Docs/
│   ├── Timeline/      # 完整时间线（按年份归档）
│   ├── _data/         # 文章索引 posts.typ（首页与时间线共用，不编译）
│   └── index.typ      # 首页：最近更新的若干篇
├── tufted-lib/        # 模板实现（随上游同步，勿手改）
├── assets/            # 样式与脚本
│   ├── tufted.css     # 上游功能层
│   ├── theme.css      # 上游主题变量
│   ├── fonts.css      # 自托管字体的 @font-face（脚本生成，勿手改）
│   ├── fonts/         # 手写字体子集（Xiaolai / Excalifont / WenKai Mono）
│   ├── custom.css     # 内容级补丁（提示块、脚注）
│   ├── site.css       # 本站视觉层（改样式在这里）
│   ├── site.js        # 本站脚本（页头状态、主题切换动画）
│   ├── icons/         # RSS / 明暗图标
│   └── scripts/       # 上游脚本（目录、返回顶部、复制等）
├── tools/
│   ├── build_fonts.py     # 生成字体子集与 assets/fonts.css
│   └── font-charset.txt   # 字符集（脚本生成）
├── build.py           # 构建脚本（HTML / PDF / RSS / sitemap）
├── config.typ         # 站点配置
├── CNAME              # 自定义域名（部署真源）
└── .github/
    ├── workflows/
    │   ├── deploy.yml # 自动构建与部署
    │   └── update.yml # 每两周从上游同步模板
    └── .templatesyncignore  # 同步时排除的本站文件
```

## 写文章

1. 在 `content/Blog/` 下创建目录：`YYYY-MM-DD-title/`
2. 在目录中创建 `index.typ`
3. 在 `content/_data/posts.typ` 的 `posts` 数组里加一行
   （首页「最近更新」与 `/Timeline/` 都从这里取数据）
4. 提交到 `githubversion` 分支，触发自动部署

示例：

```typst
#import "../../config.typ": template, tufted
#show: template.with(title: "文章标题")

= 文章标题
正文内容...
```

## 部署

仓库在 `githubversion` 分支有变更时，会由 `.github/workflows/deploy.yml` 自动构建并发布到 GitHub Pages（`gh-pages` 分支）。

构建会产出的文件：

```text
_site/
├── index.html
├── Blog/ About/ Links/ Docs/ CV/   # 各页面
├── feed.xml        # RSS（全文输出）
├── sitemap.xml     # 站点地图
├── robots.txt      # 指向 sitemap
├── assets/
└── CNAME
```

## 自定义域名

站点通过自定义域名 `blog.rainoffallingstar.com` 访问。

**域名在三处定义，改域名必须三处同时改：**

| 位置 | 作用 |
| --- | --- |
| `CNAME`（仓库根目录） | GitHub Pages 读取的域名文件，只写裸域名，不带协议和斜杠 |
| `config.typ` 的 `site-url` | 生成 `canonical`、`sitemap.xml`、`feed.xml`、Open Graph 的绝对 URL |
| `.github/workflows/deploy.yml` 的 `cname:` | 部署 action 写入 `gh-pages` 的域名，必须与 `CNAME` 一致 |

### 注意事项

- **不要手改 `gh-pages` 分支上的 `CNAME`**。该分支是构建产物，下次部署会从主分支的 `CNAME` 覆盖回去。
- 部署工作流在发布前会校验 `CNAME` 存在且非空，写错会让 CI 直接失败，而不是静默丢掉域名。
- 更换域名后，还要到域名服务商（Cloudflare）把记录改为指向 `rainoffallingstar.github.io` 的 CNAME，并**先关闭代理（灰云 / DNS only）**，等 GitHub 签发完 TLS 证书后再按需开启。
- 确认部署状态：

```bash
gh api repos/rainoffallingstar/rainoffallingstar.github.io/pages \
  --jq '{cname, https_enforced, status}'
curl -sSI https://blog.rainoffallingstar.com/ | head -1
```

`https_enforced` 应为 `true`，且 HTTP 会 301 跳转到 HTTPS。

### Cloudflare 代理（橙云）

当前 DNS 记录为**橙云（Proxied）**：TLS 在 Cloudflare 边缘终结，回源走 HTTPS。

**SSL/TLS 模式必须保持 Full (strict)**。若设成 `Flexible`，Cloudflare 会用
HTTP 回源，GitHub Pages 会 301 跳回 HTTPS，形成无限重定向循环。

验证链路：

```bash
# 边缘证书：应为 CN=rainoffallingstar.com（Cloudflare 通用证书）
echo | openssl s_client -servername blog.rainoffallingstar.com \
  -connect blog.rainoffallingstar.com:443 2>/dev/null \
  | openssl x509 -noout -subject -dates

# 回源：绕过代理直连 GitHub Pages
curl -sS -o /dev/null -w 'origin=%{http_code}\n' \
  --resolve blog.rainoffallingstar.com:443:185.199.108.153 \
  https://blog.rainoffallingstar.com/

# 只跳一次，然后 200
curl -sSL -o /dev/null -w 'final=%{url_effective} code=%{http_code} redirects=%{num_redirects}\n' \
  http://blog.rainoffallingstar.com/
```

### ⚠️ 证书续期（需要定期手动处理）

涉及两个证书，**只有一个是自动续期的**：

| 证书 | 续期 |
| --- | --- |
| Cloudflare 边缘证书 | 自动，无需操作 |
| GitHub Pages 源站证书 | **橙云下无法自动续期** |

源站是 Let's Encrypt 证书，验证方式为 HTTP-01，但该请求会被橙云拦截。
源站证书一旦过期，GitHub Pages 会返回过期证书，Cloudflare 在 Full (strict)
模式下报 **526 Invalid SSL certificate**，站点直接不可访问。

**当前源站证书到期：2027-02-13**。请在 **2027-01-15 前后**（提前约一个月）
执行以下步骤，此后每约 90 天重复一次：

1. Cloudflare DNS 把 `blog` 记录切成 **DNS only（灰云）**
2. 等待生效，然后到 GitHub 仓库 Settings → Pages 让它重新签发证书
   （界面里如有 “Check again” 就点一下）；可能需要几分钟到几小时
3. 确认新的到期时间：

   ```bash
   echo | openssl s_client -servername blog.rainoffallingstar.com \
     -connect 185.199.108.153:443 2>/dev/null \
     | openssl x509 -noout -enddate
   ```

4. 切回 **Proxied（橙云）**，确认首页返回 200

日常健康检查（能在访客发现之前捕捉到问题）：

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  --resolve blog.rainoffallingstar.com:443:185.199.108.153 \
  https://blog.rainoffallingstar.com/
```

返回非 `200` 就说明源站证书需要处理。

### 未启用的自动化方案

`docs/pages-certificate-proxy.yml.disabled` 里放着一份完整的 GitHub Actions
工作流，能把上面的灰云 / 橙云切换做成全自动：

- 读 Pages API 的 `https_certificate.expires_at`
- 剩余 ≤ 30 天 → 自动切灰云
- GitHub 确认已签发新证书且剩余 ≥ 45 天 → 自动切回橙云
- 中间状态不动 DNS，避免反复横跳
- 灰云超过 24 小时仍没续上 → 报错提醒，不会贸然恢复橙云

**但它没有启用。** 文件放在 `.github/workflows/` 之外，还带 `.disabled`
后缀，GitHub 不会执行它。上面那套手动流程才是当前采用的方式。

留档而不启用的原因：

| 原因 | 说明 |
| --- | --- |
| 凭据风险 | 需要一个带 `DNS:Edit` 权限的 Cloudflare API Token，能改写整个域名的解析，影响面比仓库里其他任何东西都大 |
| 灰云期间无防护 | 切换期间站点失去 Cloudflare 的缓存、WAF 和代理保护，而 GitHub 重新签发可能耗时数小时 |
| 频率不高 | 约 90 天一次，手动操作比维护一套能悄悄改坏 DNS 的自动化更划算 |

文件头部写了完整的启用步骤（移动位置、创建 Token、配置 Secret/Variable、
先手动跑一次看日志）。如果哪天想改用自动化，照着做即可。

## 与上游模板同步

`tufted-lib/`、`assets/tufted.css`、`assets/theme.css`、`assets/scripts/` 等来自上游模板。

- **不要直接修改这些文件**，否则下次同步会被覆盖。
- 本站定制的样式写在 `assets/site.css`，配置写在 `config.typ`。
- `.github/workflows/update.yml` 每两周向上游拉取一次改动并开 PR。
- 本站自有文件已列入 `.github/.templatesyncignore`，同步时会被跳过。新增需要保留的文件时，记得也加进去。

## 许可证

[MIT License](./LICENSE)
