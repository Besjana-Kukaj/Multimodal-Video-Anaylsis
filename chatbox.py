# chatbox.py
from sentence_transformers import SentenceTransformer
import numpy as np
from llama_cpp import Llama
import os  # <-- Make sure to import os for os.cpu_count()


class ChatHandler:
    def __init__(self, transcript_data):  # Renamed parameter for clarity
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # --- CORRECTED Llama Initialization ---
        self.llm = Llama(
            model_path='./models/mistral-7b-instruct-v0.1.Q4_K_M.gguf',
            n_ctx=4096,  # Try a larger context window, 2048 or 4096 is common for Mistral
            n_batch=512,  # How many tokens to process in parallel during prompt evaluation. Can affect speed/memory.
            n_threads=os.cpu_count(),  # Use all available CPU cores for processing
            verbose=True  # Enable verbose output for Llama, useful for debugging
        )
        # --- END CORRECTED Llama Initialization ---

        self.vector_db = []  # This line MUST be inside __init__
        # Iterate through the list of dictionaries returned by YouTubeTranscriptApi
        for snippet in transcript_data:
            # Extract the 'text' from the dictionary and strip whitespace
            chunk_text = snippet.get('text', '').strip()

            # Only process if there's actual text content
            if chunk_text:
                # Encode the actual text string
                embedding = self.embedder.encode(chunk_text).tolist()
                self.vector_db.append((chunk_text, embedding))
            else:
                print(f"Warning: Skipping empty or invalid transcript snippet: {snippet}")

    def cosine_similarity(self, a, b):
        # Ensure inputs are numpy arrays for calculation, then convert result
        a_np = np.array(a)
        b_np = np.array(b)
        dot = np.dot(a_np, b_np)
        norm_a = np.linalg.norm(a_np)
        norm_b = np.linalg.norm(b_np)

        # Handle division by zero for embeddings that might be all zeros
        if norm_a == 0 or norm_b == 0:
            return 0.0

        # Explicitly convert to standard Python float at the end of calculation
        return float(dot / (norm_a * norm_b))

    def retrieve(self, query, top_n=3):
        # Encode the query and convert to a standard Python list
        query_embedding = self.embedder.encode(query).tolist()
        scored_chunks = []
        for chunk_text, emb in self.vector_db:  # chunk_text is now a string
            sim = self.cosine_similarity(query_embedding, emb)
            scored_chunks.append((chunk_text, sim))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_n]

    def respond(self, user_query):
        retrieved = self.retrieve(user_query)
        context_parts = []
        for chunk_text, _ in retrieved:
            context_parts.append(f'- {str(chunk_text)}\n')
        context = ''.join(context_parts)

        print(
            f"\n--- Context for LLM for query '{user_query}': ---\n{context}\n---------------------------------------------\n")

        # --- MODIFIED PROMPT ---
        prompt = (
            "You are a helpful chatbot. Based on the provided context, answer the user's question concisely.\n"
            "Use only the following pieces of context to answer the question. "
            "Do not make up new information. If the answer cannot be found, state that you don't know.\n"
            f"Context:\n{context}\n"  # Explicitly label context
            f"Question: {str(user_query)}\n"
            "Answer:"  # Explicitly ask for an answer
        )

        try:
            result = self.llm.create_completion(
                prompt=prompt,
                max_tokens=200,
                temperature=0.7,  # Increase temperature from default (often 0.0 or 0.1)
                top_p=0.9,  # Adjust top_p
                top_k=40,  # Adjust top_k
                stop=["\nQuestion:", "\nAI:", "\nHuman:", "\nUser:", "\nAssistant:"]  # Add more common stop sequences
            )
            print("LLM output:", result)

            if result and 'choices' in result and len(result['choices']) > 0 and 'text' in result['choices'][0]:
                generated_text = result['choices'][0]['text'].strip()
                if not generated_text:
                    print("Warning: LLM generated an empty string even after completion.")
                    return "(AI struggled to provide an answer based on the context.)"
                return generated_text
            else:
                print("Warning: LLM response structure unexpected or empty.")
                return "(No response from AI, unexpected output format.)"
        except Exception as e:
            print(f"Error during LLM completion: {e}")
            raise  # Re-raise the exception to be caught by the Flask route

    def ask(self, question):
        return self.respond(question)