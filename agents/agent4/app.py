import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

# st.set_page_config(page_title="Enterprise IT Helpdesk AI", layout="centered")
st.title("💻 Enterprise IT Helpdesk AI Assistant")

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    st.warning("Please set OPENROUTER_API_KEY in your .env file.")
    st.stop()

@tool
def check_system_status(system: str) -> str:
    """Check the operational status of an enterprise system (e.g. wifi, vpn, email, github)."""
    systems = {
        "wifi": "Wi-Fi service is operational.",
        "vpn": "VPN service is operational.",
        "email": "Email service is operational.",
        "github": "GitHub service is operational."
    }
    return systems.get(system.lower(), f"No status information is available for {system}.")

@tool
def get_employee_information(employee_name: str) -> str:
    """Retrieve employee information from the enterprise directory (e.g. rahul, priya, arjun)."""
    employees = {
        "rahul": {"department": "Finance", "office": "Hyderabad", "device": "Dell Latitude 5440"},
        "priya": {"department": "Engineering", "office": "Bangalore", "device": "Lenovo ThinkPad"},
        "arjun": {"department": "HR", "office": "Delhi", "device": "HP EliteBook"}
    }
    employee = employees.get(employee_name.lower())
    if not employee:
        return f"No employee information found for {employee_name}."
    return f"Employee: {employee_name}\nDepartment: {employee['department']}\nOffice: {employee['office']}\nDevice: {employee['device']}"

@tool
def create_ticket(employee_name: str, issue: str) -> str:
    """Create an IT support ticket for an employee."""
    ticket_id = "INC-1001"
    return f"Ticket created successfully.\nTicket ID: {ticket_id}\nEmployee: {employee_name}\nIssue: {issue}\nStatus: Open"

@tool
def search_it_policy(query: str) -> str:
    """Search the company's IT policies."""
    policies = {
        "password": "Employees must change their password every 90 days. Passwords must contain uppercase, lowercase, numbers, and special characters.",
        "vpn": "Employees must use the approved company VPN when accessing internal systems from outside the corporate network.",
        "software": "Employees must request approval from IT before installing company-managed software.",
        "wifi": "Employees should connect company devices to the approved corporate Wi-Fi network."
    }
    query = query.lower()
    for keyword, policy in policies.items():
        if keyword in query:
            return policy
    return "No matching IT policy was found."

@tool
def get_ticket_status(ticket_id: str) -> str:
    """Retrieve the current status of an IT support ticket (e.g. INC-1001, INC-1002)."""
    tickets = {
        "INC-1001": "Open - IT technician has been assigned.",
        "INC-1002": "Resolved - Password was successfully reset.",
        "INC-1003": "In Progress - VPN issue is being investigated."
    }
    return tickets.get(ticket_id.upper(), f"Ticket {ticket_id} was not found.")

@st.cache_resource
def init_agent():
    llm = ChatOpenRouter(
        model="openrouter/auto",
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
        temperature=0
    )
    tools = [
        check_system_status,
        get_employee_information,
        create_ticket,
        get_ticket_status,
        search_it_policy
    ]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful Enterprise IT Helpdesk AI Assistant. You have access to various IT tools."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

agent_executor = init_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("How can I help with your IT issue?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            # Format chat history for LangChain
            chat_history = []
            for msg in st.session_state.messages[:-1]: # exclude the latest user message
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
            st.session_state.messages.append({"role": "assistant", "content": reply})
