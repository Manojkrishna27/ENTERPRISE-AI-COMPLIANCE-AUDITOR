import time
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.ai_config import ai_config
from app.config import Config
from app.services.providers.factory import embedding_provider
from app.utils.logger import rag_logger


class QdrantService:
    def __init__(self):
        self.host = Config.QDRANT_HOST
        self.port = Config.QDRANT_PORT

        self.policy_collection = ai_config.policies_collection
        self.contract_collection = ai_config.contracts_collection

        self.client = None
        self.fallback_db = {}  # In-memory vector database fallback

        try:
            # Initialize Qdrant Client
            self.client = QdrantClient(host=self.host, port=self.port)
            self._ensure_collection_exists(self.policy_collection)
            self._ensure_collection_exists(self.contract_collection)
        except Exception as e:
            print(
                f"Could not connect to Qdrant at {self.host}:{self.port} - {e}. Using in-memory fallback vector DB."
            )
            self.client = None

    def is_connected(self):
        return self.client is not None

    def _ensure_collection_exists(self, collection_name):
        if not self.client:
            return
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=ai_config.embedding_dimension,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                print(
                    f"Created Qdrant collection: {collection_name} with dim {ai_config.embedding_dimension}"
                )
        except Exception as e:
            print(
                f"Error checking/creating Qdrant collection {collection_name}: {e}. Falling back to memory."
            )
            self.client = None

    def index_policy_chunks(self, policy_id, chunks):
        points = []
        for chunk in chunks:
            embedding, _ = embedding_provider.get_embedding(chunk.chunk_text)
            qdrant_uuid = chunk.qdrant_id or str(uuid.uuid4())
            chunk.qdrant_id = qdrant_uuid

            payload = {
                "type": "policy",
                "policy_id": policy_id,
                "text": chunk.chunk_text,
                "page_number": chunk.page_number,
                "paragraph_number": chunk.paragraph_number,
                "chunk_position": chunk.chunk_position,
            }

            if self.client:
                points.append(
                    qmodels.PointStruct(
                        id=qdrant_uuid, vector=embedding, payload=payload
                    )
                )
            else:
                self.fallback_db[qdrant_uuid] = {
                    "vector": embedding,
                    "payload": payload,
                }

        if self.client and points:
            try:
                self.client.upsert(
                    collection_name=self.policy_collection, points=points
                )
                print(f"Indexed {len(points)} chunks in Qdrant for policy {policy_id}")
            except Exception as e:
                print(f"Failed upsert to Qdrant: {e}")

    def index_contract_chunks(self, version_id, chunks):
        points = []
        for chunk in chunks:
            embedding, _ = embedding_provider.get_embedding(chunk.chunk_text)
            qdrant_uuid = chunk.qdrant_id or str(uuid.uuid4())
            chunk.qdrant_id = qdrant_uuid

            payload = {
                "type": "contract",
                "version_id": version_id,
                "text": chunk.chunk_text,
                "page_number": chunk.page_number,
                "paragraph_number": chunk.paragraph_number,
                "chunk_position": chunk.chunk_position,
            }

            if self.client:
                points.append(
                    qmodels.PointStruct(
                        id=qdrant_uuid, vector=embedding, payload=payload
                    )
                )
            else:
                self.fallback_db[qdrant_uuid] = {
                    "vector": embedding,
                    "payload": payload,
                }

        if self.client and points:
            try:
                self.client.upsert(
                    collection_name=self.contract_collection, points=points
                )
                print(
                    f"Indexed {len(points)} chunks in Qdrant for contract version {version_id}"
                )
            except Exception as e:
                print(f"Failed upsert to Qdrant: {e}")

    def search_policy_chunks(self, query_text, limit=5, department_id=None):
        start_time = time.time()
        query_embedding, emb_latency = embedding_provider.get_embedding(query_text)

        filter_query = None
        if department_id:
            filter_query = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="department_id",
                        match=qmodels.MatchValue(value=department_id),
                    )
                ]
            )

        if self.client:
            try:
                results = self.client.search(
                    collection_name=self.policy_collection,
                    query_vector=query_embedding,
                    query_filter=filter_query,
                    limit=limit,
                )
                formatted = [
                    dict(res.payload, score=res.score, id=res.id) for res in results
                ]
                latency = time.time() - start_time
                self._log_retrieval(
                    "Policy", query_text, formatted, limit, latency, emb_latency
                )
                return formatted
            except Exception as e:
                print(f"Qdrant search failed: {e}. Falling back to memory search.")

        # Memory Fallback
        mem_filters = {}
        if department_id:
            mem_filters["department_id"] = department_id
        results = self._memory_search(
            query_embedding,
            "policy",
            limit,
            filters=mem_filters if mem_filters else None,
        )
        latency = time.time() - start_time
        self._log_retrieval(
            "Policy (Memory)", query_text, results, limit, latency, emb_latency
        )
        return results

    def search_contract_chunks(self, version_id, query_text, limit=5):
        start_time = time.time()
        query_embedding, emb_latency = embedding_provider.get_embedding(query_text)

        if self.client:
            try:
                results = self.client.search(
                    collection_name=self.contract_collection,
                    query_vector=query_embedding,
                    query_filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="version_id",
                                match=qmodels.MatchValue(value=version_id),
                            )
                        ]
                    ),
                    limit=limit,
                )
                formatted = [
                    dict(res.payload, score=res.score, id=res.id) for res in results
                ]
                latency = time.time() - start_time
                self._log_retrieval(
                    "Contract", query_text, formatted, limit, latency, emb_latency
                )
                return formatted
            except Exception as e:
                print(f"Qdrant search failed: {e}. Falling back to memory search.")

        # Memory Fallback
        results = self._memory_search(
            query_embedding, "contract", limit, {"version_id": version_id}
        )
        latency = time.time() - start_time
        self._log_retrieval(
            "Contract (Memory)", query_text, results, limit, latency, emb_latency
        )
        return results

    def _memory_search(self, query_embedding, chunk_type, limit, filters=None):
        import math

        def cosine_similarity(v1, v2):
            dot_product = sum(x * y for x, y in zip(v1, v2))
            norm_a = math.sqrt(sum(x * x for x in v1))
            norm_b = math.sqrt(sum(x * x for x in v2))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return dot_product / (norm_a * norm_b)

        results = []
        for qid, data in self.fallback_db.items():
            payload = data["payload"]
            if payload.get("type") != chunk_type:
                continue

            if filters:
                match = all(payload.get(k) == v for k, v in filters.items())
                if not match:
                    continue

            sim = cosine_similarity(query_embedding, data["vector"])
            p = payload.copy()
            p["score"] = sim
            p["id"] = qid
            results.append(p)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _log_retrieval(self, source, query, results, limit, latency, emb_latency):
        metrics = {
            "action": "retrieval",
            "source": source,
            "query": query,
            "limit": limit,
            "retrieval_latency": round(latency, 4),
            "embedding_latency": round(emb_latency, 4),
            "provider": ai_config.provider,
            "embedding_model": ai_config.embedding_model,
            "embedding_dimension": ai_config.embedding_dimension,
            "retrieved_count": len(results),
            "retrieved_chunk_ids": [r.get("id") for r in results],
            "similarity_scores": [round(r.get("score", 0), 4) for r in results],
        }
        rag_logger.info(
            f"Retrieved {len(results)} chunks from {source}",
            extra={"rag_metrics": metrics},
        )


qdrant_service = QdrantService()
