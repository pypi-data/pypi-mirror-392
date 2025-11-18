import os
import shutil
from langsmith import Client
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from .utils import load_pdfs_from_folder, build_vectorstore
from langchain_text_splitters import RecursiveCharacterTextSplitter



class RAGLecture:
    def __init__(self, persist_dir=".rag_lecture_index"):
        self.persist_dir = persist_dir
        self.vectorstore = None
        self.retriever = None
        self.client = Client()

    def index_folder(self, folder_path, reset=False):
        if reset and os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
            print("🧹 Old index cleared.\n") 

        docs = load_pdfs_from_folder(folder_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)

        if os.path.exists(self.persist_dir) and not reset:
            print("📚 Appending to existing index...\n")
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=OpenAIEmbeddings()
            )
            self.vectorstore.add_documents(splits)
        else:
            print("🆕 Creating new index...\n")
            self.vectorstore = build_vectorstore(splits, self.persist_dir)

        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 1})
        print(f"✅ Index ready for folder: {folder_path}\n")

    def ask(self, question):
        if not self.retriever:
            raise RuntimeError("No index loaded. Run index_folder() first.\n")
        
        prompt = self.client.pull_prompt("rlm/rag-prompt")
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        return rag_chain.invoke(question)
