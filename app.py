# app.py
import streamlit as st
import os
from LLM.llm import GenerativeAI

# Page configuration
st.set_page_config(page_title="💬 Chatbot", page_icon="💬")

# Sidebar for API key
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Initialize GenerativeAI instance
try:
    generative_ai = GenerativeAI()
except ValueError as e:
    generative_ai = None
    if "API key" in str(e) and not openai_api_key:
        pass  # Don't show error if we already showed warning about API key
    else:
        st.error(f"Error initializing AI: {str(e)}")

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Process new user input
if prompt := st.chat_input():
    if generative_ai:
        # Add user message to chat UI
        st.chat_message("user").write(prompt)
        
        # Process message and get response
        with st.spinner("Thinking..."):
            response = generative_ai.process_message_and_get_response(prompt, st.session_state)
        
        # Display assistant response
        st.chat_message("assistant").write(response)