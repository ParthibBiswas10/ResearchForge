from agents import search_agent, scrap_agent, writer_chain, critic_chain

def run_pipeline(topic:str)->dict:
    state{}

    print("\n"+" ="*50)
    print("search agent is cooking...")
    print("="*50)

    agent1=search_agent()
    searchResult=agent1.invoke({
        "messages":[("user",f"Find recent, reliable and detailed information about: {topic}")]
    })
    
    state["search_results"]=searchResult['messages'][-1].content

    print("\n search result ",state['search_results'])

    print("\n"+" ="*50)
    print("scrap agent is cooking...")
    print("="*50)

    agent2=scrap_agent()
    scrapped=agent2.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scrapped_result']=scraped['messages'][-1].content

    print("\nscrapped content: \n",state['scrapped_result'])


#writer chain

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

research_result=(
    f"search resuls: \n {state['search_results']} \n\n"

    f"Scrapped content: \n {state['scrapped_result']}"
)

state["report"]=writer_chain.invoke({
    "topic": topic,
    "research": research_result
})

print("\n Final Report\n",state['report'])


#critic chain
print("\n"+" ="*50)
print("step 4 - critic is reviewing the report ")
print("="*50)

state["feedback"]=critic_chain.invoke({
    "report":state[report]
})

print("\n critic report \n", state['feedback'])
return state

if _name_=="_main_":
    topic=input("\n Enter a Research topic: ")
    run_pipeline(topic)

