"""
文献检索工具
负责从学术数据库搜索和获取论文
"""

import arxiv
import aiohttp
import asyncio
from typing import List, Dict, Optional
import json
import os
from datetime import datetime, timedelta
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PaperSearchEngine:
    """论文检索引擎"""
    
    def __init__(self):
        self.arxiv_client = arxiv.Client()
        self.cache_dir = "data/search_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 领域关键词映射
        self.domain_keywords = {
            'cs': ['computer science', 'cs', 'computing', 'algorithm'],
            'ai': ['artificial intelligence', 'ai', 'machine learning', 'deep learning', 'neural network'],
            'nlp': ['natural language processing', 'nlp', 'language model', 'text generation'],
            'cv': ['computer vision', 'cv', 'image processing', 'object detection'],
            'robotics': ['robotics', 'robot', 'automation', 'control system']
        }
    
    async def search_papers(
        self, 
        keywords: List[str], 
        max_results: int = 20,
        days_back: int = 365
    ) -> List[Dict]:
        """
        搜索论文
        
        Args:
            keywords: 关键词列表
            max_results: 最大结果数
            days_back: 搜索过去多少天的论文
            
        Returns:
            论文列表
        """
        print(f"  搜索关键词: {', '.join(keywords)}")
        print(f"  时间范围: 过去 {days_back} 天")
        
        # 构建查询
        query = self._build_query(keywords, days_back)
        print(f"  查询语句: {query}")
        
        # 检查缓存
        cache_key = self._get_cache_key(keywords, days_back)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            print(f"  使用缓存数据: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # 检查缓存是否过期
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                if (datetime.now() - cache_time).days < 1:  # 缓存1天
                    return cached_data['papers'][:max_results]
        
        # 执行搜索
        print(f"  正在检索 arXiv...")
        papers = []
        
        try:
            # 使用 arxiv API 搜索 - 简化选项
            search = arxiv.Search(
                query=query,
                max_results=min(max_results * 2, 50),  # 限制最大数量
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            results = list(search.results())
            print(f"  获取到 {len(results)} 篇候选论文")
            
            for i, result in enumerate(results, 1):
                try:
                    paper_info = self._parse_arxiv_result(result)
                    if paper_info:  # 确保成功解析
                        papers.append(paper_info)
                        if len(papers) >= max_results:
                            break
                except Exception as e:
                    print(f"    解析论文 {i} 时出错: {str(e)}")
                    continue
            
            print(f"  成功解析 {len(papers)} 篇论文")
            
            # 缓存结果
            self._cache_results(cache_file, papers)
            
        except Exception as e:
            print(f"  搜索过程中出错: {str(e)}")
            # 如果是查询错误，提供简化的备选方案
            if "HTTP 500" in str(e) or "HTTP 400" in str(e):
                print(f"  尝试使用简化查询重新搜索...")
                try:
                    # 使用更简单的查询
                    simple_query = ' '.join(keywords[:2])  # 只使用前2个关键词
                    print(f"  简化查询: {simple_query}")
                    
                    simple_search = arxiv.Search(
                        query=simple_query,
                        max_results=max_results,
                        sort_by=arxiv.SortCriterion.SubmittedDate
                    )
                    
                    simple_results = list(simple_search.results())
                    print(f"  简化搜索获取到 {len(simple_results)} 篇论文")
                    
                    for result in simple_results:
                        paper_info = self._parse_arxiv_result(result)
                        if paper_info:
                            papers.append(paper_info)
                            if len(papers) >= max_results:
                                break
                except Exception as e2:
                    print(f"  简化搜索也失败了: {str(e2)}")
        
        return papers
    
    def _build_query(self, keywords: List[str], days_back: int) -> str:
        """
        构建 arXiv 查询语句 - 最简化版本
        
        Args:
            keywords: 关键词列表
            days_back: 时间范围
            
        Returns:
            查询字符串
        """
        # 提取简短、有效的关键词
        valid_keywords = []
        for keyword in keywords[:2]:  # 最多2个关键词
            # 清理关键词：只保留字母
            clean = ''.join(c for c in keyword if c.isalpha()).lower()
            if clean and len(clean) > 2 and clean not in ['the', 'and', 'for', 'use']:
                valid_keywords.append(clean)
        
        # 如果没有有效关键词，使用默认值
        if not valid_keywords:
            valid_keywords = ['transformer']
        
        # 构建最简单的查询：只使用第一个关键词
        query = valid_keywords[0]
        
        return query
    
    def _parse_arxiv_result(self, result) -> Optional[Dict]:
        """
        解析 arXiv 搜索结果
        
        Args:
            result: arxiv.Result 对象
            
        Returns:
            论文信息字典
        """
        try:
            # 验证必要字段
            if not result.title or not result.summary:
                return None
                
            # 生成唯一ID
            paper_id = result.entry_id.split('/')[-1] if result.entry_id else str(hash(result.title))
            
            paper_info = {
                'id': paper_id,
                'title': result.title.strip(),
                'authors': [str(author) for author in result.authors],
                'summary': result.summary.strip(),
                'published': result.published.isoformat() if result.published else None,
                'updated': result.updated.isoformat() if result.updated else None,
                'pdf_url': result.pdf_url,
                'primary_category': result.primary_category if hasattr(result, 'primary_category') else None,
                'categories': result.categories if hasattr(result, 'categories') else [],
                'doi': getattr(result, 'doi', None),
                'journal_ref': getattr(result, 'journal_ref', None),
                'comment': getattr(result, 'comment', None)
            }
            
            # 添加统计信息
            paper_info['word_count'] = len(paper_info['summary'].split())
            paper_info['author_count'] = len(paper_info['authors'])
            
            return paper_info
            
        except Exception as e:
            print(f"解析论文时出错: {str(e)}")
            return None
    
    async def download_paper(self, paper_id: str, pdf_url: str) -> str:
        """
        下载论文PDF
        
        Args:
            paper_id: 论文ID
            pdf_url: PDF链接
            
        Returns:
            本地文件路径
        """
        papers_dir = "data/papers"
        os.makedirs(papers_dir, exist_ok=True)
        
        # 清理文件名，适配不同操作系统
        file_name = f"{paper_id.replace('/', '_').replace(':', '_')}.pdf"
        file_path = os.path.join(papers_dir, file_name)
        
        if os.path.exists(file_path):
            return file_path
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())
                        return file_path
                    else:
                        print(f"下载失败，状态码: {response.status}")
                        return None
        except Exception as e:
            print(f"下载 PDF 时出错: {str(e)}")
            return None
    
    def _get_cache_key(self, keywords: List[str], days_back: int) -> str:
        """生成缓存键"""
        key_string = "_".join(sorted(keywords)) + f"_{days_back}"
        # 替换特殊字符，适配不同文件系统
        return re.sub(r'[^a-zA-Z0-9_]', '', key_string)[:50]
    
    def _cache_results(self, cache_file: str, papers: List[Dict]):
        """缓存搜索结果"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'count': len(papers),
                'papers': papers
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"缓存结果时出错: {str(e)}")


# 测试函数
async def test_search():
    """测试搜索功能"""
    engine = PaperSearchEngine()
    
    # 测试搜索
    keywords = ["transformer", "optimization", "efficient attention"]
    results = await engine.search_papers(keywords, max_results=5)
    
    print(f"\n找到 {len(results)} 篇论文:")
    for paper in results:
        print(f"\n标题: {paper['title']}")
        print(f"作者: {', '.join(paper['authors'][:3])}")
        print(f"摘要: {paper['summary'][:200]}...")
        print(f"发布日期: {paper['published']}")
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(test_search())
