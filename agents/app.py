import streamlit as st

st.set_page_config(page_title="Agentic AI Hub", layout="centered")

pg = st.navigation([
    st.Page("agent/app.py", title="Agent 1", icon="🔍", url_path="agent1"),
    st.Page("agent2/app.py", title="Agent 2", icon="📊", url_path="agent2"),
    st.Page("agent3/app.py", title="Agent 3", icon="📂", url_path="agent3"),
    st.Page("agent4/app.py", title="Agent 4", icon="🤖", url_path="agent4"),
    st.Page("agent5/app.py", title="Agent 5", icon="🚀", url_path="agent5"),
])

pg.run()
