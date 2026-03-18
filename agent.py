import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Annotated, TypedDict

# LangChain & LangGraph Imports
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Web imports
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Import CORS
from fastapi.middleware.cors import CORSMiddleware

# Setup & Connection
load_dotenv()
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
collection = client[os.getenv("DB_NAME")][os.getenv("COLLECTION_NAME")]

model_choice = os.getenv("MODEL_TYPE", "local").lower()

if (model_choice == "cloud"):
    print("Using gpt-4o-mini")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # temperature 0 keeps it factual
else:
    print("Using llama3.2")
    llm = ChatOllama(model="llama3.2", temperature=0)

# Initialize Models
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Setup Retriever
vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,
    index_name="vector_index"
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Define State
class AgentState(TypedDict):
    
    messages: Annotated[list, add_messages]
    
    # This will hold the raw text to pull from MongoDB
    context: str

# Define nodes
def retrieve_node(state: AgentState):
    print("Fetching notes from MongoDB...")
    
    recent_message = state["messages"][-1].content
    docs = retriever.invoke(recent_message)
    
    # Debugging via x-ray specs for the api
    print(f"\n[Debug] MongoDB found {len(docs)} notes for the query: '{recent_message}'")
    if len(docs) > 0:
        print(f"[Debug] Top Note: {docs[0].page_content}\n")
    
    found_text = "\n\n".join(doc.page_content for doc in docs)
    return {"context": found_text}


def generate_node(state: AgentState):
    print("Llama 3.2 is reading the history and notes...")
    
    # Grab user's question
    user_question = state["messages"][-1].content
    
    # Make the prompt Llama 3.2
    enforced_prompt = f"""You are a precise Personal Librarian. 

    DOCUMENTS FOUND IN DATABASE:
    {state['context']}

    USER QUESTION: 
    {user_question}

    INSTRUCTIONS:
    1. Answer the question using ONLY the documents provided above.
    2. If the documents mention multiple topics, do NOT combine them unless they are explicitly related.
    3. If the answer is not in the documents, say "I don't know."
    4. Do not mention taxes if the user is asking about meetings, and vice versa.
    """
    
    # Use HumanMessage() instead of the Tuple
    new_message = HumanMessage(content=enforced_prompt)
    messages_to_send = state["messages"][:-1] + [new_message]
    
    # Hand the clean package to Llama 3.2
    response = llm.invoke(messages_to_send)
    
    return {"messages": [response]}


# Build the Graph
# Initialize graph with the State
workflow = StateGraph(AgentState)

# Add the spaces to the board
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

# Connect spaces
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile the graph with a Memory checkpointer
# This actively saves chat history between terminal inputs.
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# FastAPI Web Server

# Define what the incoming request from future frontend will look like
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "1"

# Initialize the API
api = FastAPI(title="My Librarian API")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the Endpoint
@api.post("/chat")
def chat_endpoint(request: ChatRequest):
    print(f"\nReceived request from web: {request.message}")
    
    # Package the frontend's text for LangGraph
    input_message = {"messages": [("user", request.message)]}
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Run the graph
    output_state = app.invoke(input_message, config)
    
    # Extract the AI's final answer
    ai_response = output_state["messages"][-1].content
    print(f"Sending response back to web.")
    
    # Return it as a clean JSON package
    return {"response": ai_response}

# Start the Server
if __name__ == "__main__":
    print("\nStarting local API server...")
    uvicorn.run(api, host="0.0.0.0", port=8000)
