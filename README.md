# 🏥 MediSecure AI — Role-Aware Hybrid RAG System for Healthcare

## 📌 Overview

MediSecure AI is a **role-aware, retrieval-augmented healthcare assistant** designed to enable secure and intelligent interaction with Electronic Health Records (EHRs).

Unlike basic RAG systems, this project implements a **multi-stage hybrid retrieval pipeline with RBAC enforced at the ML layer**, ensuring both **accuracy and data privacy**.

The system supports:

* 👨‍⚕️ Doctors → cohort-level analysis and clinical summaries
* 🧑‍⚕️ Patients → simplified, personalized medical explanations

---

## ⚙️ Key Features

### 🔐 Role-Based Access Control (RBAC)

* Doctor → full dataset access
* Patient → strictly limited to own records
* Enforced inside the **retrieval pipeline**, not just API

---

### 🔍 Hybrid Retrieval System (Core Innovation)

A **multi-stage retrieval pipeline** combining:

* Semantic search (FAISS + Sentence-BERT)
* Structured metadata filtering (severity, admission type, etc.)
* Diagnosis-level semantic similarity
* Query-type adaptive retrieval

---

### 🧠 Query Understanding Layer

* Converts natural language → structured query
* Extracts:

  * diagnosis
  * patient name
  * severity level
  * admission type
* Enables **hybrid search (semantic + structured)**

---

### ⚡ Multi-Stage Ranking

* **Bi-Encoder (Sentence-BERT)** → fast candidate retrieval
* **Cross-Encoder** → precise reranking

Balances:

* speed ⚡
* accuracy 🎯

---

### 💬 Conversational Intelligence

* Query rewriting using chat history
* Session-based memory per user
* Supports follow-up questions

---

### 🤖 Role-Aware Response Generation

Different behaviors based on role:

* Doctor → structured clinical summaries
* Patient → simplified, easy-to-understand explanations

Also supports:

* count queries
* cohort queries
* summary queries

---

## 🏗️ System Architecture (V1)

```text
User Query
   ↓
Query Rewriting (chat memory)
   ↓
Query Understanding (intent extraction)
   ↓
Query Type Detection
   ↓
FAISS Vector Search (bi-encoder)
   ↓
RBAC Filtering (role-aware)
   ↓
Metadata Filtering (structured constraints)
   ↓
Candidate Selection
   ↓
Cross-Encoder Reranking
   ↓
Context Construction
   ↓
LLM Generation (role-aware prompts)
```

---

## 📂 Project Structure

```
src/
 ├── api/                # FastAPI endpoints + authentication (JWT-based)
 ├── retrieval/          # Hybrid search pipeline (FAISS + filtering + reranking)
 ├── llm/                # Query rewriting + answer generation
 ├── documents/          # Narrative construction from structured EHR data
 ├── embeddings/         # Vector index building
```

---

## 🧠 Design Highlights

* 🔹 **Separation of Concerns**

  * Query understanding, retrieval, and generation are modular

* 🔹 **Security at ML Layer**

  * RBAC enforced during retrieval (not post-processing)

* 🔹 **Hybrid Search**

  * Combines semantic + structured filtering

* 🔹 **Adaptive Retrieval Strategy**

  * Different pipelines for cohort vs specific queries

* 🔹 **Deterministic Query Rewriting**

  * Temperature = 0 for stable query transformations

---

## ⚠️ Current Limitations (V1)

This version is intentionally designed as a **retrieval-first system**, leading to:

* ❌ No true aggregation (counts are approximate)
* ❌ Limited dataset awareness (top-k retrieval only)
* ❌ No temporal reasoning (trends, timelines)
* ❌ Structured data is converted into narrative text
* ❌ In-memory chat history (not persistent)

---

## 🚀 Future Improvements (V2+)

* Hybrid SQL + RAG querying
* True aggregation engine (accurate counts, averages)
* Temporal reasoning (trends, progression analysis)
* Patient history tracking (multi-visit linking)
* Explainability layer for clinical validation

---

## 🧠 Tech Stack

* Python
* FastAPI
* FAISS
* Sentence-BERT
* Cross-Encoder (MS MARCO)
* OpenRouter (LLM API)
* dotenv (secure key management)

---

## 🎯 Why This Project Matters

Healthcare AI systems must balance:

* accuracy
* privacy
* interpretability

MediSecure AI explores how modern AI pipelines can achieve this by integrating:

* secure retrieval
* structured filtering
* role-aware generation

---