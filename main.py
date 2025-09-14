from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
# from langchain_groq import ChatGroq
from windows_use.agent import Agent
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    llm=ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite',temperature=0.2)
    # llm=ChatGroq(model='meta-llama/llama-4-maverick-17b-128e-instruct',api_key=os.getenv("GROQ_API_KEY"),temperature=0)
    agent = Agent(llm=llm,browser='chrome',use_vision=False,auto_minimize=True)
    query=input("Enter your query: ")
    agent.print_response(query)

if __name__ == "__main__":
    main()