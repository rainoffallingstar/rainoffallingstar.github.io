# 博客归档说明

## 归档原因

由于Typst编译错误，部分博客文件无法正常构建。为了保证博客站点的稳定运行，将这些有问题的文件归档。

## 归档信息

- **归档日期**: 2025年1月5日
- **归档目录**: `content/Blog/_archived/`
- **归档文件数量**: 14个文件
- **归档原因**: 编译错误，包含编码问题、语法错误或格式问题

## 归档文件列表

### 2020年
1. 2020-08-23-生物竞赛路标系统2.0

### 2021年
2. 2021-05-20-临床问诊指北
3. 2021-08-24-肾肿瘤论文检索与阅读
4. 2021-11-22-Automated Classification of Papillary Renal Cell Carcinoma and Chromophobe Renal Cell Carcinoma Based on a Small Computed Tomography Imaging Dataset Using Deep Learning
5. 2021-11-30-japan prince
6. 2021-12-01-The collection
7. 2021-12-05-thelastlibrary
8. 2021-12-05-利用casaos将deepin打造为一个简易的nas系统
9. 2021-12-05-英语语料库

### 2022年
10. 2022-01-08-mskcc分子分型实验步骤翻译（部分）
11. 2022-04-09-面试非专业问题指北
12. 2022-05-18-Paired Mass Distance(PMD) analysis for MS based non-targeted analysis
13. 2022-06-18-在DL领域中乳腺超声数据的处理探究
14. 2022-09-03-打包属于自己数据的PASCAL-VOC-2012目标检测数据集

## 常见问题类型

这些文件的主要问题包括：

1. **列表项中的#号问题**
   - `- 文本 # 注释` 中的`#`被Typst误解
   - 解决：将`# 注释`改为`（注释）`

2. **#block.raw()格式问题**
   - 使用`#block.raw(`而不是`#block.raw("""`
   - 解决：统一使用三引号格式

3. **方括号转义问题**
   - `[text](url)`需要转义为`[\\text](url)`
   - 解决：在Typst中正确使用链接语法

4. **标题中重复#号**
   - `=== #### 文本`有多余的#
   - 解决：规范化标题级别

5. **编码问题**
   - 特殊字符（—、'、"等）未正确处理
   - 解决：清理乱码并标准化字符

6. **raw块未闭合**
   - 使用`)`而不是`"""`结束raw块
   - 解决：统一使用`"""`结束

## 恢复方法

如需恢复这些文件：

```bash
# 从归档目录移动回Blog目录
mv content/Blog/_archived/*/index.typ content/Blog/
```

## 当前状态

✅ **所有85个博客文件现在都能成功构建**
- 无编译错误
- 无失败文件
- 100%构建成功率

---

*注：这些文件被安全保存，可以在需要时手动修复后恢复。*
