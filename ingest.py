import os
import certifi
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# LangChain Imports
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch

# Load Credentials
load_dotenv()
uri = os.getenv("MONGODB_URI")
db_name = os.getenv("DB_NAME", "librarian_db")
collection_name = os.getenv("COLLECTION_NAME", "my_notes")

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
collection = client[db_name][collection_name]

def main():
    print("Starting the Ingestion Process...")

    # Load Documents from the 'data' folder
    # Using a DirectoryLoader that looks for .txt files for now
    print("Looking for files in the data/ folder...")
    loader = DirectoryLoader('./data', glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("Error: No text files found in the 'data' folder. Please add some!")
        return
        
    print(f"Found {len(documents)} document(s).")

    # Split the Text into Chunks
    # Prevents AI from being overwhelmed by massive files
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} searchable chunks.")

    # Initialize the Filing Clerk
    print("Initializing Ollama Embeddings (nomic-embed-text)...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Upload to MongoDB Atlas
    print("Uploading chunks and vectors to MongoDB Atlas...")
    
    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection=collection,
        index_name="vector_index"
    )
    
    print("Ingestion complete, notes are now in the database.")

if __name__ == "__main__":
    main()