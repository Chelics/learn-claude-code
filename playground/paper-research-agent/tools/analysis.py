"""
文本分析工具
负责论文内容的分析和相关性评估
"""

import re
import nltk
from typing import List, Dict, Any, Optional
import asyncio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dataclasses import dataclass
import sys
import os

# import torch
# from transformers import pipeline

# 确保必要的NLTK数据已下载
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# try:
#     nltk.data.find('corpora/stopwords')
# except LookupError:
#     nltk.download('stopwords')


@dataclass
class PaperAnalysis:
    """论文分析结果"""
    paper_id: str
    relevance_score: float
    key_findings: List[str]
    methodology: str
    novelty_score: float
    contribution_summary: str
    technical_terms: List[str]
    experimental_results: List[str]


class PaperAnalyzer:
    """论文分析器"""
    
    def __init__(self):
        # 研究相关关键词库，按照通用性分为不同优先级
        self.research_keywords = {
            'high': [
                'novel', 'innovative', 'state-of-the-art', 'sota', 'benchmark', 'evaluation',
                'experiment', 'results', 'performance', 'improvement', 'approach', 'method',
                'propose', 'introduce', 'demonstrate', 'show', 'validate', 'significant'
            ],
            'medium': [
                'algorithm', 'model', 'framework', 'architecture', 'network', 'system',
                'analysis', 'study', 'investigation', 'research', 'development',
                'optimization', 'efficient', 'scalable', 'robust', 'accurate'
            ],
            'low': [
                'paper', 'work', 'study', 'research', 'investigation', 'analysis', 'development',
                'based', 'using', 'with', 'through', 'via', 'by'
            ]
        }
        
        # 高质量论文特征词
        self.quality_indicators = [
            'comprehensive', 'extensive', 'thorough', 'systematic',
            'rigorous', 'sound', 'solid', 'well-founded',
            'empirical', 'experimental', 'theoretical', 'analytical',
            'comparative', 'ablation', 'baseline', 'state-of-the-art'
        ]
        
        # 使用更基础的文本向量化方法
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
        except Exception as e:
            print(f"初始化向量器时出错: {e}，使用简化版本")
            self.vectorizer = None
        
        # 初始化 Hugging Face 模型（可选）
        # self.summarizer = None
        # try:
        #     self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # except Exception as e:
        #     print(f"加载摘要模型失败: {e}，将使用基于规则的方法")
    
    async def analyze_research_intent(self, query: str) -> Dict[str, Any]:
        """
        分析研究意图并构建关键词
        
        Args:
            query: 用户查询
            
        Returns:
            分析结果包含主题和关键词
        """
        print(f"    分析查询: {query}")
        
        # 提取核心主题
        topic = self._extract_topic(query)
        print(f"    识别主题: {topic}")
        
        # 构建搜索关键词
        keywords = self._build_search_keywords(query, topic)
        print(f"    构建关键词: {', '.join(keywords[:5])}")
        
        # 识别研究类型
        research_type = self._identify_research_type(query)
        print(f"    研究类型: {research_type}")
        
        return {
            'topic': topic,
            'keywords': keywords,
            'research_type': research_type,
            'original_query': query
        }
    
    async def analyze_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单篇论文
        
        Args:
            paper: 论文信息字典
            
        Returns:
            分析结果
        """
        paper_id = paper.get('id', 'unknown')
        title = paper.get('title', '')
        summary = paper.get('summary', '')
        
        if not title or not summary:
            return {
                'paper_id': paper_id,
                'relevance_score': 0.0,
                'analysis_failed': True,
                'error': 'Missing title or summary'
            }
        
        try:
            # 计算相关性分数
            relevance_score = await self._calculate_relevance(title, summary)
            
            # 提取关键发现
            key_findings = self._extract_key_findings(title, summary)
            
            # 识别研究方法
            methodology = self._identify_methodology(summary)
            
            # 评估创新性
            novelty_score = self._assess_novelty(title, summary, paper)
            
            # 总结贡献
            contribution_summary = self._extract_contribution(title, summary)
            
            # 提取技术术语
            technical_terms = self._extract_technical_terms(summary)
            
            analysis_result = {
                'paper_id': paper_id,
                'title': title,
                'relevance_score': relevance_score,
                'key_findings': key_findings,
                'methodology': methodology,
                'novelty_score': novelty_score,
                'contribution_summary': contribution_summary,
                'technical_terms': technical_terms,
                'paper_metadata': paper
            }
            
            print(f"    ✓ 相关性: {relevance_score:.2f} | 新颖性: {novelty_score:.2f}")
            
            return analysis_result
            
        except Exception as e:
            print(f"    ✗ 分析失败: {str(e)}")
            return {
                'paper_id': paper_id,
                'relevance_score': 0.0,
                'analysis_failed': True,
                'error': str(e)
            }
    
    async def analyze_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        分析用户反馈
        
        Args:
            feedback: 用户反馈
            
        Returns:
            反馈分析结果
        """
        feedback_lower = feedback.lower()
        
        # 判断反馈类型
        if any(word in feedback_lower for word in ['more', 'add', 'also', 'include', 'expand']):
            # 扩展搜索
            new_keywords = self._extract_keywords_from_feedback(feedback)
            return {
                'action': 'expand',
                'new_keywords': new_keywords,
                'feedback': feedback
            }
        elif any(word in feedback_lower for word in ['focus', 'specific', 'particular', 'narrow']):
            # 聚焦搜索
            extracted_topics = self._extract_topic_from_feedback(feedback)
            return {
                'action': 'focus',
                'focus_topic': extracted_topics,
                'feedback': feedback
            }
        else:
            # 重新分析
            return {
                'action': 'reanalyze',
                'feedback': feedback
            }
    
    def _extract_topic(self, query: str) -> str:
        """提取核心主题"""
        # 去除常见停用词
        stop_words = {'i', 'want', 'to', 'learn', 'about', 'research', 'on', 'in', 'the', 'a', 'an', 'and', 'or', 'but', 'recent', 'latest', 'new', 'studies', 'papers'}
        words = query.lower().split()
        
        # 提取关键词（去除停用词）
        keywords = [word for word in words if word.isalnum() and word not in stop_words]
        
        if not keywords:
            return query.strip()
        
        # 返回前3-8个关键词作为主题
        return ' '.join(keywords[:6])
    
    def _build_search_keywords(self, query: str, topic: str) -> List[str]:
        """构建搜索关键词"""
        keywords = []
        
        # 从查询中提取基础关键词
        words = re.findall(r'[a-zA-Z]+', query.lower())
        words = [w for w in words if len(w) > 2 and w not in {'the', 'and', 'for', 'with', 'from', 'that', 'this', 'are', 'was', 'has', 'have', 'had'}]
        
        # 添加主题词
        keywords.extend(topic.split()[:3])
        
        # 添加关键词变体
        for word in words[:5]:
            if word not in keywords:
                keywords.append(word)
                
            # 添加相关术语
            related_terms = self._get_related_terms(word)
            keywords.extend([term for term in related_terms if term not in keywords])
        
        # 为AI/ML相关查询添加通用关键词
        if any(term in query.lower() for term in ['ai', 'artificial', 'intelligence', 'machine', 'learning', 'deep', 'neural']):
            keywords.extend(['machine learning', 'deep learning', 'neural networks'])
        
        # 去重并限制数量
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
                if len(unique_keywords) >= 7:
                    break
        
        return unique_keywords[:7]
    
    def _get_related_terms(self, word: str) -> List[str]:
        """获取相关术语"""
        term_mapping = {
            'transformer': ['attention', 'bert', 'gpt', 'language model'],
            'optimization': ['efficient', 'fast', 'acceleration', 'improvement'],
            'network': ['architecture', 'model', 'system', 'framework'],
            'learning': ['training', 'fine-tuning', 'adaptation', 'generalization'],
            'computer': ['computing', 'system', 'architecture', 'hardware'],
            'algorithm': ['method', 'technique', 'approach', 'procedure']
        }
        return term_mapping.get(word.lower(), [])
    
    def _identify_research_type(self, query: str) -> str:
        """识别研究类型"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['survey', 'review', 'overview', 'literature']):
            return 'literature_review'
        elif any(word in query_lower for word in ['compare', 'comparison', 'versus']):
            return 'comparative'
        elif any(word in query_lower for word in ['improve', 'enhance', 'optimize', 'better']):
            return 'optimization'
        elif any(word in query_lower for word in ['new', 'novel', 'propose', 'introduce']):
            return 'innovation'
        else:
            return 'general_research'
    
    async def _calculate_relevance(self, title: str, summary: str) -> float:
        """
        计算论文相关性分数
        
        Args:
            title: 论文标题
            summary: 论文摘要
            
        Returns:
            相关性分数 (0-1)
        """
        text = f"{title} {summary}".lower()
        
        # 基础分数
        base_score = 0.5
        
        # 标题中包含技术词的加分
        title_words = re.findall(r'[a-zA-Z]+', title.lower())
        tech_words = [w for w in title_words if len(w) > 4 and w not in {
            'using', 'based', 'with', 'from', 'that', 'this', 'these', 'those', 'paper', 'study'}]
        
        base_score += min(len(tech_words) * 0.05, 0.2)  # 最多加0.2
        
        # 摘要质量指标
        summary_sentences = summary.split('.')
        if len(summary_sentences) >= 3:  # 有足够多的句子
            base_score += 0.1
        
        # 摘要长度适中（不太短也不太长）
        words = summary.split()
        if 100 <= len(words) <= 400:
            base_score += 0.05
        
        # 检查高质量指标词
        quality_count = sum(1 for indicator in self.quality_indicators if indicator in text)
        base_score += min(quality_count * 0.03, 0.15)
        
        # 平衡基准分，避免过高或过低
        relevance_score = max(0.1, min(1.0, base_score))
        
        return relevance_score
    
    def _extract_key_findings(self, title: str, summary: str) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 在标题中找关键信息
        if ':' in title:
            parts = title.split(':')
            if len(parts) > 1:
                findings.append(f"Approach: {parts[1].strip()}")
        
        # 在摘要中找结果描述
        patterns = [
            r'(?:show|demonstrate|prove|validate|achieve|obtain|attain)(?:s)?\s+([^.;]+[0-9]+%?[^.;]*)',
            r'(?:result|performance|accuracy|improvement|gain|boost)(?:s)?\s+([^.;]+[0-9]+%?[^.;]*)',
            r'(?:outperform|surpass|exceed|beat)(?:s)?\s+([^.;]+)',
            r'(?:reduc(?:e|es|ing)|decreas(?:e|es|ing))\s+([^.;]+[0-9]+%?[^.;]*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, summary, re.IGNORECASE)
            findings.extend([f"Result: {match.strip()}" for match in matches[:2]])
        
        # 如果找到结果，添加到发现列表
        if findings:
            return findings[:3]  # 限制数量
        else:
            # 提取方法描述作为备选
            method_matches = re.findall(r'(?:propose|present|introduce)(?:s)?\s+([^.;]+)', summary, re.IGNORECASE)
            if method_matches:
                return [f"Method: {match.strip()}" for match in method_matches[:2]]
        
        return ["Key approach described in abstract"]
    
    def _identify_methodology(self, summary: str) -> str:
        """识别研究方法"""
        summary_lower = summary.lower()
        
        if any(word in summary_lower for word in ['experiment', 'empirical', 'evaluation', 'benchmark']):
            return 'empirical'
        elif any(word in summary_lower for word in ['theoretical', 'theory', 'prove', 'proof', 'analysis']):
            return 'theoretical'
        elif any(word in summary_lower for word in ['survey', 'review', 'comprehensive', 'overview']):
            return 'survey'
        else:
            return 'proposed_method'
    
    def _assess_novelty(self, title: str, summary: str, paper: Dict) -> float:
        """评估创新性"""
        text = f"{title} {summary}".lower()
        
        novelty_score = 0.5  # 基础分
        
        # 新颖性关键词
        novelty_keywords = [
            'novel', 'new', 'innovative', 'first', 'introduce', 'propose',
            'exploit', 'address', 'tackle', 'handle', 'mitigate',
            'improve', 'enhance', 'outperform', 'surpass', 'beat', 'exceed'
        ]
        
        # 统计新颖性词
        novelty_count = sum(1 for word in novelty_keywords if word in text)
        novelty_score += min(novelty_count * 0.05, 0.3)
        
        # 标题新颖性特征
        if len(title.split()) <= 15:  # 简洁的标题
            novelty_score += 0.05
        
        # 作者数量适当（不太少也不太多）
        authors = paper.get('authors', [])
        if 2 <= len(authors) <= 6:
            novelty_score += 0.05
        
        # 发表在近期
        try:
            from datetime import datetime
            published = paper.get('published')
            if published:
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
                if days_old < 365:  # 一年内的论文
                    novelty_score += 0.1
        except:
            pass
        
        # 限制在合理范围内
        novelty_score = max(0.3, min(1.0, novelty_score))
        
        return novelty_score
    
    def _extract_contribution(self, title: str, summary: str) -> str:
        """提取论文贡献"""
        # 从摘要中提取贡献陈述
        patterns = [
            r'(?:contribution|contributions)(?:s)?\s+([^.;]+)',
            r'(?:we|this paper|our work)(?:\s+\w+){0,4}\s+([^.;]+?)(?:\.|;)',
            r'(?:show|demonstrate|prove|validate)(?:s)?\s+([^.;]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, summary, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # 如果没有明确的贡献陈述，生成一个
        return f"Investigates {title.lower()} with novel approaches and insights"
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """提取技术术语"""
        # 简单的技术术语提取
        words = re.findall(r'[A-Z][a-z]+|[a-z]+', text)
        
        # 过滤和筛选可能的术语
        potential_terms = []
        for word in words:
            if len(word) >= 6 and word.islower() and word not in {
                'through', 'between', 'however', 'therefore', 'because', 'although',
                'throughout', 'particularly', 'especially', 'generally'}:
                # 检查是否可能是术语（包含技术词根）
                if any(root in word for root in ['network', 'model', 'algorithm', 'system', 
                                                  'method', 'approach', 'framework', 'technique']):
                    potential_terms.append(word)
        
        # 去重并限制数量
        return list(set(potential_terms))[:8]
    
    def _extract_keywords_from_feedback(self, feedback: str) -> List[str]:
        """从反馈中提取关键词"""
        return self._build_search_keywords(feedback, feedback[:50])
    
    def _extract_topic_from_feedback(self, feedback: str) -> str:
        """从反馈中提取主题"""
        return self._extract_topic(feedback)


# 测试函数
async def test_analyzer():
    """测试分析器"""
    analyzer = PaperAnalyzer()
    
    # 测试意图分析
    query = "我想了解最近一年关于Transformer架构优化的最新研究"
    intent_analysis = await analyzer.analyze_research_intent(query)
    print("意图分析结果:")
    print(json.dumps(intent_analysis, indent=2, ensure_ascii=False))
    
    # 测试论文分析
    test_paper = {
        'id': 'test123',
        'title': 'Efficient Attention Mechanisms for Large Language Models',
        'summary': 'We propose a novel attention mechanism that reduces computational complexity from O(n²) to O(n log n). Our experiments demonstrate 40% speed improvement while maintaining accuracy. We validate our approach on language modeling tasks and achieve state-of-the-art results.',
        'authors': ['John Smith', 'Jane Doe'],
        'published': '2024-01-15T00:00:00Z',
        'categories': [
            'cs.CL',
            'cs.LG',
            'cs.AI'
        ]
    }
    
    print("\n论文分析结果:")
    paper_analysis = await analyzer.analyze_paper(test_paper)
    print(f"相关性分数: {paper_analysis['relevance_score']:.2f}")
    print(f"关键发现: {paper_analysis['key_findings']}")
    print(f"方法论: {paper_analysis['methodology']}")
    print(f"新颖性分数: {paper_analysis['novelty_score']:.2f}")


if __name__ == "__main__":
    import json
    asyncio.run(test_analyzer())
