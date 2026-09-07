import streamlit as st

st.set_page_config(page_title="Agentic AI Hub", layout="centered")

pg = st.navigation([
    st.Page("agent/app.py", title="Agent 1", icon="🔍"),
    st.Page("agent2/app.py", title="Agent 2", icon="📊"),
    st.Page("agent3/app.py", title="Agent 3", icon="📂"),
    st.Page("agent4/app.py", title="Agent 4", icon="🤖"),
    st.Page("agent5/app.py", title="Agent 5", icon="🚀"),
])

pg.run()
