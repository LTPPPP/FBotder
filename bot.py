import os
import logging
import nltk
from typing import List
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from chromadb import Client
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
from transformers import AutoConfig
from serpapi import GoogleSearch

# Configure logging and NLTK
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
nltk.download('punkt')

# Load environment variables
load_dotenv()

def load_dataset(path: str) -> List[str]:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} does not exist.")
    loader = TextLoader(path, encoding='utf-8')
    return loader.load()

def split_documents(documents: List[str], chunk_size: int = 500, chunk_overlap: int = 4) -> List[str]:
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)

def configure_chroma(persist_dir: str, index_name: str, docs: List[str], embeddings) -> Chroma:
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)

    if not os.access(persist_dir, os.W_OK):
        raise PermissionError(f"The directory {persist_dir} is not writable.")

    chroma_client = Client(Settings(persist_directory=persist_dir))
    existing_collections = [collection.name for collection in chroma_client.list_collections()]

    if index_name not in existing_collections:
        docsearch = Chroma.from_documents(documents=docs, embedding=embeddings, collection_name=index_name, persist_directory=persist_dir)
    else:
        docsearch = Chroma(collection_name=index_name, persist_directory=persist_dir)

    docsearch.persist()
    return docsearch

def configure_llm(repo_id: str, api_token: str) -> HuggingFaceHub:
    config = AutoConfig.from_pretrained(repo_id)
    max_sequence_length = config.max_position_embeddings

    return HuggingFaceHub(
        repo_id=repo_id,
        model_kwargs={"temperature": 0.6, "top_k": 20, "top_p": 0.85, "max_length": min(10000, max_sequence_length)},
        huggingfacehub_api_token=api_token
    )

def create_prompt_template() -> PromptTemplate:
    template = """
    Act as an expert in everything and answer the question of users. 
    Your response should be limited to 2 sentences or 1000 words and summarize the main points of the context.
    Answer will be translated to Vietnamese.
    IMPORTANT: summarize the main points of the context.

    Context: {context}
    Question: {question}
    Answer: 
    """
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

def create_rag_chain(docsearch, llm) -> dict:
    prompt = create_prompt_template()
    return (
        {"context": docsearch.as_retriever(), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

def save_to_file(question: str, answer: str, filename: str = 'new_answers.txt'):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"Q: {question}\nA: {answer}\n\n")

def google_search(query: str) -> str:
    api_key = "9c14bc0b080dfed830e2022860b10ee851ca1a05"
    if not api_key:
        raise ValueError("SERPAPI_API_KEY environment variable is not set.")

    search = GoogleSearch({"q": query, "api_key": api_key})
    result = search.get_dict()

    try:
        answer_box = result["answer_box"]["snippet"]
    except KeyError:
        try:
            answer_box = result["organic_results"][0]["snippet"]
        except (KeyError, IndexError):
            answer_box = "No relevant answer found."

    return answer_box

def chat(rag_chain):
    while True:
        user_input = input("Nhập câu hỏi của bạn (hoặc 'quit' để thoát): ")
        if user_input.lower() == 'quit':
            break
        try:
            result = rag_chain.invoke(user_input)   
            answer_start = "Answer: "
            response = result.split(answer_start)[-1].strip()

            if not response:
                response = google_search(user_input)

            print("Câu trả lời:", response)
            save_to_file(user_input, response)
        except Exception as e:
            logger.error(f"Lỗi: {e}")
            print(f"Đã xảy ra lỗi: {e}")

if __name__ == '__main__':
    dataset_path = './dataset.txt'
    documents = load_dataset(dataset_path)
    docs = split_documents(documents)
    embeddings = HuggingFaceEmbeddings()

    persist_directory = "./chroma_data"
    index_name = "infinity-demo"
    docsearch = configure_chroma(persist_directory, index_name, docs, embeddings)

    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    huggingfacehub_api_token = "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"
    llm = configure_llm(repo_id, huggingfacehub_api_token)

    rag_chain = create_rag_chain(docsearch, llm)
    chat(rag_chain)
