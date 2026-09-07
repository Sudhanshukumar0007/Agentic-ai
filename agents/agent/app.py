import streamlit as st
import os
from pathlib import Path
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool

# st.set_page_config(page_title="Hospital Assistant Agent", layout="centered")

st.title("🏥 Hospital AI Assistant")
st.write("An agent capable of answering questions from the hospital knowledge base.")

@st.cache_resource
def init_agent():
    # Load and process PDF
    pdf_path = os.path.join(os.path.dirname(__file__), '..', 'Viva Questions with Answers.pdf')
    
    if not os.path.exists(pdf_path):
        st.error(f"Could not find PDF file at {pdf_path}")
        return None
        
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    @tool
    def search_hospital(query: str) -> str:
        """Search hospital documents."""
        results = retriever.invoke(query)
        return "\n".join(doc.page_content for doc in results)
        
    system_prompt = SystemMessage(
        content=\"\"\"
You are an AI Hospital Assistant.
Answer using the hospital knowledge base.
Do not diagnose or recommend medical treatment.
If the answer is not found, say you don't know.
\"\"\"
    )
    
    memory = InMemorySaver()
    
    agent = create_agent(
        model="ollama:llama3.2:3b",
        tools=[search_hospital],
        system_prompt=system_prompt,
        checkpointer=memory
    )
    return agent

agent = init_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What are patient safety rights?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    if agent:
        with st.chat_message("assistant"):
            config = {"configurable": {"thread_id": "patient-001"}}
            response = agent.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config=config
            )
            reply = response["messages"][-1].content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
