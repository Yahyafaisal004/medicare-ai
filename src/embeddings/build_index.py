import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os


DATA_PATH = "data/processed/admissions_rag_documents.json"
INDEX_SAVE_PATH = "data/vector_store/faiss.index"
METADATA_SAVE_PATH = "data/vector_store/metadata.npy"


def build_index():

    print("Loading JSON documents...")

    with open(DATA_PATH, "r") as f:
        documents = json.load(f)

    texts = [doc["page_content"] for doc in documents]
    metadata = [doc["metadata"] for doc in documents]

    print(f"Loaded {len(texts)} documents.")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    dimension = embeddings.shape[1]

    print("Building FAISS index...")
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    os.makedirs("data/vector_store", exist_ok=True)

    print("Saving FAISS index...")
    faiss.write_index(index, INDEX_SAVE_PATH)

    print("Saving metadata mapping...")
    np.save(METADATA_SAVE_PATH, metadata, allow_pickle=True)

    print("Index build complete.")


if __name__ == "__main__":
    build_index()
