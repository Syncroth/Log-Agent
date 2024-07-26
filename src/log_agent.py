#!/usr/bin/env python3

from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langgraph.checkpoint.sqlite import SqliteSaver

# Load the environment variables
_ = load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define the model and embeddings
model=ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key, verbose=True)
google_embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# load persistent vector store 
vectorstore = Chroma("logs_store", google_embeddings, persist_directory="./database/chroma_db")

# Tool definition
retriever = vectorstore.as_retriever()
log_tool = create_retriever_tool(
    retriever,
    "log_entry_search_tool",
    "Retrieve and provide detailed information about specific log entries."
)
memory = SqliteSaver.from_conn_string(":memory:")

# Agent definition
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    def __init__(self, model, tools, checkpointer, system=""):
        self.system = system
        graph=StateGraph(AgentState)
        graph.add_node("llm", self.call_model)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges("llm",
                                    self.exists_action,
                                    {True: "action", False: END})   
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph=graph.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}
        self.model= model.bind_tools(tools)

    def call_model(self, state: AgentState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message=self.model.invoke(messages)
        return {'messages':[message]}
    def exists_action(self, state: AgentState):
        result=state["messages"][-1]
        return len(result.tool_calls) > 0
    
    def take_action(self, state: AgentState):
        tool_calls=state["messages"][-1].tool_calls
        results=[]
        for t in tool_calls:
            print(f"calling tool : {t}")
            result = self.tools[t['name']].invoke(t["args"])
            results.append(ToolMessage(tool_call_id=t['id'],name=t['name'], content=str(result)))
        print("Back to the model")
        return {'messages':results}
    
# Load the system prompt
script_dir = os.path.dirname(os.path.abspath(__file__))
system_prompt_path = os.path.abspath(os.path.join(script_dir,"..", "prompts/system_prompt.txt"))

with open(system_prompt_path,"r") as f:
    system_message = f.read()

# Create the agent
tools = [log_tool]
abot = Agent(model, tools, memory, system_message)

# test the agent
if __name__ == "__main__":
    user_message= "Hi there! I've been noticing some irregularities in our network performance. Can you analyze the recent log entries and provide insights into any potential issues with our applications, specifically focusing on connection stability and data transfer efficiency? Thanks!"
    messages = [HumanMessage(content=user_message)]

    result= abot.graph.invoke({"messages":messages },
                        config = {"configurable":{"thread_id": "1"}})

    print(result['messages'][-1].content)