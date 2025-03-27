import os
import json
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings

# Load JSON data
file_path = "data/www.runtime-solutions.com_crawl_results.json"
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Initialize FastAPI app
app = FastAPI()

# Define request model
class QueryRequest(BaseModel):
    query: str

# Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Prepare FAISS vector store
def create_vectorstore():
    texts = [entry.get("title", "") + " " + entry.get("description", "") for entry in data]
    metadata = [{"url": entry.get("url", "")} for entry in data]
    db = FAISS.from_texts(texts, embedding_model, metadatas=metadata)
    db.save_local("vectorstore/db_faiss")
    return db

vectorstore = create_vectorstore()

# Load FAISS
def get_vectorstore():
    return FAISS.load_local("vectorstore/db_faiss", embedding_model, allow_dangerous_deserialization=True)

vectorstore = get_vectorstore()

# Load LLM
HF_TOKEN = os.getenv("HF_TOKEN")
huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

def load_llm():
    return HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.2,
        model_kwargs={"token": HF_TOKEN, "max_length": "512"}
    )

llm = load_llm()

# Custom Prompt
custom_prompt_template = """
Use the pieces of information provided in the context to answer user's questions.
If you don't know the answer, just say that you don't know.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""

prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

# Create Retrieval QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
    return_source_documents=True,
    chain_type_kwargs={'prompt': prompt}
)

@app.post("/chatbot/")
def chatbot(request: QueryRequest):
    response = qa_chain.invoke({'query': request.query})
    return {"response": response["result"], "source_documents": response["source_documents"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
