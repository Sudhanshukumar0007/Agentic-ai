import streamlit as st
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun, PubmedQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, PubMedAPIWrapper
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ToolStrategy

# st.set_page_config(page_title="R&D Literature Research Agent", layout="wide")

st.title("📚 R&D Literature Research Agent")
st.write("Automated Multi-Source Research Brief Generation using Wikipedia and PubMed.")

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    st.warning("Please set OPENROUTER_API_KEY in your .env file.")
    st.stop()

class ResearchBrief(BaseModel):
    """Structured format for a research brief."""
    topic: str = Field(description="The main topic being researched.")
    background: str = Field(description="A concise explanation and background of the topic.")
    recent_research: list[str] = Field(description="Important research findings, papers, or studies related to the topic.")
    key_findings: list[str] = Field(description="The most important findings from the research.")
    open_questions: list[str] = Field(description="Important unresolved questions, limitations, or areas for future research.")

@st.cache_resource
def init_agent():
    llm = ChatOpenAI(
        model="openrouter/auto", # default to auto or stealth/ox-alpha if needed
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
        temperature=0
    )

    wiki_wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=800)
    wiki_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)

    pubmed_wrapper = PubMedAPIWrapper(top_k_results=3)
    pubmed_tool = PubmedQueryRun(api_wrapper=pubmed_wrapper)

    tools = [wiki_tool, pubmed_tool]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are an R&D research assistant. "
            "Use the wikipedia tool for background and definitions. "
            "Use the pubmed tool for recent research papers and clinical/scientific findings. "
            "Always check both tools before writing your final answer. "
            "Clearly separate background information from recent research findings, "
            "and note any open or unresolved questions in the field."
        ),
        response_format=ToolStrategy(ResearchBrief)
    )
    return agent

agent = init_agent()

query = st.text_input("Enter research topic (e.g., 'paracetamol'):")

if st.button("Generate Research Brief"):
    if query:
        with st.spinner("Researching..."):
            result = agent.invoke({
                "messages": [{"role": "user", "content": query}]
            })
            
            # The structured response is typically available in the output
            st.write("### Research Results")
            st.json(result) # Or format the ResearchBrief nicely if it returns a dict
    else:
        st.error("Please enter a topic to research.")
