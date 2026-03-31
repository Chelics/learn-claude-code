"""
报告生成工具
负责生成结构化的文献综述报告
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        pass
    
    async def generate_report(
        self, 
        topic: str, 
        analyzed_papers: List[Dict[str, Any]], 
        keywords: List[str]
    ) -> str:
        """
        生成综述报告
        
        Args:
            topic: 研究主题
            analyzed_papers: 分析过的论文列表
            keywords: 关键词列表
            
        Returns:
            Markdown格式的报告
        """
        print(f"    生成主题: {topic}")
        print(f"    论文数量: {len(analyzed_papers)}")
        print(f"    关键词: {', '.join(keywords[:5])}")
        
        # 分析论文数据以生成统计信息
        stats = self._analyze_papers_statistics(analyzed_papers)
        
        # 组织论文成主题群组
        paper_groups = self._group_papers_by_theme(analyzed_papers)
        
        # 生成关键见解
        key_insights = self._generate_key_insights(analyzed_papers, stats)
        
        # 渲染报告
        report = self._render_report(topic, analyzed_papers, stats, paper_groups, key_insights, keywords)
        
        print(f"    报告生成完成")
        
        return report
    
    def _analyze_papers_statistics(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析论文统计数据"""
        if not papers:
            return {'error': 'No papers to analyze'}
        
        # 相关性统计
        relevance_scores = [p.get('relevance_score', 0) for p in papers]
        
        # 新颖性统计
        novelty_scores = [p.get('novelty_score', 0) for p in papers]
        
        # 时间分布
        publication_dates = []
        for paper in papers:
            date_str = paper.get('paper_metadata', {}).get('published')
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    publication_dates.append(date)
                except:
                    continue
        
        # 方法论分布
        methodologies = [p.get('methodology', 'unknown') for p in papers]
        method_counts = {}
        for method in methodologies:
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # 技术术语频率
        all_terms = []
        for paper in papers:
            terms = paper.get('technical_terms', [])
            all_terms.extend(terms)
        
        term_frequency = {}
        for term in all_terms:
            term_frequency[term] = term_frequency.get(term, 0) + 1
        
        # 热门技术术语
        popular_terms = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        stats = {
            'avg_relevance': sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            'avg_novelty': sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0,
            'high_relevance_count': sum(1 for s in relevance_scores if s > 0.7),
            'high_novelty_count': sum(1 for s in novelty_scores if s > 0.7),
            'publication_dates': publication_dates,
            'methodology_distribution': method_counts,
            'popular_terms': popular_terms
        }
        
        return stats
    
    def _group_papers_by_theme(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按主题分组论文"""
        # 提取所有技术术语
        all_terms = []
        for paper in papers:
            terms = paper.get('technical_terms', [])
            title_words = paper.get('title', '').lower().split()
            all_terms.extend(terms + [w for w in title_words if len(w) > 5])
        
        # 统计术语频率
        term_freq = {}
        for term in all_terms:
            if len(term) >= 4:  # 只考虑较有意义的术语
                term_freq[term] = term_freq.get(term, 0) + 1
        
        # 识别主要主题（出现频率较高的术语）
        main_themes = [term for term, freq in term_freq.items() if freq >= 2]
        main_themes = sorted(set(main_themes), key=lambda x: term_freq[x], reverse=True)[:5]
        
        # 按主题分组论文
        groups = []
        for theme in main_themes:
            group_papers = []
            for paper in papers:
                title = paper.get('title', '').lower()
                terms = paper.get('technical_terms', [])
                if theme in title or theme in ' '.join(terms):
                    group_papers.append(paper)
            
            if group_papers:
                groups.append({
                    'theme': theme,
                    'theme_name': theme.replace('_', ' ').title(),
                    'papers': group_papers,
                    'paper_count': len(group_papers)
                })
        
        return groups
    
    def _generate_key_insights(self, papers: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[str]:
        """生成关键见解"""
        insights = []
        
        if not papers:
            return insights
        
        # 趋势分析
        recent_papers = [p for p in papers if self._is_published_recently(p)]
        if len(recent_papers) > len(papers) * 0.7:
            insights.append("🔥 **研究热点**: 大多数论文在最近6个月内发表，表明这是当前研究热点")
        
        # 方法论洞察
        method_dist = stats.get('methodology_distribution', {})
        if method_dist:
            most_common_method = max(method_dist.items(), key=lambda x: x[1])
            insights.append(f"🧪 **主要方法**: {most_common_method[0]}方法占主导地位 ({most_common_method[1]}篇论文)")
        
        # 质量评估
        relevance_scores = [p.get('relevance_score', 0) for p in papers]
        high_quality_papers = sum(1 for s in relevance_scores if s >= 0.8)
        if high_quality_papers >= 3:
            insights.append(f"⭐ **高质量研究**: 发现{high_quality_papers}篇高度相关的优秀论文")
        
        # 技术创新分析
        popular_terms = stats.get('popular_terms', [])
        if len(popular_terms) >= 3:
            top_technologies = [term for term, freq in popular_terms[:3]]
            insights.append(f"🚀 **关键技术**: {', '.join(top_technologies)}是研究中的核心技术")
        
        # 新兴主题识别
        novelty_scores = [p.get('novelty_score', 0) for p in papers]
        high_novelty_papers = sum(1 for s in novelty_scores if s >= 0.75)
        
        if high_novelty_papers >= 2:
            insights.append(f"💡 **创新趋势**: {high_novelty_papers}篇论文展现出较高的创新性，值得关注")
        
        return insights
    
    def _render_report(
        self, 
        topic: str, 
        papers: List[Dict[str, Any]], 
        stats: Dict[str, Any],
        paper_groups: List[Dict[str, Any]],
        key_insights: List[str],
        keywords: List[str]
    ) -> str:
        """渲染报告"""
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 报告头部
        report = f"""# 📊 文献综述报告: {topic}

*生成日期: {date_str}*  
*关键词: {', '.join(keywords[:5])}*  
*分析论文数量: {len(papers)}篇*

---

## 🎯 执行摘要

"""
        
        # 添加关键见解
        for insight in key_insights:
            report += f"{insight}\n\n"
        
        # 研究概况
        report += f"""---

## 📈 研究概况

### 总体统计
- **平均相关性**: {stats['avg_relevance']:.2f}/1.00
- **平均新颖性**: {stats['avg_novelty']:.2f}/1.00
- **高相关性论文**: {stats['high_relevance_count']}篇 (≥0.7)
- **高新颖性论文**: {stats['high_novelty_count']}篇 (≥0.7)

"""
        
        # 热门技术术语
        if stats.get('popular_terms'):
            report += "### 热门技术术语\n"
            for term, freq in stats['popular_terms']:
                report += f"- **{term}**: 出现在{freq}篇论文中\n"
            report += "\n"
        
        # 方法论分布
        if stats.get('methodology_distribution'):
            report += "### 研究方法分布\n"
            for method, count in sorted(stats['methodology_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True):
                report += f"- {method}: {count}篇论文\n"
            report += "\n"
        
        # 论文详细分析
        report += """---

## 📚 论文详细分析

"""
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', '未知标题')
            relevance = paper.get('relevance_score', 0)
            novelty = paper.get('novelty_score', 0)
            methodology = paper.get('methodology', '未知')
            contribution = paper.get('contribution_summary', '')
            findings = paper.get('key_findings', [])
            metadata = paper.get('paper_metadata', {})
            authors = metadata.get('authors', ['未知作者'])
            published = metadata.get('published', '')[:10] if metadata.get('published') else '未知'
            pdf_url = metadata.get('pdf_url', '')
            
            # 只为高相关性论文生成详细内容
            if relevance >= 0.6:
                stars = "⭐" * int(relevance * 5)
                
                report += f"""### {i}. {title}

- **相关性分数**: {relevance:.2f} {stars}
- **新颖性分数**: {novelty:.2f} 💡
- **研究方法**: {methodology}
- **作者**: {', '.join(authors[:5])}
- **发表日期**: {published}

**研究贡献**: {contribution}

"""
                
                if findings:
                    report += "**关键发现**:\n"
                    for finding in findings[:3]:
                        report += f"- {finding}\n"
                    report += "\n"
                
                if pdf_url:
                    report += f"**PDF链接**: [点击下载]({pdf_url})\n"
                
                report += "---\n\n"
        
        # 研究主题分析
        if paper_groups:
            report += """---

## 🎯 研究主题分析

"""
            for group in paper_groups:
                theme_name = group['theme_name']
                paper_count = group['paper_count']
                
                report += f"""### {theme_name} ({paper_count}篇论文)

"""
                
                for paper in group['papers'][:3]:
                    title = paper.get('title', '')
                    relevance = paper.get('relevance_score', 0)
                    contribution = paper.get('contribution_summary', '')
                    report += f"- **{title}** (相关性: {relevance:.2f})\n"
                    if contribution:
                        report += f"  - {contribution[:150]}...\n"
                
                if paper_count > 3:
                    report += f"\n*以及其他{paper_count - 3}篇相关论文...*\n"
                report += "\n"
        
        # 结尾
        report += """---

## 🔍 研究建议

### 深入研究建议
1. 对高相关性论文进行全文精读
2. 关注关键技术的演进和最新进展
3. 探索研究空白和潜在创新方向

### 文献管理
- 建议建立个人文献库，分类存储相关论文
- 定期跟踪最新研究动态
- 关注顶级会议和期刊的发表趋势

---

*本报告由 AI 论文研究分析 Agent 自动生成*  
*数据来源: arXiv 学术预印本数据库*  
*生成工具: PaperResearchAgent v1.0*
"""
        
        return report
    
    def _is_published_recently(self, paper: Dict[str, Any], months: int = 6) -> bool:
        """检查论文是否为近期发表"""
        try:
            date_str = paper.get('paper_metadata', {}).get('published')
            if date_str:
                from datetime import datetime
                pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
                return days_old <= months * 30
        except:
            pass
        return False


# 测试函数
async def test_report_generator():
    """测试报告生成器"""
    generator = ReportGenerator()
    
    # 创建测试数据
    test_papers = [
        {
            'paper_id': 'test1',
            'title': 'Efficient Transformer Optimization Techniques',
            'relevance_score': 0.85,
            'novelty_score': 0.78,
            'key_findings': ['40% speed improvement', 'Memory usage reduced by 35%'],
            'methodology': 'empirical',
            'contribution_summary': 'Proposed novel attention mechanism optimization',
            'technical_terms': ['transformer', 'attention', 'optimization', 'efficiency'],
            'paper_metadata': {
                'authors': ['John Smith', 'Alice Johnson'],
                'published': '2024-01-15T00:00:00Z',
                'pdf_url': 'https://arxiv.org/test1.pdf'
            }
        }
    ] * 3  # 复制几份测试
    
    # 生成报告
    report = await generator.generate_report(
        topic="Transformer Architecture Optimization",
        analyzed_papers=test_papers,
        keywords=['transformer', 'optimization', 'efficiency']
    )
    
    # 保存测试报告
    os.makedirs('test_output', exist_ok=True)
    with open('test_output/test_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("测试报告已生成: test_output/test_report.md")
    print(f"报告长度: {len(report)} 字符")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_report_generator())
