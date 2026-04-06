import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.retrieval.query_understanding import understand_query
from src.retrieval.query_type import detect_query_type


INDEX_PATH = "data/vector_store/faiss.index"
METADATA_PATH = "data/vector_store/metadata.npy"
DATA_PATH = "data/processed/admissions_rag_documents.json"


# ----------------------------
# MODELS
# ----------------------------

bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


# ----------------------------
# DATA
# ----------------------------

index = faiss.read_index(INDEX_PATH)

metadata = np.load(METADATA_PATH, allow_pickle=True)

with open(DATA_PATH) as f:
    documents = json.load(f)

# ----------------------------
# PRECOMPUTE DIAGNOSIS EMBEDDINGS
# ----------------------------

diagnosis_texts = [m["primary_diagnosis"] for m in metadata]

diagnosis_embeddings = bi_encoder.encode(
    diagnosis_texts,
    convert_to_numpy=True
)

# ----------------------------
# RBAC
# ----------------------------

def apply_rbac(indices, role, user_subject_id):

    allowed = []

    for idx in indices:

        meta = metadata[idx]

        if role == "doctor":
            allowed.append(idx)

        elif role == "patient":
            if meta["subject_id"] == user_subject_id:
                allowed.append(idx)

    return allowed


# ----------------------------
# METADATA FILTER
# ----------------------------

def metadata_filter(idx, parsed_query, query_diagnosis_emb=None):

    m = metadata[idx]

    patient = parsed_query.get("patient_name")
    severity = parsed_query.get("severity_level")
    admission = parsed_query.get("admission_type")
    diagnosis = parsed_query.get("diagnosis")

    if patient and m["patient_name"].lower() != patient.lower():
        return False

    if severity and m["severity_level"] != severity:
        return False

    if admission and m["admission_type"] != admission:
        return False

    if query_diagnosis_emb is not None:
        doc_emb = diagnosis_embeddings[idx]
        similarity = np.dot(query_diagnosis_emb, doc_emb)

        if similarity < 0.6:
            return False

    return True


# ----------------------------
# RERANK
# ----------------------------

def rerank(query, candidates):

    pairs = [(query, c["text"]) for c in candidates]

    scores = cross_encoder.predict(pairs)

    ranked = list(zip(scores, candidates))

    ranked.sort(key=lambda x: x[0], reverse=True)

    return [doc for score, doc in ranked]


# ----------------------------
# SEARCH
# ----------------------------

def search(query, role, user_subject_id=None, top_k=3):

    # Query understanding
    try:
        parsed_query = understand_query(query)
        rewritten_query = parsed_query.get("rewritten_query", query)

    except Exception:
        parsed_query = {}
        rewritten_query = query
    
    query_type = detect_query_type(query)

    query_diagnosis_emb = None
    if parsed_query.get("diagnosis"):
        query_diagnosis_emb = bi_encoder.encode(
            [parsed_query["diagnosis"]]
        )[0]
    # ----------------------------
    # PATIENT MODE (STRICT PERSONAL SEARCH)
    # ----------------------------

    if role == "patient":

        patient_indices = [
            i for i, m in enumerate(metadata)
            if m["subject_id"] == user_subject_id
        ]

        candidates = []

        for idx in patient_indices:

            candidates.append({
                "metadata": metadata[idx],
                "text": documents[idx]["page_content"]
            })

        # rerank ONLY within patient's own records
        reranked = rerank(rewritten_query, candidates)

        return reranked[:5]

    # Embedding
    query_embedding = bi_encoder.encode([rewritten_query]).astype("float32")
     

    # ----------------------------
    # VECTOR SEARCH
    # ----------------------------

    candidate_pool = 100 if query_type == "cohort" else 30

    distances, indices = index.search(query_embedding, candidate_pool)


    # ----------------------------
    # RBAC
    # ----------------------------

    allowed_indices = apply_rbac(indices[0], role, user_subject_id)


    # ----------------------------
    # METADATA FILTER + HYBRID SCORE
    # ----------------------------

    scored = []

    for idx, dist in zip(indices[0], distances[0]):

        if idx not in allowed_indices:
            continue

        if not metadata_filter(idx, parsed_query):
            continue

        text = documents[idx]["page_content"]

        semantic_score = -dist
        hybrid_score = semantic_score   
        scored.append((hybrid_score, idx))


    # ----------------------------
    # BUILD CANDIDATES
    # ----------------------------
    candidates = []

    limit = 30 if query_type == "cohort" else 10

    for score, idx in scored[:limit]:

        candidates.append({
            "metadata": metadata[idx],
            "text": documents[idx]["page_content"]
        })

    # ----------------------------
    # FALLBACK FOR LOW RECALL
    # ----------------------------

    if query_type == "cohort" and len(scored) < 5:

        distances, indices = index.search(query_embedding, 100)

        for idx, dist in zip(indices[0], distances[0]):

            if idx not in allowed_indices:
                continue

            if not metadata_filter(idx, parsed_query, query_diagnosis_emb):
                continue

            text = documents[idx]["page_content"]

            semantic_score = -dist
            hybrid_score = semantic_score
            scored.append((hybrid_score, idx))

    scored.sort(key=lambda x: x[0], reverse=True)
    # ----------------------------
    # CROSS ENCODER RERANK
    # ----------------------------

    reranked = rerank(rewritten_query, candidates)

    
    if query_type == "cohort":
            return reranked[:15]

    elif query_type == "comparison":
            return reranked[:8]

    else:
        return reranked[:top_k]