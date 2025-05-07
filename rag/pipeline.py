from rag.retriever import load_vector_db, retrieve_documents
from rag.embedding import load_embedding_model, embed_query
from rag.reranker import load_reranker_model, rerank
from rag.reader import load_reader_model, generate_answer
from rag.utils import load_pickle

class RAGPipeline:
    def __init__(self, vector_db_path, docs_path, reranker_model_name, openai_api_key, embedding_model_name="all-MiniLM-L6-v2"):
        # Load vector DB and docs
        self.vector_db = load_vector_db(vector_db_path)
        self.docs = load_pickle(docs_path)
        # Load embedding model
        self.embed_model = load_embedding_model(embedding_model_name)
        # Load reranker
        self.reranker_tokenizer, self.reranker_model = load_reranker_model(reranker_model_name)
        # Load reader (LLM)
        load_reader_model(openai_api_key)

    def run(self, query, top_k=5, top_n=3):
        # 1. Query embedding
        query_vec = embed_query(self.embed_model, query)
        # 2. Retrieve top-k documents
        retrieved_docs = retrieve_documents(query, self.vector_db, self.docs, self.embed_model, top_k=top_k)
        # 3. Rerank top-k documents
        top_docs = rerank(query, retrieved_docs, self.reranker_tokenizer, self.reranker_model, top_n=top_n)
        # 4. Generate answer using reader
        answer = generate_answer(query, top_docs)
        return answer 