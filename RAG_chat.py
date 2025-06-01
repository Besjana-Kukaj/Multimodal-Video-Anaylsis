from sentence_transformers import SentenceTransformer
import numpy as np
from llama_cpp import Llama

# Load sentence transformer for embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')

dataset = []
with open('transcript.txt', 'r') as file:
    dataset = file.readlines()
print(f'Loaded {len(dataset)} entries')

VECTOR_DB = []

def add_chunk_to_database(chunk):
    embedding = embedder.encode(chunk).tolist()  # float list
    VECTOR_DB.append((chunk, embedding))

for i, chunk in enumerate(dataset):
    add_chunk_to_database(chunk)
    print(f'Added chunk {i+1}/{len(dataset)} to the database')

def cosine_similarity(a, b):
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot / (norm_a * norm_b)

def retrieve(query, top_n=3):
    query_embedding = embedder.encode(query)
    similarities = []
    for chunk, embedding in VECTOR_DB:
        sim = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, sim))
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]

input_query = input('Ask me a question: ')
retrieved_knowledge = retrieve(input_query)

print('Retrieved knowledge:')
for chunk, similarity in retrieved_knowledge:
    print(f' - (similarity: {similarity:.2f}) {chunk.strip()}')

# Now, for local LLM generation using llama-cpp-python
llm = Llama(model_path='./models/mistral-7b-instruct-v0.1.Q4_K_M.gguf')

instruction_prompt = f"""You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up new information:
{''.join(['- ' + chunk for chunk, _ in retrieved_knowledge])}
"""

response = llm(instruction_prompt + '\nQuestion: ' + input_query, max_tokens=200)
print('\nChatbot response:')
print(response['choices'][0]['text'])
