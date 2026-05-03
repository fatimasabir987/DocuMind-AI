from flask import Blueprint, request, jsonify, render_template
from .rag_engine import extract_text_from_pdf, build_vector_store, retrieve_context
from .groq_client import ask_groq
import os, uuid

main = Blueprint('main', __name__)
doc_store = {}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('pdf')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Please upload a valid PDF file'}), 400

    session_id = str(uuid.uuid4())
    path = os.path.join('uploads', f"{session_id}.pdf")
    file.save(path)

    chunks = extract_text_from_pdf(path)
    if not chunks:
        return jsonify({'error': 'Could not extract text from PDF'}), 400

    idf, vectors = build_vector_store(chunks)
    doc_store[session_id] = {
        'chunks': chunks,
        'idf': idf,
        'vectors': vectors,
        'filename': file.filename
    }

    return jsonify({'session_id': session_id, 
                    'filename': file.filename, 
                    'chunks': len(chunks)})

@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('session_id')
    question = data.get('question', '').strip()

    if not session_id or session_id not in doc_store:
        return jsonify({'error': 'Please upload a document first'}), 400
    if not question:
        return jsonify({'error': 'Please enter a question'}), 400

    store = doc_store[session_id]
    context = retrieve_context(
        question,
        store['chunks'],
        store['idf'],
        store['vectors']
    )
    answer = ask_groq(question, context)
    return jsonify({'answer': answer})