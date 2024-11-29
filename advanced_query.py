import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from embed_function import text_embed

# Define paths and constants
CHROMA_PATH = "chroma"

# Prompt templates
QUERY_PROMPT_TEMPLATE = """
You are an AI assistant tasked with improving the retrieval of relevant documents. 
Generate five different versions of the given user question to maximize the relevance of retrieved documents.
Original question: {question}
"""

RAG_PROMPT_TEMPLATE = """
Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

def query_rag_with_multiquery(query_text: str):
    # Load the Chroma vector database
    embedding_function = text_embed()
    vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # Initialize the LLM
    llm = OllamaLLM(model="mistral-openorca")
    
    query_prompt = PromptTemplate(
        input_variables=["question"],
        template=QUERY_PROMPT_TEMPLATE,
    )
    
    # Initialize the retriever
    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(),
        llm,
        prompt=query_prompt,
    )

    # Generate the context using the retriever
    documents = retriever.invoke(query_text)

    context_text = "\n\n---\n\n".join([doc.page_content for doc in documents])

    # Create the RAG prompt
    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    final_prompt = rag_prompt.format(context=context_text, question=query_text)

    # Invoke the LLM with the RAG prompt
    response = llm.invoke(final_prompt)
    return response


# Test the query RAG with multiquery function directly in the notebook
query_text = "What is the total revenue of Google Search in 2023?"

# Call the function to get a response
response = query_rag_with_multiquery(query_text)
print("\n--- Final Response ---\n")
print(response)