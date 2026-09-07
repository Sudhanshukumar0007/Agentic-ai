import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.prompts import PromptTemplate

# st.set_page_config(page_title="Organizational Info RAG Agent", layout="centered")
st.title("📂 Enterprise Knowledge RAG Agent")
st.write("Retrieve organizational information from enterprise documents.")

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    st.warning("Please set OPENROUTER_API_KEY in your .env file.")
    st.stop()

client = OpenAI(
    api_key=openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)

class OpenRouterEmbeddings(Embeddings):
    def embed_documents(self, texts):
        response = client.embeddings.create(
            model="liquid/lfm-2.5-embedding-350m:free",
            input=texts
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text):
        response = client.embeddings.create(
            model="liquid/lfm-2.5-embedding-350m:free",
            input=text
        )
        return response.data[0].embedding

@st.cache_resource
def init_system():
    pdf_path = os.path.join(os.path.dirname(__file__), '..', 'financial_policy_guidelines_and_example.pdf')
    if not os.path.exists(pdf_path):
        st.error(f"Could not find PDF file at {pdf_path}")
        return None, None
        
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = OpenRouterEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", # the original notebook used this
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    return retriever, llm

retriever, llm = init_system()

query = st.text_input("Ask a question about the financial policy:")

if st.button("Search"):
    if query and retriever and llm:
        with st.spinner("Searching and generating answer..."):
            docs = retriever.invoke(query)
            context = "\n\n".join(doc.page_content for doc in docs)
            
            prompt_text = f"""
            Use the following context to answer the question.
            If the answer is not present in the context, say:
            "I could not find this information in the provided documents."
            
            Context:
            {context}
            
            Question:
            {query}
            """
            
            try:
                response = llm.invoke(prompt_text)
                st.write("### Answer")
                st.write(response.content)
            except Exception as e:
                st.error(f"Error calling LLM: {e}")
    elif not query:
        st.error("Please enter a question.")
