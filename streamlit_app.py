import streamlit as st
import requests

st.title("🤖 AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    response = requests.post(
        "YOUR_BACKEND_API_URL/chat",
        json={"message": prompt}
    )

    answer = response.json()["response"]

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()