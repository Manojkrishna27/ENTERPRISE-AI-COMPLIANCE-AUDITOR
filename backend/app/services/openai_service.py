import os
import json
from openai import OpenAI
from app.config import Config

class OpenAIService:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.client = None
        self.is_gemini = False
        
        if self.api_key:
            self.api_key = self.api_key.strip()
            # Detect if it's a Gemini key (typically starts with AIzaSy or AQ...)
            if not self.api_key.startswith("sk-"):
                self.is_gemini = True
                
            try:
                if self.is_gemini:
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                    )
                    print("Initialized OpenAI client with Gemini compatibility layer.")
                else:
                    self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def get_embedding(self, text):
        """
        Generates text embedding using text-embedding-3-small (1536 dims).
        Returns a mock vector of floats if OpenAI client is not initialized or if using Gemini.
        """
        if not self.client or self.is_gemini:
            # Return a deterministic mock embedding vector of 1536 dimensions
            import random
            random.seed(hash(text))
            return [random.uniform(-1, 1) for _ in range(1536)]
            
        try:
            response = self.client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}. Falling back to mock vector.")
            import random
            random.seed(hash(text))
            return [random.uniform(-1, 1) for _ in range(1536)]

    def analyze_clause_against_policy(self, contract_chunk_text, contract_page, contract_para, policy_chunks):
        """
        Calls OpenAI/Gemini to audit a contract chunk against matching policy chunks.
        Returns a structured list of compliance findings or empty list if compliant.
        """
        if not self.client:
            return self._generate_mock_findings(contract_chunk_text, contract_page, contract_para, policy_chunks)

        policy_context = ""
        for pc in policy_chunks:
            policy_context += f"Policy: {pc.get('policy_name', 'Company Policy')} (Page {pc.get('page_number')}, Para {pc.get('paragraph_number')}):\n{pc.get('text')}\n\n"

        prompt = f"""
You are an expert AI Contract Auditor.
Analyze the following Contract Clause against the retrieved Company Policies.

CONTRACT CLAUSE (Page {contract_page}, Paragraph {contract_para}):
"{contract_chunk_text}"

RELEVANT COMPANY POLICIES:
{policy_context}

Identify if this contract clause violates, contradicts, or represents a compliance risk under any of the company policies.
Also look for:
- Missing clauses (e.g. missing GDPR clauses, liability limits)
- Weak wording
- Payment terms discrepancies
- Security requirements

Format your response as a JSON array of objects. If the clause complies fully and has no risk, return an empty array [].
Each object must have the following structure:
{{
    "category": "GDPR Violation" | "Security Risk" | "Payment Term" | "Liability Issue" | "Confidentiality" | "Weak Wording" | "Missing Clause" | "Vendor Risk",
    "risk_level": "High" | "Medium" | "Low",
    "title": "Short title of the finding",
    "explanation": "Detailed explanation of the issue",
    "business_impact": "Business impact of this clause/violation",
    "recommendation": "Actionable recommendation to fix the clause",
    "confidence_score": 0.0 to 1.0 (float),
    "policy_id": "ID of the policy violated (if any, copy from the context)",
    "policy_page_number": page number of the policy matching (integer),
    "policy_paragraph_number": paragraph number of the policy matching (integer),
    "matching_clause_text": "Exact quote from the contract clause that triggers this finding",
    "matching_policy_text": "Exact quote from the policy that is violated/matched"
}}
"""

        model_name = "gemini-1.5-flash" if self.is_gemini else "gpt-4o"
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional legal auditor that outputs JSON arrays of findings."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            content = response.choices[0].message.content
            # Parse the response, handling nested structures if LLM wraps it in a key
            data = json.loads(content)
            if isinstance(data, dict):
                # Look for list in dictionary keys
                for val in data.values():
                    if isinstance(val, list):
                        return val
                # If no list found, maybe the dict itself represents one finding or we wrap it
                return [data]
            return data
        except Exception as e:
            print(f"Error during OpenAI API call: {e}. Using mock findings.")
            return self._generate_mock_findings(contract_chunk_text, contract_page, contract_para, policy_chunks)

    def copilot_answer(self, query, contract_name, contract_chunks, policy_chunks):
        """
        Uses RAG to answer user questions about the contract with citations.
        """
        if not self.client:
            return self._generate_mock_copilot_response(query)

        context_contract = "\n".join([f"Contract Page {c['page_number']}, Para {c['paragraph_number']}: {c['text']}" for c in contract_chunks[:15]])
        context_policy = "\n".join([f"Policy '{p.get('policy_name')}' Page {p.get('page_number')}, Para {p.get('paragraph_number')}: {p.get('text')}" for p in policy_chunks[:5]])

        prompt = f"""
You are an AI Contract Copilot assisting a compliance officer.
Answer the following question about the contract: "{contract_name}".

QUESTION:
"{query}"

CONTRACT EXTRACTS:
{context_contract}

RELEVANT COMPANY POLICIES:
{context_policy}

Provide a concise, helpful answer.
Every finding or detail you mention MUST cite the page and paragraph numbers from the contract and/or policies.
Include a section at the end called "CITATIONS" listing each cited source as:
- Contract Page X, Paragraph Y
- Policy 'Name' Page A, Paragraph B
"""

        model_name = "gemini-1.5-flash" if self.is_gemini else "gpt-4o"
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful contract auditor. Always cite page and paragraph numbers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Copilot: {e}")
            return self._generate_mock_copilot_response(query)

    def _generate_mock_findings(self, contract_text, contract_page, contract_para, policy_chunks):
        """
        Fallback mock findings generator for demo mode.
        """
        findings = []
        text_lower = contract_text.lower()
        
        policy_id = policy_chunks[0].get('policy_id') if policy_chunks else None
        policy_page = policy_chunks[0].get('page_number', 1) if policy_chunks else 1
        policy_para = policy_chunks[0].get('paragraph_number', 1) if policy_chunks else 1
        matching_policy = policy_chunks[0].get('text', "Compliance policy guidelines") if policy_chunks else "Standard compliance guidelines"

        # Check for liability terms
        if 'liability' in text_lower or 'indemn' in text_lower:
            findings.append({
                "category": "Liability Issue",
                "risk_level": "High",
                "title": "Unlimited Liability Clause Detected",
                "explanation": "The contract contains language that could expose the company to unlimited liability or overly broad indemnification obligations, which contradicts our standard limit of liability policies.",
                "business_impact": "Potential catastrophic financial exposure in the event of a breach or litigation.",
                "recommendation": "Negotiate a liability cap equal to 12 months of fees paid under this agreement.",
                "confidence_score": 0.92,
                "policy_id": policy_id,
                "policy_page_number": policy_page,
                "policy_paragraph_number": policy_para,
                "matching_clause_text": contract_text[:150] + "...",
                "matching_policy_text": matching_policy[:150] + "..."
            })
            
        # Check for payment terms
        if 'payment' in text_lower or 'net 90' in text_lower or 'net 60' in text_lower:
            findings.append({
                "category": "Payment Term",
                "risk_level": "Medium",
                "title": "Non-Standard Payment Terms",
                "explanation": "The payment terms specify Net 60/Net 90, whereas company procurement guidelines mandate Net 30 terms.",
                "business_impact": "Negative impact on cash flow and working capital management.",
                "recommendation": "Amend the payment terms clause to Net 30.",
                "confidence_score": 0.88,
                "policy_id": policy_id,
                "policy_page_number": policy_page,
                "policy_paragraph_number": policy_para,
                "matching_clause_text": contract_text[:150] + "...",
                "matching_policy_text": matching_policy[:150] + "..."
            })

        # Check for GDPR/privacy
        if 'gdpr' in text_lower or 'personal data' in text_lower or 'privacy' in text_lower:
            findings.append({
                "category": "GDPR Violation",
                "risk_level": "High",
                "title": "Missing Standard Contractual Clauses (SCCs)",
                "explanation": "Cross-border data transfer details are mentioned without explicit reference to the Standard Contractual Clauses or adequate protection safeguards required by GDPR.",
                "business_impact": "Substantial regulatory fines (up to 4% of global turnover) and compliance investigations.",
                "recommendation": "Append GDPR Standard Contractual Clauses (SCCs) to the data processing agreement.",
                "confidence_score": 0.95,
                "policy_id": policy_id,
                "policy_page_number": policy_page,
                "policy_paragraph_number": policy_para,
                "matching_clause_text": contract_text[:150] + "...",
                "matching_policy_text": matching_policy[:150] + "..."
            })

        # Check for termination
        if 'terminate' in text_lower or 'convenience' in text_lower:
            findings.append({
                "category": "Vendor Risk",
                "risk_level": "Low",
                "title": "One-Sided Termination for Convenience",
                "explanation": "The vendor is allowed to terminate for convenience with 30 days notice, whereas the company does not have a matching reciprocal right.",
                "business_impact": "Operational disruption if the vendor terminates suddenly without cause.",
                "recommendation": "Make the termination for convenience clause reciprocal or increase the notice period to 90 days.",
                "confidence_score": 0.85,
                "policy_id": policy_id,
                "policy_page_number": policy_page,
                "policy_paragraph_number": policy_para,
                "matching_clause_text": contract_text[:150] + "...",
                "matching_policy_text": matching_policy[:150] + "..."
            })

        # Only add a "Weak Wording" finding if the clause text actually uses soft or ambiguous verbs
        if not findings:
            weak_words = ['reasonable', 'efforts', 'endeavor', 'approximate', 'suitable', 'appropriate', 'standard password']
            matched_word = next((w for w in weak_words if w in text_lower), None)
            
            if matched_word:
                findings.append({
                    "category": "Weak Wording",
                    "risk_level": "Low",
                    "title": f"Ambiguous Phrasing Detected ('{matched_word}')",
                    "explanation": f"The clause uses the soft qualifier '{matched_word}' instead of a binding commitment, making compliance verification and enforcement difficult.",
                    "business_impact": "Legal difficulty in holding the counterparty accountable to measurable metrics or strict audit obligations.",
                    "recommendation": f"Replace ambiguous phrasing with precise, measurable SLAs (e.g., replace '{matched_word} efforts' with binding commitments).",
                    "confidence_score": 0.75,
                    "policy_id": policy_id,
                    "policy_page_number": policy_page,
                    "policy_paragraph_number": policy_para,
                    "matching_clause_text": contract_text[:150] + "...",
                    "matching_policy_text": matching_policy[:150] + "..."
                })

        return findings

    def _generate_mock_copilot_response(self, query):
        q = query.lower()
        if "summary" in q or "summarize" in q:
            return """### Contract Summary

This agreement is a Standard Services Contract between the Company and the Vendor.
* **Effective Date**: January 1, 2026
* **Scope**: Information technology consulting and software deployment.
* **Payment Terms**: Net 60 days (Page 3, Paragraph 2) - **Warning**: Violates Company standard Net 30 policy.
* **Liability**: Uncapped liability for vendor breaches (Page 5, Paragraph 1).

### CITATIONS
* Contract Page 3, Paragraph 2
* Contract Page 5, Paragraph 1
"""
        elif "payment" in q:
            return """### Payment Terms

The payment terms are structured as **Net 60 days** from the invoice date (Contract Page 3, Paragraph 2). 

However, our internal **Procurement Guidelines** (Policy 'Vendor Guidelines' Page 2, Paragraph 1) require that all standard consulting service agreements adhere to **Net 30 days**.

### CITATIONS
* Contract Page 3, Paragraph 2
* Policy 'Vendor Guidelines' Page 2, Paragraph 1
"""
        elif "gdpr" in q or "privacy" in q:
            return """### GDPR & Privacy compliance

The contract references personal data processing on Page 4, Paragraph 3. However, there are several key issues:
1. **Missing Data Processing Addendum (DPA)**: A DPA is not attached or referenced.
2. **Standard Contractual Clauses (SCCs)**: Not present, which poses a compliance threat for cross-border data flows.

### CITATIONS
* Contract Page 4, Paragraph 3
* Policy 'GDPR' Page 12, Paragraph 4
"""
        else:
            return f"""Here is the information related to: "{query}".

Based on the contract text, the relevant clause appears on **Page 2, Paragraph 4** stating terms of service and execution. Under our **SOC2 Security Policies** (Policy 'SOC2 Compliance' Page 5, Paragraph 3), the vendor is required to submit annual audit reviews.

### CITATIONS
* Contract Page 2, Paragraph 4
* Policy 'SOC2 Compliance' Page 5, Paragraph 3
"""

openai_service = OpenAIService()
