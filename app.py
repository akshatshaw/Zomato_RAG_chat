from utils import *
import uuid
import gradio as gr
import os
from langchain_community.llms import HuggingFaceHub
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

# Define the function that updates the chat
def user_input(message, chat_history, session_state):
    if message.strip() == "":
        return "", chat_history
    bot_message = respond(message, chat_history, session_state)
    chat_history.append((message, bot_message))
    return "", chat_history

# Function to clear conversation and start new session
def clear_conversation(session_state):
    return [], session_state

# Function to start a new session
def new_conversation(session_state):
    session_state["session_id"] = str(uuid.uuid4())
    return [], session_state

# Function to handle example questions
def use_example(example, chat_history, session_state):
    bot_message = respond(example, chat_history, session_state)
    chat_history.append((example, bot_message))
    return chat_history


# Example questions to help users get started
example_questions = [
    "What are the popular dishes at Spice Garden?",
    "What vegetarian options does Pizza Palace offer?",
    "How much is the Chicken Biryani at Taj Restaurant?",
    "Which restaurant has the best desserts?",
    "Compare prices of burgers across different restaurants"
]

# Create the Gradio interface with a custom theme
with gr.Blocks(theme=gr.themes.Soft(primary_hue="orange", secondary_hue="orange")) as demo:
    with gr.Row():
        gr.HTML("""
            <div style="text-align: center; margin-bottom: 1rem">
                <h1 style="margin-bottom: 0.5rem">Zomato Restaurant Menu Assistant</h1>
                <p style="margin: 0; font-size: 1.1rem; color: #666">Your AI guide to restaurant menus, dishes, and prices</p>
            </div>
        """)
    
    # Create a session state
    session_state = gr.State({"session_id": None})
    
    with gr.Row():
        with gr.Column(scale=7):
            # Create the chatbot interface with improved styling (removed bubble_full_width)
            chatbot = gr.Chatbot(
                height=500,
                show_label=False,
                avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"),
                container=True,
                elem_id="chatbot"
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Type your question about restaurant menus...",
                    scale=9,
                    container=False,
                    show_label=False,
                    elem_id="msg-textbox"
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Row():
                clear = gr.Button("Clear Conversation", variant="secondary")
                new_session = gr.Button("New Session", variant="secondary")
        
        with gr.Column(scale=3):
            gr.HTML("""
                <div style="border-radius: 8px; border: 1px solid #ddd; padding: 15px; height: 100%;">
                    <h3 style="margin-top: 0;">How to use this assistant</h3>
                    <p>Ask questions about restaurant menus, dishes, prices, and recommendations.</p>
                    <p>The assistant remembers your conversation context, so you can ask follow-up questions.</p>
                    <p>Click "New Session" to start a fresh conversation with a new context.</p>
                </div>
            """)
            
            with gr.Accordion("Example Questions", open=True):
                # Fix: Create example buttons properly
                for question in example_questions:
                    btn = gr.Button(question, size="sm")
                    # Connect each button directly here
                    btn.click(
                        fn=use_example,
                        inputs=[gr.Textbox(value=question, visible=False), chatbot, session_state],
                        outputs=[chatbot]
                    )
    
    # Add footer
    gr.HTML("""
        <div style="text-align: center; margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 0.9rem;">Powered by AI - Get restaurant information instantly</p>
        </div>
    """)
    
    
    
    # Link buttons to functions
    msg.submit(user_input, [msg, chatbot, session_state], [msg, chatbot])
    submit_btn.click(user_input, [msg, chatbot, session_state], [msg, chatbot])
    clear.click(clear_conversation, [session_state], [chatbot, session_state])
    new_session.click(new_conversation, [session_state], [chatbot, session_state])
    
    # Link example buttons
    # Remove the problematic loop since we're handling button clicks above
    # for i, btn in enumerate(example_btns):
    #     btn.click(
    #         use_example, 
    #         [example_questions[i], chatbot, session_state], 
    #         [chatbot]
    #     )

# Add custom CSS for better styling
css = """
#chatbot {
    border-radius: 10px;
    border: 1px solid #ddd;
}
#msg-textbox {
    border-radius: 8px;
}
"""

# Launch the interface
if __name__ == "__main__":
    demo.launch(debug=True)