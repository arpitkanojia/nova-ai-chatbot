import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai

# API key load karo: pehle .env se (local), phir Streamlit Secrets se (cloud)
load_dotenv(Path(__file__).resolve().parent / ".env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

st.set_page_config(
    page_title="Nova AI Chat",
    page_icon="🤖",
    layout="centered"
)

# Custom styling
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #10131f, #171b2e);
    color: #f5f7ff;
}
header[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}
h1 {
    color: #a9b8ff;
}
div[data-testid="stChatMessage"] {
    border: 1px solid #343952;
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 12px;
}
div[data-testid="stChatInput"] {
    border-color: #6978bc;
}
</style>
""", unsafe_allow_html=True)

if not api_key:
    st.error("API key nahi mili. Streamlit Secrets ya .env file check karo.")
    st.stop()

client = genai.Client(api_key=api_key)

# Conversation state
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

# Sidebar
with st.sidebar:
    st.title("🤖 Nova AI")
    st.caption("Your personal AI assistant")

    if st.button("＋ New Chat", use_container_width=True):
        name = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[name] = []
        st.session_state.active_chat = name
        st.rerun()

    st.divider()
    st.subheader("Your conversations")

    for name in list(st.session_state.chats.keys()):
        if st.button(
            f"💬 {name}",
            key=f"select_{name}",
            use_container_width=True
        ):
            st.session_state.active_chat = name
            st.rerun()

    st.divider()
    st.caption("Built with Streamlit + Gemini")

# Current chat
chat_name = st.session_state.active_chat
messages = st.session_state.chats[chat_name]

st.title("✨ Nova AI")
st.caption("Ask anything. Let's figure it out together.")

# Show conversation
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
prompt = st.chat_input("Message Nova AI...")

if prompt:
    messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        {
            "role": "user" if m["role"] == "user" else "model",
            "parts": [{"text": m["content"]}]
        }
        for m in messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Nova is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=history
                )
                answer = response.text or "No text response received."
                st.markdown(answer)
                messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Gemini error: {e}")
                messages.pop()
