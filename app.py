from utils import *
import uuid
import gradio as gr
import gradio as gr
import uuid
from langchain_community.llms import HuggingFaceHub
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['HUGGINGFACEHUB_API_TOKEN']

hf=HuggingFaceHub(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", #meta-llama/Llama-3.1-8B-Instruct
    model_kwargs={"temperature":0.3}

)

session_id = str(uuid.uuid4())
# Gradio chat interface
def respond(message, history, session_state):
    # Extract session_id from session_state
    session_id = session_state.get("session_id", None)
    
    # If no session_id, create a new one
    if not session_id:
        session_id = str(uuid.uuid4())
        session_state["session_id"] = session_id
    
    # Process the query
    response = query_with_memory(message, hf, session_id)
    
    return response

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Zomato Restaurant Menu Assistant")
    gr.Markdown("Ask questions about restaurant menus, items, and prices.")
    
    # Create a session state
    session_state = gr.State({"session_id": None})
    
    # Create the chatbot interface
    chatbot = gr.Chatbot(height=100)
    msg = gr.Textbox(label="Your Question", placeholder="Ask about restaurant menus...")
    
    # Clear button
    clear = gr.Button("Clear Conversation")
    
    # Define the function that updates the chat
    def user_input(message, chat_history, session_state):
        bot_message = respond(message, chat_history, session_state)
        chat_history.append((message, bot_message))
        return "", chat_history
    
    # Function to clear conversation and start new session
    def clear_conversation(session_state):
        session_state["session_id"] = str(uuid.uuid4())
        return [], session_state
    
    # Link buttons to functions
    msg.submit(user_input, [msg, chatbot, session_state], [msg, chatbot])
    clear.click(clear_conversation, [session_state], [chatbot, session_state])

# Launch the interface
if __name__ == "__main__":
    demo.launch(debug=True)