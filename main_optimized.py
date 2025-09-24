from langchain_openai import ChatOpenAI
from raya.agent import Agent
from dotenv import load_dotenv


load_dotenv()
load_dotenv(".env.local", override=False)

def main():
    print("Choose model configuration:")
    print("1. GPT-4o (recommended for best performance)")
    print("2. GPT-4o-mini (budget option, slower)")
    print("3. GPT-4-turbo (balanced option)")
    
    choice = input("Enter choice (1-3) or press Enter for default: ").strip()
    
    if choice == "1":
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            max_tokens=2000,
            timeout=30,
            max_retries=2
        )
        print("Using GPT-4o for optimal performance")
    elif choice == "3":
        llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.1,
            max_tokens=2000,
            timeout=30,
            max_retries=2
        )
        print("Using GPT-4-turbo for balanced performance")
    else:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=1500,
            timeout=20,
            max_retries=1
        )
        print("Using GPT-4o-mini (budget option)")
    
    agent = Agent(
        llm=llm,
        browser='chrome',
        use_vision=False,  
        auto_minimize=True,
        max_steps=8, 
        consecutive_failures=2  
    )
    
  
    
    query = input("\nEnter your query: ")
    agent.print_response(query)

if __name__ == "__main__":
    main()