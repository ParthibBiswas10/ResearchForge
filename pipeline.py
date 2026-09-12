from agents import search_agent, scrap_agent, writer_agent, critic_agent

def run_pipeline(topic:str)->dict:
    state{}

    print("\n"+" ="*50)
    print("search agent is cooking...")
    print("="*50)

    agent=search_agent()
    searchResult=agent.invoke({
        "messages":[("user",f"Find recent, reliable and detailed information about: {topic}")]
    })
    
    state["search_results"]=searchResult['messages'][-1].content

    print("\n search result ",state['search_results'])