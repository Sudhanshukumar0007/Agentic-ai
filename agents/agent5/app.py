import streamlit as st
import os
import asyncio
import requests
import xml.etree.ElementTree as ET
import edge_tts
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# st.set_page_config(page_title="Medical Information AI", layout="centered")
st.title("🩺 Voice Medical Information Assistant")

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    st.warning("Please set OPENROUTER_API_KEY in your .env file.")
    st.stop()

@tool
def medical_information(topic: str) -> str:
    """
    Search MedlinePlus for general medical information about a topic.
    Provides educational information only and does not diagnose or prescribe.
    """
    url = "https://wsearch.nlm.nih.gov/ws/query"
    params = {
        "db": "healthTopics",
        "term": topic,
        "retmax": 3,
        "rettype": "brief"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        results = []
        
        for document in root.findall(".//document"):
            title = ""
            summary = ""
            page_url = document.attrib.get("url", "")
            for content in document.findall("content"):
                name = content.attrib.get("name")
                text = "".join(content.itertext()).strip()
                if name == "title":
                    title = text
                elif name == "full-summary":
                    summary = text
            if title or summary:
                results.append({"title": title, "summary": summary, "url": page_url})
                
        if not results:
            return f"No medical information found for: {topic}"
            
        output = f"Medical information from MedlinePlus for '{topic}':\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['title']}\n{result['summary']}\nSource: {result['url']}\n\n"
            
        output += "Important: This information is for educational purposes only. It does not provide a diagnosis or medical prescription."
        return output
    except requests.RequestException as e:
        return f"Unable to access MedlinePlus: {str(e)}"
    except ET.ParseError:
        return "Unable to process the medical information returned by MedlinePlus."

@st.cache_resource
def init_agent():
    llm = ChatOpenRouter(
        model="openrouter/auto",
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
        temperature=0
    )
    tools = [medical_information]
    
    system_prompt = """
    You are a medical information voice assistant.
    Your job is to provide general educational medical information.

    Important rules:
    - Do not diagnose diseases.
    - Do not prescribe medicines.
    - Do not replace a healthcare professional.
    - Use information retrieved from the medical information tool.
    - Since your response will be spoken aloud, keep the answer concise.
    - Use simple language.
    - Do not use Markdown.
    - Avoid long lists.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

agent_executor = init_agent()

async def generate_voice(text, filename="medical_response.mp3"):
    voice = "en-IN-NeerjaNeural"
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(filename)

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"])

if prompt := st.chat_input("Ask a medical question:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            chat_history = []
            for msg in st.session_state.messages[:-1]:
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    chat_history.append(AIMessage(content=msg["content"]))
                    
            response = agent_executor.invoke({
                "input": prompt,
                "chat_history": chat_history
            })
            
            reply = response["output"]
            st.markdown(reply)
            
            audio_file = "medical_response.mp3"
            asyncio.run(generate_voice(reply, audio_file))
            
            st.audio(audio_file)
            
            # Save audio as bytes to session state so it can be replayed on reload
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
                
            st.session_state.messages.append({
                "role": "assistant", 
                "content": reply,
                "audio": audio_bytes
            })
