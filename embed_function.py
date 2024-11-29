from langchain_ollama import OllamaEmbeddings

def text_embed():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings 