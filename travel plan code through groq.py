# Install required packages
# pip install gradio langchain-openai langchain google-search-results python-dotenv

import os
from typing import List, Dict
from langchain_community.tools import GoogleSearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
import gradio as gr

# Initialize components
search = GoogleSearchResults(api_key=os.getenv("SERPAPI_KEY"))
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# System Prompts
INITIAL_PROMPT = """You are a professional travel planner AI. Your task is to:
1. Collect essential information through natural conversation:
- Travel dates (exact or approximate)
- Starting location
- Destination(s)
- Budget range (per person or total)
- Travel purpose (leisure, business, etc.)
- Special preferences (food, mobility, interests)

2. Identify missing information and politely ask for clarifications

3. Use Google Search tool to find:
- Current attractions/events
- Local hidden gems matching preferences
- Transportation options
- Verified accommodations within budget

4. Generate final itinerary with:
- Logical daily structure
- Realistic timing
- Budget allocations
- Personalized recommendations"""

ITINERARY_PROMPT = """Generate a {days}-day itinerary for {user_name} traveling from {origin} to {destination} from {start_date} to {end_date}.

Budget: {budget}
Preferences: {preferences}

Include these verified points:
{search_results}

Format:
- Day 1:
  - Morning: [Activity] ([Budget Estimate])
  - Afternoon: [Activity] ([Budget Estimate])
  - Evening: [Activity] ([Budget Estimate])
  - Hidden Gem: [Recommendation]
- Accommodation Suggestion
- Daily Budget Summary"""

# Agent Tools
tools = [search]
prompt = ChatPromptTemplate.from_messages([
    ("system", INITIAL_PROMPT),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

def process_conversation(message: str, history: List[List[str]]):
    response = agent_executor.invoke({"input": message})
    
    if "itinerary" in message.lower() and all(key in memory.chat_memory.messages[-1].content for key in ["origin", "destination", "start_date"]):
        # Extract collected parameters
        params = {
            "user_name": "John Doe",  # Could be extracted from history
            "origin": memory.load_memory_variables({}).get("origin", ""),
            "destination": memory.load_memory_variables({}).get("destination", ""),
            "start_date": memory.load_memory_variables({}).get("start_date", ""),
            "end_date": memory.load_memory_variables({}).get("end_date", ""),
            "budget": memory.load_memory_variables({}).get("budget", ""),
            "preferences": memory.load_memory_variables({}).get("preferences", ""),
            "search_results": memory.load_memory_variables({}).get("search_results", ""),
            "days": 5  # Calculate from dates
        }
        
        itinerary = llm.invoke(ITINERARY_PROMPT.format(**params))
        return itinerary.content
    
    return response["output"]

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# AI Travel Planner ✈️")
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(label="Your Message")
    clear = gr.Button("Clear")

    def respond(message, chat_history):
        bot_message = process_conversation(message, chat_history)
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
