from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

def load_reranker_model(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, model

def rerank(query, docs, tokenizer, model, top_n=3):
    pairs = [(query, doc) for doc in docs]
    inputs = tokenizer([q for q, d in pairs], [d for q, d in pairs], return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        scores = model(**inputs).logits.squeeze().tolist()
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked[:top_n]] 