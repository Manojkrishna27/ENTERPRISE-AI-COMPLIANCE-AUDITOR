# RAG Pipeline Workflow & Architecture

## Overview

The **Enterprise RAG (Retrieval-Augmented Generation) Pipeline** is designed for high-accuracy legal contract parsing, semantic comparison against corporate policies, and risk mitigation.

![RAG Pipeline Workflow](../screenshots/rag-workflow.png)

---

## ⚙️ Workflow Stages

### 1. Document Ingestion & Parsing
- **Format Support**: Accepts PDF and DOCX documents.
- **Parsing Engine**: `PyMuPDF` extracts clean text content preserving structure.
- **Semantic Chunking**: `LlamaIndex` sentence splitter breaks down documents into contextually rich, non-overlapping semantic blocks.

### 2. Embedding & Vector Indexing
- **Vector Model**: Matryoshka-optimized 768-dimensional embeddings via Google Gemini (`gemini-embedding-2`) / OpenAI provider adapters.
- **Vector Database**: `Qdrant` stores dense vector representations with rich metadata payloads (`document_id`, `department_id`, `chunk_index`, `page_num`).
- **Multi-Tenant Isolation**: Payload filtering guarantees `department_id` isolation during vector search.

### 3. Retrieval & Risk Analysis
- **Query Resolution**: Search queries and contract context are transformed into 768-dim embedding vectors.
- **Dual Vector Search**:
  1. Retrieve Top-K relevant contract chunks.
  2. Retrieve Top-K relevant corporate policy/standard chunks.
- **LLM Reasoning**: Prompts sent to Google Gemini (`gemini-1.5-flash`) / OpenAI for deep compliance scoring, missing clause detection, and automated risk breakdown.

---

## 📊 Sequence Diagram

The underlying execution flow is documented in PlantUML format:
See [`docs/diagrams/rag-workflow.puml`](./diagrams/rag-workflow.puml).
