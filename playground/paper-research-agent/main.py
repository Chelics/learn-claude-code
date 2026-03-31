"""
论文研究分析 Agent - 主程序入口
"""

import asyncio
import sys
import os
from typing import List, Dict, Any, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import PaperResearchAgent


def print_welcome():
    """打印欢迎信息"""
    print("=" * 70)
    print("📚 论文研究分析 Agent")
    print("专注于人工智能和计算机领域的学术文献研究")
    print("=" * 70)
    print()
    print("功能特性:")
    print("  🤖 智能意图解析与关键词构建")
    print("  🔍 自动化文献检索 (arXiv)")
    print("  📄 相关性过滤与智能分析")
    print("  📝 结构化综述与报告生成")
    print()
    print("使用说明:")
    print("  1. 输入您的研究问题或感兴趣的主题")
    print("  2. Agent 将自动检索、分析相关论文")
    print("  3. 生成包含关键发现和见解的综述报告")
    print()
    print("示例查询:")
    print("  • 最近一年关于Transformer架构优化的研究")
    print("  • 大语言模型在代码生成方面的应用")
    print("  • 计算机视觉中的注意力机制最新进展")
    print("=" * 70)
    print()


async def interactive_mode():
    """交互式模式"""
    agent = PaperResearchAgent()
    
    print("🚀 启动交互式模式...")
    print("输入 'quit' 或 'exit' 退出程序")
    print("输入 'help' 查看帮助信息")
    print()
    
    session_id = None
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n💬 请输入您的研究问题: ").strip()
            
            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit']:
                print("👋 感谢使用，再见！")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'status':
                if session_id:
                    summary = agent.get_session_summary(session_id)
                    print(summary)
                else:
                    print("尚未开始研究会话")
                continue
            elif not user_input:
                print("❌ 输入不能为空，请重新输入")
                continue
            
            # 启动研究
            print(f"\n🔍 正在为您研究: {user_input}")
            print("-" * 60)
            
            result = await agent.start_research(user_input)
            session_id = f"research_{len(agent.sessions)}"
            
            # 显示结果
            print("\n" + "=" * 70)
            print("📄 生成的研究报告:")
            print("=" * 70)
            print(result[:2000])  # 显示前2000字符
            print("=" * 70)
            
            # 提问是否继续优化
            print("\n💡 您想要:")
            print("  1. 基于当前结果继续深入研究")
            print("  2. 开始新的研究主题")
            print("  3. 查看详细报告文件")
            print("  4. 退出程序")
            
            choice = input("\n请选择 (1-4): ").strip()
            
            if choice == '1':
                await continue_research_session(agent, session_id)
            elif choice == '2':
                continue
            elif choice == '3':
                show_report_files()
            elif choice == '4':
                print("👋 感谢使用，再见！")
                break
            else:
                print("无效选择，返回主菜单")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，程序退出")
            break
        except Exception as e:
            print(f"❌ 处理过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()


async def continue_research_session(agent: PaperResearchAgent, session_id: str):
    """继续研究会话"""
    print("\n🔍 继续深入研究模式")
    print("您可以提供以下类型的反馈:")
    print("  • 我想要更多关于某个具体方向的内容")
    print("  • 请聚焦在特定的方法或应用")
    print("  • 添加一些相关的关键词")
    print("输入 'back' 返回主菜单")
    print()
    
    while True:
        feedback = input("💬 请输入您的反馈: ").strip()
        
        if feedback.lower() == 'back':
            break
        elif not feedback:
            print("❌ 反馈不能为空")
            continue
        
        try:
            print("\n🔄 正在根据您的反馈调整研究方向...")
            result = await agent.continue_research(session_id, feedback)
            
            print("\n" + "=" * 70)
            print("📄 更新后的研究报告:")
            print("=" * 70)
            print(result[:2000])
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ 处理反馈时出错: {str(e)}")


def print_help():
    """打印帮助信息"""
    help_text = """
📖 帮助信息

可用命令:
  help      - 显示此帮助信息
  status    - 查看当前研究会话状态
  quit/exit - 退出程序

使用指南:
  1. 提出您的研究问题
  2. Agent将自动进行文献检索和分析
  3. 可以基于结果提供反馈进行深入研究
  4. 生成的报告保存在 data/reports/ 目录

示例研究问题:
  • "最近一年关于大语言模型推理优化的研究"
  • "计算机视觉中的自注意力机制应用"
  • "图神经网络在推荐系统中的应用"
  • "对比学习在少样本学习中的最新进展"

反馈建议:
  • "我想了解更多关于具体实现细节"
  • "请增加一些工业界应用相关的论文"
  • "关注最新的实验结果和性能对比"
"""
    print(help_text)


def show_report_files():
    """显示报告文件"""
    reports_dir = "data/reports"
    
    if not os.path.exists(reports_dir):
        print("❌ 报告目录不存在")
        return
    
    files = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
    
    if not files:
        print("📭 暂无生成的报告文件")
        return
    
    print("\n📂 已生成的报告文件:")
    for i, file in enumerate(files, 1):
        file_path = os.path.join(reports_dir, file)
        size = os.path.getsize(file_path)
        print(f"  {i}. {file} ({size} bytes)")
    
    print("\n文件位置:", os.path.abspath(reports_dir))


async def research_mode(query: str):
    """单次研究模式"""
    agent = PaperResearchAgent()
    
    print(f"🔍 执行单次研究: {query}")
    print("-" * 60)
    
    result = await agent.start_research(query)
    
    print("\n" + "=" * 70)
    print("📄 研究报告:")
    print("=" * 70)
    print(result)
    print("=" * 70)
    
    print("\n✅ 研究完成！")
    print("📁 报告已保存到 data/reports/ 目录")


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        if sys.argv[1] == '--help':
            print("""
使用方法:
  python main.py              - 启动交互式模式
  python main.py "研究问题"     - 执行单次研究
  
选项:
  --help  - 显示帮助信息
            """)
            return
        else:
            # 执行单次研究
            query = sys.argv[1]
            asyncio.run(research_mode(query))
    else:
        # 交互式模式
        print_welcome()
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
