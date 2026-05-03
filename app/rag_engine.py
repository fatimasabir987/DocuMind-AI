import fitz  # PyMuPDF
import math
import numpy as np
from collections import Counter

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    chunks = []
    for page in doc:
        text = page.get_text()
        words = text.split()
        for i in range(0, len(words), 400):
            chunk = " ".join(words[i:i+400])
            if chunk.strip():
                chunks.append(chunk)
    return chunks

def tokenize(text):
    return text.lower().split()

def build_vector_store(chunks):
    # TF-IDF pure Python mein
    tokenized = [tokenize(c) for c in chunks]
    
    # IDF calculate karo
    df = {}
    N = len(chunks)
    for tokens in tokenized:
        for word in set(tokens):
            df[word] = df.get(word, 0) + 1
    
    idf = {word: math.log(N / (freq + 1)) for word, freq in df.items()}
    
    # TF-IDF vectors banao
    vectors = []
    for tokens in tokenized:
        tf = Counter(tokens)
        total = len(tokens)
        vec = {word: (count/total) * idf.get(word, 0) 
               for word, count in tf.items()}
        vectors.append(vec)
    
    return idf, vectors

def cosine_sim(vec1, vec2):
    common = set(vec1.keys()) & set(vec2.keys())
    dot = sum(vec1[w] * vec2[w] for w in common)
    mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0
    return dot / (mag1 * mag2)

def retrieve_context(query, chunks, idf, vectors, top_k=4):
    query_tokens = tokenize(query)
    tf = Counter(query_tokens)
    total = len(query_tokens)
    query_vec = {word: (count/total) * idf.get(word, 0) 
                 for word, count in tf.items()}
    
    scores = [cosine_sim(query_vec, vec) for vec in vectors]
    top_indices = sorted(range(len(scores)), 
                         key=lambda i: scores[i], reverse=True)[:top_k]
    
    return "\n\n".join([chunks[i] for i in top_indices])