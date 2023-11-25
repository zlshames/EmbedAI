import os

from flask import jsonify, request
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from ..constants import CHROMA_SETTINGS
from . import app
from ..document_loaders import load_documents_from_dir
from ..llm_model import LLMModel


embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME", 'all-MiniLM-L6-v2')
persist_directory = os.environ.get('PERSIST_DIRECTORY', 'db')
source_directory = os.environ.get('SOURCE_DIRECTORY', 'source_documents')

def init_routes():
    @app.route('/ingest', methods=['GET'])
    def ingest_data():
        # Load documents and split in chunks
        app.logger.info(f"Loading documents from {source_directory}")
        chunk_size = 500
        chunk_overlap = 50
        documents = load_documents_from_dir(source_directory)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(documents)
        app.logger.info(f"Loaded {len(documents)} documents from {source_directory}")
        app.logger.info(f"Split into {len(texts)} chunks of text (max. {chunk_size} characters each)")
        if len(texts) == 0:
            return jsonify(response="Ingest complete, no documents found")

        # Create embeddings
        embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
        
        # Create and store locally vectorstore
        db = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory, client_settings=CHROMA_SETTINGS)
        db.persist()
        db = None
        return jsonify(response="Success")
        
    @app.route('/get_answer', methods=['POST'])
    def get_answer():
        query = request.json
        embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
        retriever = db.as_retriever()

        # Load the model and throw an error if it doesn't exist
        model = LLMModel().llm
        if not model:
            return jsonify(response="No model loaded"), 400
        
        # If there is no query, throw an error
        if not query:
            return jsonify(response="No query provided"), 400

        # Get the answer from the model
        qa = RetrievalQA.from_chain_type(llm=model, chain_type="stuff", retriever=retriever, return_source_documents=True)
        response = qa(query)
        answer, docs = response['result'], response['source_documents']
        
        # Extract the source documents
        source_data = []
        for document in docs:
            source_data.append({"name": document.metadata["source"]})

        return jsonify(query=query, answer=answer, source=source_data)


    @app.route('/upload_doc', methods=['POST'])
    def upload_doc():
        if 'document' not in request.files:
            return jsonify(response="No document file found"), 400
        
        document = request.files['document']
        if not document.filename:
            return jsonify(response="No selected file"), 400

        filename = document.filename
        save_path = os.path.join('source_documents', filename)
        document.save(save_path)

        return jsonify(response="Document upload successful")

    @app.route('/download_model', methods=['GET'])
    def download_and_save():
        model = LLMModel()
        model.download_model(force=True)
        return jsonify(response="Download completed")