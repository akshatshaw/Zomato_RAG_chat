from langchain.memory import MongoDBChatMessageHistory, ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient
from langchain.schema import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
load_dotenv()
uri = os.getenv("MONGODB_URI")
os.environ['HUGGINGFACEHUB_API_TOKEN']

# MongoDB connection settings
mongo_connection_string = uri 
mongo_db_name = "chat_histories"
mongo_collection_name = "chat_db"

from sentence_transformers import SentenceTransformer
# Load the embedding model (https://huggingface.co/nomic-ai/nomic-embed-text-v1")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

def get_embedding(data):
    """Generates vector embeddings for the given data."""
    embedding = model.encode(data)
    return embedding.tolist()

# function to run vector search queries
def get_query_results(query):
    """Gets results from a vector search query."""
    client = MongoClient(uri)
    collection = client["rag_db"]["test"]
    query_embedding = get_embedding(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "exact": True,
                "limit": 10
            }
        }, {
            "$project": {
                "_id": 0,
                "text": 1
            }
        }
    ]

    results = collection.aggregate(pipeline)

    array_of_results = []
    for doc in results:
        array_of_results.append(doc)
    return array_of_results

def query_with_memory(query, llm, session_id="default_session"):
    """Process a query using conversation memory and MongoDB vector search"""
    # Initialize MongoDB chat history for the session
    message_history = MongoDBChatMessageHistory(
        connection_string=mongo_connection_string,
        database_name=mongo_db_name,
        collection_name=mongo_collection_name,
        session_id=session_id
    )
    
    # Create memory from the message history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        return_messages=True,
    )
    
    # Retrieve chat history
    chat_history = memory.load_memory_variables({}).get("chat_history", [])
    
    # Create the question rephrasing prompt
    rephrase_template = """Given the following conversation and a follow up question, 
    rephrase the follow up question to be a standalone question that includes relevant context.

    Chat History:
    {chat_history}
    
    Follow Up Input: {question}
    
    Standalone Question: 
    
    Answer:
    """
    
    rephrase_prompt = PromptTemplate(
        input_variables=["chat_history", "question"],
        template=rephrase_template
    )
    
    # Create the rephrasing chain
    rephrase_chain = LLMChain(
        llm=llm,
        prompt=rephrase_prompt,
        verbose=False
    )
    
    # If there's chat history, rephrase the question for context
    formatted_history = ""
    if chat_history:
        # Format the chat history for the prompt
        for message in chat_history:
            if isinstance(message, HumanMessage):
                formatted_history += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                formatted_history += f"AI: {message.content}\n"
        
        # Rephrase the query with context
        rephrased_query = rephrase_chain.run(
            question=query,
            chat_history=formatted_history
        )
    else:
        rephrased_query = query
    
    print(f"Original query: {query}")
    print(f"Rephrased query: {rephrased_query}")
    
    # Get search results using the rephrased query
    search_results = get_query_results(rephrased_query)
    
    # Extract text from search results
    context = "\n\n".join([doc["text"] for doc in search_results])
    
    # QA prompt template
    qa_template = """You are a helpful assistant for restaurant menu related questions.
    Use the following context to answer the question. If you don't know the answer, 
    just say "I don't know", don't try to make up an answer.
    
    Context: {context}
    
    Question: {question}
    
    Answer:"""
    
    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=qa_template
    )
    
    # Create and run the QA chain
    qa_chain = LLMChain(llm=llm, prompt=qa_prompt)
    answer = qa_chain.run(context=context, question=rephrased_query)
    
    # Save the interaction to memory
    memory.save_context({"input": query}, {"output": answer})
    
    return answer