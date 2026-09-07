# Agentic AI Hub

Welcome to the **Agentic AI Hub**! This repository houses a collection of 5 specialized AI agents, unified into a single [Streamlit](https://streamlit.io/) Multipage Application. 

Each agent is designed for a specific enterprise or research use case, leveraging LLMs and advanced retrieval techniques (RAG) to provide automated, intelligent assistance.

## 🤖 The Agents

1. **Hospital AI Assistant** (`agent 1`)
   - Capable of answering questions based on a hospital knowledge base.
2. **R&D Literature Research Agent** (`agent 2`)
   - Automated multi-source research brief generation using tools like Wikipedia and PubMed.
3. **Enterprise Knowledge RAG Agent** (`agent 3`)
   - Retrieves and answers questions about organizational information from enterprise documents (e.g., financial policies).
4. **Enterprise IT Helpdesk AI Assistant** (`agent 4`)
   - Provides intelligent IT support and troubleshooting assistance for enterprise environments.
5. **Voice Medical Information Assistant** (`agent 5`)
   - A specialized AI designed to process and provide medical information, with voice interaction capabilities.

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed (preferably Python 3.9+). 

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Agentic_AI.git
   cd Agentic_AI
   ```

2. **Set up a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   Install the unified requirements required for all the agents:
   ```bash
   pip install -r agents/requirements.txt
   ```

4. **Environment Variables:**
   Most of the agents require an API key to function. 
   - Create a `.env` file in the root directory or inside the `agents` folder.
   - Add the necessary keys (e.g., `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, etc.) depending on which models you are using.

### Running the App Locally

Start the central Streamlit Hub by running:

```bash
streamlit run agents/app.py
```

This will launch a web interface where you can easily switch between the 5 different agents using the navigation sidebar.

---

## ☁️ Deployment on Streamlit Cloud

To deploy this entire hub on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this repository to GitHub.
2. Log into Streamlit Cloud and click **Create App**.
3. Select your repository, branch, and set the **Main file path** to `agents/app.py`.
4. Add your API keys (like `OPENROUTER_API_KEY`) to the **Secrets** section in the Streamlit Cloud advanced settings.
5. Click **Deploy!** Streamlit will automatically install dependencies from `agents/requirements.txt` and launch the multipage app.
