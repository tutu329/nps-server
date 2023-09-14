from duckduckgo_search import ddg
import json
import sys
import os

def google_search(keywords: str, num_results: int = 8, time="m") -> str:
    search_results = []
    if not keywords:
        return json.dumps(search_results)

    results = ddg(
        keywords,
        max_results=num_results,
        region="us-en",
        safesearch="off",
        time=time,   # d w m y，即一天内、一周内、一月内、一年内
        )
    if not results:
        return json.dumps(search_results)

    for j in results:
        search_results.append(j)

    # results = json.dumps(search_results, ensure_ascii=False, indent=4)
    return search_results

def console_test():
    from langchain.utilities import GoogleSerperAPIWrapper
    from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
    from langchain.agents import initialize_agent, Tool

    from langchain.agents import load_tools
    from langchain.agents import initialize_agent
    from langchain.llms import OpenAI
    from langchain.agents import AgentType
    os.environ["OPENAI_API_KEY"] = "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"
    os.environ["SERPER_API_KEY"] = "c9cc9a277edd18c01d4d6c125ac2fb6b725c7e555298e03644ef906d32d46426"

    # 加载 OpenAI 模型
    llm = OpenAI(temperature=0, max_tokens=2048)
    llm.model_name = "gpt-3.5-turbo-0301"

    # 加载 serpapi 工具
    search = DuckDuckGoSearchAPIWrapper()
    # search.k=10
    # search.time='d'
    # search.region='us-en'
    # search.safesearch='off'
    # search.max_results=20
    tools = [
        Tool(
            name="Intermediate Answer",
            func=search.run,
            description="useful for when you need to ask with search"
        )
    ]

    # tools = load_tools(["serpapi", "Intermediate Answer"])

    # 如果搜索完想在计算一下可以这么写
    # tools = load_tools(['serpapi', 'llm-math'])

    # 如果搜索完想再让他再用python的print做点简单的计算，可以这样写
    # tools=load_tools(["serpapi","python_repl"])

    # 工具加载后都需要初始化，verbose 参数为 True，会打印全部的执行详情
    agent = initialize_agent(tools, llm, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True)

    # 运行 agent
    # agent.run("What's the date today?")
    # agent.run("今天twitter上的热门趋势有哪些?")
    # agent.run("今天是几号?")
    agent.run("刘德华今年几岁?")
    # agent.run("What's the date today? What great events have taken place today in history?")


def main():
    console_test()

def main0():
    arg = sys.argv
    print(arg)
    if len(arg)>=4:
        print(google_search(arg[1], int(arg[2]), arg[3]))
    else:
        print("arg1: search content, arg2: results num, arg3: time.")

if __name__ == "__main__":
    main()