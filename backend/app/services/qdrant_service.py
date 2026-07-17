import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.config import Config
from app.services.openai_service import openai_service

class QdrantService:
    def __init__(self):
        self.host = Config.QDRANT_HOST
        self.port = Config.QDRANT_PORT
        self.collection_name = "policy_chunks"
        
        self.client = None
        self.fallback_db = {}  # In-memory vector database fallback
        
        try:
            # Initialize Qdrant Client
            self.client = QdrantClient(host=self.host, port=self.port)
            self._ensure_collection_exists()
        except Exception as e:
            print(f"Could not connect to Qdrant at {self.host}:{self.port} - {e}. Using in-memory fallback vector DB.")
            self.client = None

    def _ensure_collection_exists(self):
        """
        Creates the policy_chunks collection if it doesn't already exist.
        """
        if not self.client:
            return
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=1536,  # 1536 dims for text-embedding-3-small
                        distance=qmodels.Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"Error checking/creating Qdrant collection: {e}. Falling back to memory.")
            self.client = None

    def index_policy_chunks(self, policy_id, chunks):
        """
        Takes list of PolicyChunk database objects, generates embeddings,
        and indexes them in Qdrant (or fallback memory).
        """
        points = []
        for idx, chunk in enumerate(chunks):
            # Generate embedding vector
            embedding = openai_service.get_embedding(chunk.chunk_text)
            
            qdrant_uuid = chunk.qdrant_id or str(uuid.uuid4())
            chunk.qdrant_id = qdrant_uuid  # sync back to database
            
            payload = {
                "policy_id": policy_id,
                "text": chunk.chunk_text,
                "page_number": chunk.page_number,
                "paragraph_number": chunk.paragraph_number,
                "chunk_position": chunk.chunk_position
            }
            
            if self.client:
                points.append(
                    qmodels.PointStruct(
                        id=qdrant_uuid,
                        vector=embedding,
                        payload=payload
                    )
                )
            else:
                # Store in-memory
                self.fallback_db[qdrant_uuid] = {
                    "vector": embedding,
                    "payload": payload
                }
                
        if self.client and points:
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                print(f"Indexed {len(points)} chunks in Qdrant for policy {policy_id}")
            except Exception as e:
                print(f"Failed upsert to Qdrant: {e}. Indexing to memory instead.")
                for point in points:
                    self.fallback_db[point.id] = {
                        "vector": point.vector,
                        "payload": point.payload
                    }

    def search_policy_chunks(self, query_text, limit=3):
        """
        Searches compliance policies for text relevant to the query.
        Returns a list of payload dicts with a similarity 'score'.
        """
        query_embedding = openai_service.get_embedding(query_text)
        
        if self.client:
            try:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit
                )
                
                formatted_results = []
                for res in results:
                    payload = res.payload
                    payload['score'] = res.score
                    payload['policy_id'] = payload.get('policy_id')
                    formatted_results.append(payload)
                return formatted_results
            except Exception as e:
                print(f"Qdrant search failed: {e}. Falling back to memory search.")
                
        # In-memory cosine similarity search
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
            sim = cosine_similarity(query_embedding, data["vector"])
            payload = data["payload"].copy()
            payload["score"] = sim
            results.append(payload)

        # Sort by similarity score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def delete_policy_chunks(self, policy_id):
        """
        Deletes indexed chunks associated with a policy.
        """
        if self.client:
            try:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="policy_id",
                                match=qmodels.MatchValue(value=policy_id)
                            )
                        ]
                    )
                )
                print(f"Deleted Qdrant chunks for policy {policy_id}")
                return True
            except Exception as e:
                print(f"Error deleting chunks from Qdrant: {e}")
                
        # Local memory delete
        keys_to_delete = [k for k, v in self.fallback_db.items() if v["payload"]["policy_id"] == policy_id]
        for k in keys_to_delete:
            del self.fallback_db[k]
        return True

# Export instantiated service
qdrant_service = QdrantService()
