# app.py
import streamlit as st
import os
from LLM.llm import GenerativeAI

# Page configuration
st.set_page_config(
    page_title="🌿 TNC Conservation Assistant", 
    page_icon="🌿",
    layout="wide"
)

# Sidebar with TNC branding and tools
with st.sidebar:
    st.image("tnc_logo.png", width=250)
    st.title("Conservation Assistant")
    st.markdown("---")
    
    st.subheader("Available Tools")
    st.markdown("""
    - 🔍 **Knowledge Base Search**: Access TNC's conservation research and initiatives
    - 📰 **News Search**: Find latest TNC news by keyword
    - 🗓️ **Event Search**: Discover TNC events by region and topic
    - 🌐 **Web Resources**: Access TNC's website sections
    - 📱 **Social Media**: Connect with TNC's social accounts
    - 🔗 **Web Browsing**: Visit relevant conservation websites
    """)
    
    st.markdown("---")
    st.caption("© The Nature Conservancy")

# Main chat interface
st.title("🌿 TNC Conservation Assistant")
st.caption("Ask me about conservation projects, events, or how to get involved with The Nature Conservancy")

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome to The Nature Conservancy's Conservation Assistant! How can I help you with conservation topics today?"}]

# Initialize GenerativeAI instance
try:
    generative_ai = GenerativeAI()
except ValueError as e:
    generative_ai = None
    st.error(f"Error initializing conservation assistant: {str(e)}")

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Process new user input
if prompt := st.chat_input("Ask about conservation topics..."):
    if generative_ai:
        # Add user message to chat UI
        st.chat_message("user").write(prompt)
        
        # Process message and get response
        with st.spinner("Researching conservation information..."):
            response = generative_ai.process_message_and_get_response(prompt, st.session_state)
        
        # Display assistant response
        st.chat_message("assistant").write(response)