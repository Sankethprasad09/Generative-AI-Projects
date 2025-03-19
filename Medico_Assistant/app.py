# Author : Sanketh Karuturi 

import streamlit as st
from langchain.prompts import PromptTemplate
import requests
import warnings

# Suppress unnecessary warnings
warnings.filterwarnings("ignore")

def health_chatbot(user_messages):
    """Function to interact with NVIDIA's chatbot API for health-related queries."""
    api_endpoint = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/8f4118ba-60a8-4e6b-8574-e38a4067a4a3"
    status_url_base = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/status/"
    
    headers = {
        "Authorization": "Bearer YOUR_API_KEY_HERE",
        "Accept": "application/json",
    }
    
    payload = {
        "messages": user_messages,
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024,
        "seed": 42,
        "stream": False
    }
    
    session = requests.Session()
    response = session.post(api_endpoint, headers=headers, json=payload)
    
    while response.status_code == 202:
        request_id = response.headers.get("NVCF-REQID")
        status_url = status_url_base + request_id
        response = session.get(status_url, headers=headers)
    
    response.raise_for_status()
    return response.json()['choices'][0]['message']

# Template for AI system's behavior as a virtual doctor
ai_system_message = """You are a compassionate doctor providing expert health guidance. 
Ensure to create a {detail} nutrition plan and offer valuable medical advice to users. 
Maintain an optimistic tone, encouraging patients regarding their well-being. 
Additionally, {medication} recommend medication when necessary for health improvement. 
As a doctor, do not answer non-medical questions."""

system_prompt = PromptTemplate(
    input_variables=['detail', 'medication'],
    template=ai_system_message
)

# Configure Streamlit interface
st.set_page_config(page_title="Health Assistant", page_icon=":robot:")
st.header("👋 Welcome! I'm your Health Assistant.")

# Session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            'content': system_prompt.format(detail='comprehensive', medication='provide'),
            'role': 'system'
        }
    ]

def fetch_response(query):
    """Process user queries and fetch AI-generated responses."""
    user_input_message = {'content': query, 'role': 'user'}
    st.session_state.chat_history.append(user_input_message)
    assistant_response = health_chatbot(st.session_state.chat_history)
    st.session_state.chat_history.append(assistant_response)
    return assistant_response

def get_user_input():
    """Capture user input from text box."""
    return st.text_input("You: ", key="user_input")

user_message = get_user_input()
submit_button = st.button("Get Advice")

if submit_button and user_message:
    with st.spinner("Generating a response..."):
        response = fetch_response(user_message)

# Display conversation history
for index, chat in enumerate(st.session_state.chat_history):
    if index < 2:
        continue
    if chat['role'] == 'user':
        st.markdown(f'<span style="color:green">**You:**</span> \n\n{chat["content"]}', unsafe_allow_html=True)
    else:
        st.markdown(f'<span style="color:#ffd700">**Assistant:**</span> \n\n{chat["content"]}', unsafe_allow_html=True)
