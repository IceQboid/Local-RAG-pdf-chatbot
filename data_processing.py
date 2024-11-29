from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from embed_function import text_embed
import argparse
import os
import shutil
from concurrent.futures import ThreadPoolExecutor



DATA_PATH = "data"
CHROMA_PATH = "chroma"

def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def load_documents():
    document_loader= PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

'''documents = load_documents()
print(documents[0])'''


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


'''documents = load_documents()
chunks = split_documents(documents)
print(chunks[0])'''


def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0
    
    
    #first we gather source and page from all chunks to make a simple page/source ID
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
        #since several chunks share the same page ID, we create a condition for chunk index count
        #this defines if the page id is same, increase the chunk index count
        if current_page_id == last_page_id:
            current_chunk_index += 1
        #this defines if the page is different, reset the chunk index to 0
        else:
            current_chunk_index = 0
        #Unique ID in desired format
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id    
        # Add it to the page meta-data as an element
        chunk.metadata["id"] = chunk_id
    return chunks
#This creates the desired chunks with ID


# Process the chunks by calling the function
'''chunks_with_ids = calculate_chunk_ids(chunks)


# Checking the first chunk to see if it gave us the desired format
chunk_to_check = chunks_with_ids[0]  
print(f"Chunk ID: {chunk_to_check.metadata['id']}, Metadata: {chunk_to_check.metadata}")'''


def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=text_embed()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # This is only to add or update more chunks 
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}") #length must be 0 if run first without existing DB

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
    #Runs if there are new chunks
    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        #create new unique IDs for new chunks
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        #Adds new chunk along with its Ids to the database
        db.add_documents(new_chunks, ids=new_chunk_ids)
        #for saving and future use 
        
    else:
        print("✅ No new documents to add")
        

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        import streamlit as st
    st.session_state.documents_processed = False 
        
def load_and_process_documents(pdf_path):
    with ThreadPoolExecutor() as executor:
        documents = list(executor.map(load_documents))
        chunks = list(executor.map(split_documents, documents))
        chunks_with_ids = [calculate_chunk_ids(chunk_list) for chunk_list in chunks]
    return chunks_with_ids
        
if __name__ == "__main__":
    main()
