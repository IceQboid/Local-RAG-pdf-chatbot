import streamlit as st
from data_processing import add_to_chroma, clear_database, load_and_process_documents
from advanced_query import query_rag_with_multiquery
import os

# Set page configuration
st.set_page_config(
    page_title="Content Engine",
    page_icon="📄",
    layout="centered"
)

st.title("🤖 Content Engine")
import streamlit as st

# Disclaimer pull-down message
with st.expander("ℹ️", expanded=False):
    st.markdown("""
    This is a PDF Chatbot interface where you can converse about the content of the provided PDFs with the bot.
    
    Here is how It Works:
    1. Upload your PDF files.    
    2. The uploaded files will be processed, split into chunks, and added to the vector database.
    3. The database can be used for future queries.
    4. Delete chat to remove history and re-do document loading.
    """)




# Initialize session state for chat history and document processing state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False
    
if st.button("Delete Chat"):
    # Clear the chat history and reset the document processing state
    st.session_state.chat_history = []
    st.session_state.documents_processed = False
    st.rerun()  # Refresh the page to reset the state

# File uploader for PDF documents
uploaded_files = st.file_uploader("Upload your PDF file", type=["pdf"],accept_multiple_files=True)


process_button = st.button("Process Document")


    
# Handle file upload and document processing
if uploaded_files and process_button and not st.session_state.documents_processed:
    data_folder = "data"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    file_paths = []  # List to store file paths of the uploaded PDFs

    for uploaded_file in uploaded_files:
        file_path = os.path.join(data_folder, uploaded_file.name)
        file_paths.append(file_path)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())  # Save each file properly


    with st.spinner("Processing documents... Please wait."):
        chunks = load_and_process_documents([file_paths])   # Add chunks to Chroma  
        add_to_chroma(chunks)

    st.session_state.documents_processed = True
    st.success("Document processed successfully! You can now ask questions.")

# Display chat history using chat bubbles
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display chat input only after document processing
if st.session_state.documents_processed:
    user_input = st.chat_input("Inquire me about the content...")

    if user_input:
        # Append user query to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Display user input immediately
        with st.chat_message("user"):
            st.markdown(user_input)
            
        

        # Simulate assistant response (real query call)
        with st.chat_message("assistant"):
            stop_processing = st.empty() 
            with st.spinner("Thinking..."):               
                if stop_processing.button("Stop Processing"):
                    st.warning("Query processing stopped by the user.")
                    st.stop()
                    
                response = query_rag_with_multiquery(user_input)
                st.markdown(response)
        stop_processing.empty()

        # Append assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

else:
    with st.chat_message("assistant"):
        st.markdown("Please upload and press Process Document to start querying.")
