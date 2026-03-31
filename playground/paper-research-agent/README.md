# 论文研究分析 Agent

一个专注于人工智能和计算机领域的智能研究助手，能够进行：
- 意图解析与关键词构建
- 自动化文献检索
- 相关性过滤与智能阅读
- 综述与报告生成

## 功能特性

### 1. 意图解析与关键词构建
- 理解用户的研究问题
- 提取核心概念和关键词
- 构建优化的检索查询

### 2. 自动化文献检索
- 支持 arXiv、IEEE、ACM 等学术数据库
- 智能分页检索和去重
- 元数据提取和结构化存储

### 3. 相关性过滤与智能阅读
- 基于摘要的初步筛选
- 全文分析和关键信息提取
- 相关性评分和排序

### 4. 综述与报告生成
- 自动分析文献间关系
- 生成结构化的文献综述
- 支持多种输出格式（Markdown、PDF等）

## 架构设计

```
paper-research-agent/
├── main.py              # 主程序入口
├── agent.py             # Agent 核心逻辑
├── tools/               # 工具函数
│   ├── search.py        # 文献检索工具
│   ├── analysis.py      # 文本分析工具
│   └── report.py        # 报告生成工具
├── knowledge/           # 领域知识
│   └── research_methods.md  # 研究方法论
└── data/               # 数据存储
    ├── papers/         # 下载的论文
    └── reports/        # 生成的报告
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 Agent
python main.py
```

## 使用示例

```
用户: 我想了解最近一年关于Transformer架构优化的最新研究

Agent:
1. 解析意图：Transformer优化相关研究
2. 构建关键词：transformer optimization, attention mechanism, efficient transformers
3. 检索文献：在arXiv等数据库搜索相关论文
4. 过滤分析：筛选高相关性论文并分析
5. 生成综述：提供研究现状、主要方向、关键论文总结
```
