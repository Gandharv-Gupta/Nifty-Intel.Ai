import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain.agents import create_agent
from system_prompts import nifty_agent_prompt
from Tools.market_data_tool import get_market_data
from Tools.option_chain_tool import get_option_chain
from Tools.top_gainers_losers_tool import get_top_movers
from Tools.analytics_tool import analyze_market

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")



model = init_chat_model(
    f"openai:{openai_model}",
    api_key=openai_api_key
)


# Define model, tools, and system prompt to build the agent
nifty_agent = create_agent(
    model=model,
    tools=[get_market_data, get_option_chain, get_top_movers, analyze_market],
    system_prompt=nifty_agent_prompt,
)


if __name__ == "__main__":
    inputs = {
        "messages": [
            {"role": "user", "content": "Analyse the data of top performers in the market"},
        ]
    }
    for chunk in nifty_agent.stream(inputs, stream_mode="updates"):
        print(chunk)