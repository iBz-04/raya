from langchain_openai import ChatOpenAI
from windows_use.agent import Agent
from dotenv import load_dotenv
import os

# Load .env or .env.local (whichever exists)
load_dotenv()  # .env
load_dotenv(".env.local", override=False)

def main():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    agent = Agent(llm=llm,browser='chrome',use_vision=False,auto_minimize=True)
    query=input("Enter your query: ")
    agent.print_response(query)

if __name__ == "__main__":
    main()