from langchain_openai import ChatOpenAI
from windows_use.agent import Agent
from dotenv import load_dotenv
import os

# Load .env or .env.local (whichever exists)
load_dotenv()  # .env
load_dotenv(".env.local", override=False)

def main():
    llm = ChatOpenAI(
        model="gpt-4o",  
        temperature=0.1, 
        max_tokens=3000, 
        timeout=30, 
        max_retries=2  
    )
    
    # Optimize agent settings for performance
    agent = Agent(
        llm=llm,
        browser='chrome',
        use_vision=False, 
        auto_minimize=True,
        max_steps=10,  
        consecutive_failures=2  
    )
    
    query = input("Enter your query: ")
    agent.print_response(query)

if __name__ == "__main__":
    main()
    main()