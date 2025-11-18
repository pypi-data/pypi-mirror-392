import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

def extract_text_from_pdf(file_path):
    print(f"Note: Using placeholder for PDF extraction. Implement me: {file_path}")
    return "This is placeholder PDF text."

class SimpleRAG:
    def __init__(self, openai_api_key, model="gpt-3.5-turbo", embed_model="all-MiniLM-L6-v2"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.embedder = SentenceTransformer(embed_model)
        self.knowledge = []
        self.doc_embeddings = None

    def add_text(self, text):
        self.knowledge.append(text)
        self.doc_embeddings = None

    def add_pdf(self, file_path):
        try:
            text = extract_text_from_pdf(file_path)
            self.add_text(text)
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")

    def _embed(self, texts):
        return self.embedder.encode(texts, normalize_embeddings=True)

    def build_index(self):
        print("Building embedding index...")
        if not self.knowledge:
            self.doc_embeddings = np.array([])
            print("Index built (empty).")
            return
        self.doc_embeddings = self._embed(self.knowledge)
        print(f"Index built with {len(self.doc_embeddings)} entries.")

    def _retrieve(self, query, top_k=3):
        if self.doc_embeddings is None:
            print("Index not found. Building index first.")
            self.build_index()
        if not self.knowledge or self.doc_embeddings.shape[0] == 0:
            return []
        q_emb = self._embed([query])[0]
        sims = np.dot(self.doc_embeddings, q_emb)
        top_idx = np.argsort(sims)[-top_k:][::-1]
        return [self.knowledge[i] for i in top_idx]

    def ask(self, query):
        retrieved = self._retrieve(query)
        if not retrieved:
            return "I have no knowledge in my database to answer this question."
        context = "\n\n".join(retrieved)
        prompt = f"Using the following context, please answer the question.\n\nContext:\n{context}\n\nQuestion: {query}"
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred while contacting the OpenAI API: {e}"
