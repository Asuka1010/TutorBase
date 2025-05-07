import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import pickle
from PyPDF2 import PdfReader
from rag.utils import split_text

# 1. Load embedding model
def load_embedding_model(model_name="all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)

model = load_embedding_model()

# 2. Set FAISS index path
INDEX_PATH = 'rag/vectorDB/faiss_index.index'
METADATA_PATH = 'rag/vectorDB/metadata.pkl'
PAPERS_DIR = 'rag/papers'

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        #print(text)
    return text

def load_all_papers_and_embed(chunk_size=500):
    documents = []
    metadata = []
    for fname in os.listdir(PAPERS_DIR):
        if fname.endswith('.pdf'):
            pdf_path = os.path.join(PAPERS_DIR, fname)
            text = extract_text_from_pdf(pdf_path)
            chunks = split_text(text, chunk_size)
            documents.extend(chunks)
            # 메타데이터: 파일명, chunk 인덱스
            metadata.extend([{'file': fname, 'chunk': i} for i in range(len(chunks))])
    if not documents:
        raise ValueError("No PDF documents found in the papers directory.")
    embeddings = model.encode(documents, convert_to_numpy=True)
    return documents, embeddings, metadata

def build_and_save_index_from_papers():
    documents, embeddings, metadata = load_all_papers_and_embed()
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Indexed {len(documents)} chunks from {len(metadata)} PDF files.")

# 3. Embed documents
def embed_documents(documents):
    """
    documents: List[str]
    returns: np.array of shape (num_docs, embedding_dim)
    """
    embeddings = model.encode(documents, convert_to_numpy=True)
    return embeddings


# 4. Build and save FAISS index
def build_faiss_index(embeddings, dimension):
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def save_faiss_index(index, path=INDEX_PATH):
    faiss.write_index(index, path)


def load_faiss_index(path=INDEX_PATH):
    if os.path.exists(path):
        return faiss.read_index(path)
    else:
        raise FileNotFoundError(f"{path} not found.")


# 5. Save / Load metadata
def save_metadata(metadata, path=METADATA_PATH):
    with open(path, 'wb') as f:
        pickle.dump(metadata, f)


def load_metadata(path=METADATA_PATH):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    else:
        raise FileNotFoundError(f"{path} not found.")


# 6. Query FAISS index
def embed_query(model, query):
    embedding = model.encode([query], convert_to_numpy=True)
    return embedding[0]


def search_index(index, query_embedding, top_k=5):
    distances, indices = index.search(query_embedding, top_k)
    return distances, indices

if __name__ == "__main__":
       build_and_save_index_from_papers()