#!/usr/bin/env python3
"""测试脚本 - 验证 Agent 核心功能"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.search import PaperSearchEngine
from tools.analysis import PaperAnalyzer
from tools.report import ReportGenerator


async def test_search():
    """测试搜索功能"""
    print("🔍 测试搜索功能...")
    engine = PaperSearchEngine()
    
    keywords = ["transformer", "optimization"]
    results = await engine.search_papers(keywords, max_results=3)
    
    print(f"✓ 检索到 {len(results)} 篇论文")
    if results:
        for i, paper in enumerate(results[:2], 1):
            print(f"  {i}. {paper['title'][:60]}...")
    
    return results


async def test_analysis(papers):
    """测试分析功能"""
    print("\n📄 测试分析功能...")
    analyzer = PaperAnalyzer()
    
    analyzed = []
    for paper in papers:
        result = await analyzer.analyze_paper(paper)
        analyzed.append(result)
        print(f"✓ 分析: {paper['title'][:50]}... (相关性: {result['relevance_score']:.2f})")
    
    return analyzed


async def test_report(topic, papers, keywords):
    """测试报告生成功能"""
    print("\n📝 测试报告生成功能...")
    generator = ReportGenerator()
    
    report = await generator.generate_report(topic, papers, keywords)
    
    # 保存报告
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "full_test_report.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ 报告已生成: {report_path}")
    print(f"  报告长度: {len(report)} 字符")
    
    return report


async def test_intent_analysis():
    """测试意图分析"""
    print("\n🤔 测试意图分析...")
    analyzer = PaperAnalyzer()
    
    query = "我想了解最近一年关于Transformer架构优化的最新研究"
    result = await analyzer.analyze_research_intent(query)
    
    print(f"✓ 识别主题: {result['topic']}")
    print(f"✓ 构建关键词: {', '.join(result['keywords'])}")
    
    return result


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("🚀 Agent 功能测试")
    print("=" * 60)
    
    try:
        # 1. 测试意图分析
        intent_result = await test_intent_analysis()
        
        # 2. 测试搜索
        search_results = await test_search()
        
        if not search_results:
            print("❌ 没有检索到论文，测试中止")
            return
        
        # 3. 测试分析
        analyzed_papers = await test_analysis(search_results[:3])  # 只分析前3篇
        
        # 4. 测试报告生成
        topic = "Transformer Optimization Research"
        keywords = intent_result['keywords']
        
        report = await test_report(topic, analyzed_papers, keywords)
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print(f"\n📁 生成的文件:")
        print(f"  - 完整报告: test_output/full_test_report.md")
        print(f"  - 报告预览 (前500字符):\n")
        print(report[:500] + "...")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
