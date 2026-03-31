"""
论文研究分析 Agent 核心逻辑
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os

from tools.search import PaperSearchEngine
from tools.analysis import PaperAnalyzer
from tools.report import ReportGenerator


@dataclass
class ResearchSession:
    """研究会话状态"""
    topic: str
    keywords: List[str]
    search_results: List[Dict] = None
    analyzed_papers: List[Dict] = None
    report: str = None
    
    def __post_init__(self):
        if self.search_results is None:
            self.search_results = []
        if self.analyzed_papers is None:
            self.analyzed_papers = []


class PaperResearchAgent:
    """论文研究分析 Agent"""
    
    def __init__(self):
        self.search_engine = PaperSearchEngine()
        self.analyzer = PaperAnalyzer()
        self.report_generator = ReportGenerator()
        self.sessions: Dict[str, ResearchSession] = {}
    
    async def start_research(self, user_query: str) -> str:
        """
        启动一个新的研究任务
        
        Args:
            user_query: 用户的研究问题或主题
            
        Returns:
            研究计划概述
        """
        print(f"\n{'='*60}")
        print(f"🤖 Agent: 开始分析您的研究需求...")
        print(f"{'='*60}")
        
        # 1. 意图解析和关键词构建
        print("\n📋 步骤 1: 解析研究意图并构建关键词...")
        analysis = await self._analyze_intent(user_query)
        print(f"✓ 识别主题: {analysis['topic']}")
        print(f"✓ 构建关键词: {', '.join(analysis['keywords'])}")
        
        # 创建研究会话
        session_id = f"research_{len(self.sessions) + 1}"
        session = ResearchSession(
            topic=analysis['topic'],
            keywords=analysis['keywords']
        )
        self.sessions[session_id] = session
        
        # 2. 文献检索
        print(f"\n🔍 步骤 2: 检索相关文献...")
        search_results = await self.search_engine.search_papers(
            analysis['keywords'],
            max_results=20
        )
        session.search_results = search_results
        print(f"✓ 检索到 {len(search_results)} 篇相关论文")
        
        if not search_results:
            return "未找到相关论文，请尝试调整关键词或扩大搜索范围。"
        
        # 3. 相关性过滤和分析
        print(f"\n📄 步骤 3: 分析和过滤文献...")
        analyzed_papers = []
        for i, paper in enumerate(search_results[:10]):  # 分析前10篇
            print(f"  分析论文 {i+1}/{min(10, len(search_results))}: {paper['title'][:50]}...")
            analysis_result = await self.analyzer.analyze_paper(paper)
            if analysis_result['relevance_score'] > 0.6:  # 相关性阈值
                analyzed_papers.append(analysis_result)
        
        session.analyzed_papers = analyzed_papers
        print(f"✓ 筛选出 {len(analyzed_papers)} 篇高相关性论文")
        
        # 4. 生成综述
        print(f"\n📝 步骤 4: 生成综述报告...")
        if analyzed_papers:
            report = await self.report_generator.generate_report(
                session.topic,
                analyzed_papers,
                analysis['keywords']
            )
            session.report = report
            
            # 保存报告
            report_path = f"data/reports/report_{session_id}.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✓ 报告已生成: {report_path}")
        
        print(f"\n{'='*60}")
        print("✅ 研究完成！")
        print(f"{'='*60}")
        
        return session.report
    
    async def _analyze_intent(self, query: str) -> Dict[str, Any]:
        """
        分析用户意图并构建关键词
        
        Args:
            query: 用户查询
            
        Returns:
            包含主题和关键词的字典
        """
        # 使用 analyzer 进行意图分析
        return await self.analyzer.analyze_research_intent(query)
    
    async def continue_research(self, session_id: str, feedback: str) -> str:
        """
        基于用户反馈继续研究
        
        Args:
            session_id: 会话ID
            feedback: 用户反馈
            
        Returns:
            更新后的研究综述
        """
        if session_id not in self.sessions:
            return "未找到对应的研究会话，请重新开始。"
        
        session = self.sessions[session_id]
        
        # 分析用户反馈，调整研究方向
        feedback_analysis = await self.analyzer.analyze_feedback(feedback)
        
        if feedback_analysis['action'] == 'expand':
            # 扩展搜索
            new_keywords = feedback_analysis['new_keywords']
            print(f"扩展搜索关键词: {new_keywords}")
            
            new_results = await self.search_engine.search_papers(
                new_keywords,
                max_results=15
            )
            
            # 去重并添加新结果
            existing_ids = {p['id'] for p in session.search_results}
            new_papers = [p for p in new_results if p['id'] not in existing_ids]
            
            session.search_results.extend(new_papers)
            print(f"新增 {len(new_papers)} 篇论文到搜索结果")
            
        elif feedback_analysis['action'] == 'focus':
            # 聚焦特定方向
            focus_topic = feedback_analysis['focus_topic']
            print(f"聚焦主题: {focus_topic}")
            
            # 重新分析已收集的论文，筛选相关 subset
            focused_papers = []
            for paper in session.search_results:
                if focus_topic.lower() in paper['title'].lower() or \
                   focus_topic.lower() in paper['summary'].lower():
                    focused_papers.append(paper)
            
            session.analyzed_papers = focused_papers[:10]
            print(f"筛选出 {len(session.analyzed_papers)} 篇聚焦论文")
        
        # 重新生成报告
        new_report = await self.report_generator.generate_report(
            session.topic,
            session.analyzed_papers,
            session.keywords
        )
        session.report = new_report
        
        # 保存更新后的报告
        report_path = f"data/reports/report_{session_id}_updated.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(new_report)
        
        return f"基于您的反馈，已更新研究报告:\n{new_report}"
    
    def get_session_summary(self, session_id: str) -> str:
        """
        获取研究会话的摘要信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话摘要
        """
        if session_id not in self.sessions:
            return "未找到对应的研究会话。"
        
        session = self.sessions[session_id]
        return f"""
        📊 研究会话摘要 ({session_id})
        
        🎯 研究主题: {session.topic}
        🔑 关键词: {', '.join(session.keywords)}
        📚 检索论文: {len(session.search_results)} 篇
        ✅ 分析论文: {len(session.analyzed_papers)} 篇
        📝 报告状态: {'已生成' if session.report else '未生成'}
        """


if __name__ == "__main__":
    # 测试 Agent
    async def test_agent():
        agent = PaperResearchAgent()
        
        # 测试查询
        test_query = "我想了解最近一年关于Transformer架构优化的最新研究"
        result = await agent.start_research(test_query)
        print("\n📄 生成的报告:")
        print(result)
    
    asyncio.run(test_agent())
