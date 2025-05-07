import faiss
import numpy as np
from .embedding import load_embedding_model, embed_query
from sentence_transformers import SentenceTransformer

def load_vector_db(index_path="rag/vectorDB/faiss_index.index"):
    return faiss.read_index(index_path)

def retrieve_documents(query, vector_db, docs, model, top_k=5):
    query_vec = np.array([embed_query(model, query)]).astype("float32")
    D, I = vector_db.search(query_vec, top_k)
    return [docs[i] for i in I[0]]

def add_documents(new_docs, vector_db, model, docs, index_path="rag/vectorDB/faiss_index.index"):
    new_vecs = np.array(model.encode(new_docs)).astype("float32")
    vector_db.add(new_vecs)
    docs.extend(new_docs)
    faiss.write_index(vector_db, index_path)

def load_embedding_model(model_name="all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)

def embed_query(model, query):
    embedding = model.encode([query], convert_to_numpy=True)
    return embedding[0] 