from pathlib import Path
import os

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

POLICY_FILE = BASE_DIR / "hr_policies.txt"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

# ChromaDB
chroma_client = chromadb.PersistentClient(
    path=str(VECTOR_DB_DIR)
)

collection = chroma_client.get_or_create_collection(
    name="hr_policies"
)


def generate_embedding(text):
    """Generate an embedding for the given text using Gemini."""

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT"
        )
    )

    return response.embeddings[0].values


def load_policy_chunks():
    """Load HR policies and divide them into sections."""

    if not POLICY_FILE.exists():
        raise FileNotFoundError("hr_policies.txt not found.")

    text = POLICY_FILE.read_text(encoding="utf-8")

    sections = [
        section.strip()
        for section in text.split("\n\n")
        if section.strip()
    ]

    return sections


def build_vector_database():
    """Convert HR policy sections into embeddings and store them."""

    sections = load_policy_chunks()

    # Clear previous records if rebuilding
    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    for index, section in enumerate(sections):

        embedding = generate_embedding(section)

        collection.add(
            ids=[f"policy_{index}"],
            documents=[section],
            embeddings=[embedding],
            metadatas=[{
                "source": "hr_policies.txt"
            }]
        )

    return len(sections)


def search_hr_policy_rag(query: str) -> str:
    """Find the most relevant HR policies using semantic similarity."""
    top_k=2
    query_embedding = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    ).embeddings[0].values

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        return "No relevant HR policy information was found."

    return "\n\n".join(documents)