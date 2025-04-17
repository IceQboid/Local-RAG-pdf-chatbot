# Local-RAG-pdf-chatbot
A completely local RAG-based pdf conversational AI.

Technical Workflow:
![image](https://github.com/user-attachments/assets/4782ca44-ddb6-4dca-9cc5-208dd44d2d79)


**Features:**

📄 Upload and process PDF files.

🤖 Ask questions about the uploaded content and get accurate responses.

💾 Runs entirely locally, ensuring privacy and control.

🔍 Leverages vector databases for efficient content retrieval.

**Setup Instructions**

Prerequisites :  Python 3.8+ ,Minimum 12GB RAM and 4GB VRAM for local model inference.

Required Python libraries:  pip install -r requirements.

Adjust Document reader according to Langchain documentation 

pip install -U langchain_ollama if you want to host locally using Ollama

pip install -qU chromadb langchain-chroma to install chroma extension

Clone the Repository

Set up Chroma Vector Store

Create a local Chroma database to store embeddings for the uploaded documents.

Run the Application with streamlit run app.py

Upload PDFs and Chat

