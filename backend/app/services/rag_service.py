from app.services.providers.factory import llm_provider
from app.utils.logger import rag_logger
from app.ai_config import ai_config

class RAGService:
    def _rerank_chunks(self, chunks):
        """
        Simple re-ranking based on retrieval scores.
        Qdrant already returns sorted by score, but this explicitly enforces
        the Top K highest relevance across sources if merged.
        """
        return sorted(chunks, key=lambda x: x.get('score', 0.0), reverse=True)

    def analyze_contract_compliance(self, contract_name, contract_chunks, policy_chunks):
        """
        Calls LLM to audit retrieved contract chunks against policy chunks.
        Returns the structured JSON with compliance score and citations.
        """
        # Re-rank and take top
        top_contract_chunks = self._rerank_chunks(contract_chunks)[:10]
        top_policy_chunks = self._rerank_chunks(policy_chunks)[:10]
        
        contract_context = ""
        for cc in top_contract_chunks:
            contract_context += f"[Chunk ID: {cc.get('id')}] Contract Page {cc.get('page_number')}, Para {cc.get('paragraph_number')}:\n{cc.get('text')}\n\n"
            
        policy_context = ""
        for pc in top_policy_chunks:
            policy_context += f"[Chunk ID: {pc.get('id')}] Policy Page {pc.get('page_number')}, Para {pc.get('paragraph_number')}:\n{pc.get('text')}\n\n"

        system_prompt = """
You are a Principal AI Enterprise Compliance Auditor.
Analyze the following Contract against the retrieved Company Policies.
You MUST output ONLY valid JSON matching the exact schema provided.
Never hallucinate evidence. If evidence is missing, state it.

SCHEMA:
{
  "summary": "High level summary of compliance",
  "findings": [
    {
      "severity": "HIGH", // or MEDIUM, LOW
      "title": "Short title",
      "description": "Detailed explanation",
      "category": "GDPR / Security / Financial etc",
      "business_impact": "Impact description",
      "recommendation": "Actionable fix",
      "confidence": 0.95,
      "contract_citation": {
        "page": 0,
        "paragraph": 0,
        "chunk_id": "Exact chunk ID from context"
      },
      "policy_citation": {
        "page": 0,
        "paragraph": 0,
        "chunk_id": "Exact chunk ID from context"
      }
    }
  ],
  "compliance_score": 85, // 0 to 100
  "confidence": 0.95
}
"""

        user_prompt = f"""
CONTRACT NAME: {contract_name}

RETRIEVED CONTRACT CONTEXT:
{contract_context if contract_context else "None retrieved."}

RETRIEVED POLICY CONTEXT:
{policy_context if policy_context else "None retrieved."}

Identify violations, missing clauses, or risks.
"""
        rag_logger.info("Executing contract compliance analysis LLM call", extra={
            "rag_metrics": {
                "action": "llm_generation",
                "contract": contract_name,
                "provider": ai_config.provider,
                "model": ai_config.chat_model,
                "retrieved_contract_chunks": len(top_contract_chunks),
                "retrieved_policy_chunks": len(top_policy_chunks)
            }
        })
        return llm_provider.generate_json_response(system_prompt, user_prompt)

    def copilot_answer(self, query, contract_name, contract_chunks, policy_chunks, retrieval_metrics=None):
        """
        Answers user questions with citations, using strict retrieval and re-ranking.
        """
        # Enforce Top 5
        top_contract_chunks = self._rerank_chunks(contract_chunks)[:5]
        top_policy_chunks = self._rerank_chunks(policy_chunks)[:5]
        
        contract_context = ""
        for cc in top_contract_chunks:
            contract_context += f"[Chunk ID: {cc.get('id')}] Contract Page {cc.get('page_number')}, Para {cc.get('paragraph_number')}:\n{cc.get('text')}\n\n"
            
        policy_context = ""
        for pc in top_policy_chunks:
            policy_context += f"[Chunk ID: {pc.get('id')}] Policy Page {pc.get('page_number')}, Para {pc.get('paragraph_number')}:\n{pc.get('text')}\n\n"

        system_prompt = """
You are an enterprise compliance auditor and RAG AI assistant.
Answer ONLY using the retrieved context provided below.
If the evidence is insufficient to answer the question, explicitly state:
"I could not find sufficient evidence in the uploaded documents."
Never hallucinate.

Return your response using the following structure:
Summary: <Brief summary>
Findings: <Key points>
Risk: <Risk assessment>
Recommendation: <Actionable advice>
Citations: <List exact page, paragraph, and Chunk IDs cited from Contract and Policy>
"""

        user_prompt = f"""
Answer the following question about the contract: "{contract_name}".

QUESTION:
"{query}"

RETRIEVED CONTRACT CHUNKS:
{contract_context if contract_context else "None retrieved."}

RETRIEVED COMPANY POLICIES:
{policy_context if policy_context else "None retrieved."}
"""
        rag_logger.info("Executing Copilot LLM generation", extra={
            "rag_metrics": {
                "action": "llm_generation",
                "query": query,
                "provider": ai_config.provider,
                "model": ai_config.chat_model,
                "retrieved_contract_chunks": len(top_contract_chunks),
                "retrieved_policy_chunks": len(top_policy_chunks)
            }
        })
        result = llm_provider.generate_chat_response(system_prompt, user_prompt, temperature=0.1)
        
        if retrieval_metrics:
            result.update(retrieval_metrics)
            
        return result

rag_service = RAGService()
