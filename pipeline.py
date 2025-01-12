import os
from typing import Union, List

# Import Groq API
from groq import Groq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq API client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize LLM
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="mixtral-8x7b-32768",
    temperature=0.7,
    max_tokens=4096
)

# Load documents and set up embeddings
PDF_DIRECTORY = "pdfs"
LOADED_DOCS = PyPDFDirectoryLoader(PDF_DIRECTORY).load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(LOADED_DOCS)

vectorstore = Chroma.from_documents(
    documents=docs,
    collection_name="open_source_embeds",
    embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)
retriever = vectorstore.as_retriever()

# RAG template and chain setup
rag_template = """Answer the question based only on the following context:
{context}
Question: {question}
"""
rag_prompt = ChatPromptTemplate.from_template(rag_template)
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Define helper functions
def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Groq's Whisper API"""
    with open(audio_path, "rb") as audio_file:
        transcription = groq_client.audio.translations.create(
            model="whisper-large-v3",
            file=audio_file,
        )
    return transcription.text

def process_audio_input(audio: Union[str, List[str]]) -> str:
    """Process single or multiple audio files and return combined transcription"""
    if isinstance(audio, list):
        transcriptions = [transcribe_audio(audio_file) for audio_file in audio]
        return " ".join(transcriptions)
    return transcribe_audio(audio)

def chat_pipeline(query: Union[str, dict], history: List[List[str]] = None) -> str:
    """Process chat input and return the output"""
    try:
        if isinstance(query, dict):
            # Multimodal input handling
            text_query = query.get("text", "")
            audio_files = query.get("files", [])

            if audio_files:
                audio_transcription = process_audio_input(audio_files)
                query = f"{text_query} {audio_transcription}" if text_query else audio_transcription
            else:
                query = text_query

        response = rag_chain.invoke(query)
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Usage example
if __name__ == "__main__":
    query_input = "What is machine learning?"  # Replace with your query or multimodal input
    result = chat_pipeline(query_input)
    print("Response:", result)
