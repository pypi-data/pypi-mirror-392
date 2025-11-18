import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader

def load_pdfs_from_folder(folder_path):
    docs = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            loader = PyMuPDFLoader(os.path.join(folder_path, file))
            docs.extend(loader.load())
    return docs

def build_vectorstore(docs, persist_dir):
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_dir
    )
    vectorstore.persist()
    return vectorstore
