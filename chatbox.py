# chatbox.py
from sentence_transformers import SentenceTransformer
import numpy as np
from llama_cpp import Llama
import os


class ChatHandler:
    def __init__(self):
        print("ChatHandler: Initializing SentenceTransformer and Llama model (once)...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.llm = Llama(
            model_path='./models/mistral-7b-instruct-v0.1.Q4_K_M.gguf',
            n_ctx=4096,
            n_batch=512,
            n_threads=os.cpu_count(),
            verbose=True
        )
        self.current_video_id = None
        self.vector_db = []
        print("ChatHandler: Initialization complete.")

    def _build_vector_db(self, transcript_data):
        """Builds the vector database from the given transcript data."""
        print(f"ChatHandler: Building vector database with {len(transcript_data)} snippets.")
        new_vector_db = []
        for snippet in transcript_data:
            chunk_text = snippet.get('text', '').strip()
            if chunk_text:
                embedding = self.embedder.encode(chunk_text).tolist()
                new_vector_db.append((chunk_text, embedding))
            # else:
            # print(f"Warning: Skipping empty or invalid transcript snippet: {snippet}")
        return new_vector_db

    def cosine_similarity(self, a, b):
        a_np = np.array(a)
        b_np = np.array(b)
        dot = np.dot(a_np, b_np)
        norm_a = np.linalg.norm(a_np)
        norm_b = np.linalg.norm(b_np)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def retrieve(self, query, top_n=3):
        if not self.vector_db:
            print("Warning: Attempted to retrieve from an empty vector_db (no transcript loaded).")
            return []

        query_embedding = self.embedder.encode(query).tolist()
        scored_chunks = []
        for chunk_text, emb in self.vector_db:
            sim = self.cosine_similarity(query_embedding, emb)
            scored_chunks.append((chunk_text, sim))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_n]

    def ask_question(self, user_query, video_id, transcript_fetcher_func):
        """
        Main method to ask a question. Handles transcript fetching and context management.
        :param user_query: The question from the user.
        :param video_id: The ID of the current YouTube video.
        :param transcript_fetcher_func: A callable function (e.g., get_transcript from main.py)
                                        that takes video_id and returns transcript data.
        """
     #Check to see if video_id changed
        if video_id != self.current_video_id or not self.vector_db:
            print(f"ChatHandler: Video ID changed or no context. Fetching new transcript for {video_id}.")
            try:
                transcript_data = transcript_fetcher_func(video_id)
                if not transcript_data:
                    return "(Sorry, no transcript found for this video.)"

                self.vector_db = self._build_vector_db(transcript_data)
                if not self.vector_db:
                    return "(Transcript found but no valid text chunks for analysis.)"
                self.current_video_id = video_id
            except Exception as e:
                print(f"ChatHandler: Error fetching or processing transcript for {video_id}: {e}")
                return "(Error fetching video transcript.)"
        else:
            print(f"ChatHandler: Reusing existing transcript context for {video_id}.")

    #Retrieve relevant context for the response
        retrieved = self.retrieve(user_query)
        context_parts = []
        if not retrieved:
            return "(Could not find relevant information in the video transcript.)"

        for chunk_text, _ in retrieved:
            context_parts.append(f'- {str(chunk_text)}\n')
        context = ''.join(context_parts)

        # 3. Construct prompt for LLM
        print(
            f"\n--- Context for LLM for query '{user_query}': ---\n{context}\n---------------------------------------------\n")
        prompt = (
            "You are a chatbot that answer questions about videos in which you have the transcript. Based on the provided context, answer the user's question concisely and directly.\n"
            "Use only the following pieces of context to answer the question. "
            "Do not make up new information. If the answer cannot be found, state that you don't know.\n"
            f"Context:\n{context}\n"
            f"Question: {str(user_query)}\n"
            "Answer:"
        )


        try:
            result = self.llm.create_completion(
                prompt=prompt,
                max_tokens=200,
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                stop=["\nQuestion:", "\nAI:", "\nHuman:", "\nUser:", "\nAssistant:"]
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
            return "(An internal error occurred while generating a response.)"