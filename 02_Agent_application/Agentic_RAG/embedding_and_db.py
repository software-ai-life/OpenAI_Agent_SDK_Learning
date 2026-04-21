from google import genai
import chromadb
from google.genai.types import EmbedContentConfig
from dotenv import load_dotenv
import os
import ssl
import requests
from agents.tool import function_tool

os.environ["CURL_CA_BUNDLE"] = ""
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Google GenAI client for RAG embedding/generation
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize ChromaDB in-memory client
chroma_client = chromadb.Client()

# Define and embed documents
documents = [
    "Cats are small, domesticated carnivorous mammals often valued by humans for companionship and for their ability to hunt vermin.",
    "Dogs are domesticated mammals, not natural wild animals. They were originally bred from wolves.",
    "The Apollo program was a series of space missions by NASA in the 1960s and 1970s aimed at landing humans on the Moon."
]
doc_ids = ["doc1", "doc2", "doc3"]
embed_model = "gemini-embedding-001" # Or whichever model you used

# Generate embeddings for all documents in one call
response = client.models.embed_content(
    model=embed_model,
    contents=documents,
    config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
)
doc_embeddings = [emb.values for emb in response.embeddings]

# Create or get the collection
collection = chroma_client.get_or_create_collection(name="knowledge_base1")

# Add documents, handling potential duplicates
try:
    collection.add(
        documents=documents,
        embeddings=doc_embeddings,
        ids=doc_ids
    )
except Exception as e:
    print(f"Could not add documents to collection, potentially they already exist: {e}")





@function_tool
def answer_from_knowledge_base(query: str) -> str:
    """
    Tool: Given a user query, this tool searches the knowledge base and returns an answer using retrieved documents.
    """
    # Embed the query
    q_resp = client.models.embed_content(
        model=embed_model,
        contents=[query],
        config=EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    q_vector = q_resp.embeddings[0].values
    # Search the vector store
    res = collection.query(query_embeddings=[q_vector], n_results=1, include=["documents"])
    top_doc = res["documents"][0][0]  # top result's text
    # Construct prompt with retrieved context
    prompt = f"Context:\n{top_doc}\n\nQuestion:\n{query}\n\nAnswer the question using only the context above."
    # Generate answer with Gemini 1.5 Flash
    resp = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return resp.text