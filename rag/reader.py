# rag/reader.py
import openai

def load_reader_model(api_key):
    openai.api_key = api_key

def generate_answer(query, retrieved_docs, model="gpt-3.5-turbo"):
    context = "\n\n".join(retrieved_docs)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()