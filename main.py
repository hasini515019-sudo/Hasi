from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
# main.py top
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


from transformers import pipeline

app = FastAPI()


# main.py

@app.get("/generate")
def generate_text(prompt: str = "Hello"):
    # Simple fake text generator
    generated = f"{prompt}... this is a generated response."
    return {"text": generated}

# Lightweight model
generator = pipeline("text-generation", model="distilgpt2")

@app.get("/generate")
def generate_text(prompt: str):
    # max_length small to save memory
    result = generator(prompt, max_length=50, num_return_sequences=1)
    return {"text": result[0]['generated_text']}
# Use lightweight model
generator = pipeline("text-generation", model="distilgpt2")

@app.get("/generate")
def generate_text(prompt: str):
    return generator(prompt, max_length=50)# ================== APP SETUP ==================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== INPUT MODEL ==================
class CodeRequest(BaseModel):
    code: str

# ================== LOCAL AI SETUP ==================
# Text generation using GPT-2 locally
generator = pipeline('text-generation', model='gpt2')

# Embedding model
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

# ================== KNOWLEDGE BASE ==================
documents = [
    "Use list comprehension instead of loops in Python",
    "Avoid nested loops to reduce time complexity",
    "Use dictionary (hashmap) for faster lookup",
    "Follow clean code principles",
    "Use meaningful variable names",
    "Avoid redundant computations",
    "Use built-in functions for efficiency"
]

# ================== CREATE EMBEDDINGS ==================
doc_embeddings = model.encode(documents)

# ================== VECTOR DATABASE (FAISS) ==================
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings).astype('float32'))

# ================== API ENDPOINT ==================
@app.post("/refactor")
def refactor_code(req: CodeRequest):
    # Step 1: Convert user code → embedding
    query_embedding = model.encode([req.code])

    # Step 2: Retrieve similar best practices
    D, I = index.search(np.array(query_embedding).astype('float32'), k=3)
    retrieved_docs = [documents[i] for i in I[0]]

    # Step 3: Create local prompt
    prompt = f"""
Analyze and refactor the following code using best practices:

CODE:
{req.code}

BEST PRACTICES:
{retrieved_docs}
"""

    # Step 4: Generate text locally (no API key needed)
    response = generator(prompt, max_length=200, num_return_sequences=1)

    # Step 5: Return result
    return {"result": response[0]['generated_text']}

# ================== ROOT ==================
@app.get("/")
def home():
    return {"message": "AI Code Refactor Backend Running 🚀"}