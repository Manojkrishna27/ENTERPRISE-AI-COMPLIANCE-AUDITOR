# Known Limitations & Roadmap

**Project**: Enterprise AI Compliance & Contract Auditor  

---

## 📌 Current Operational Considerations

1. **OCR for Scanned PDF Files**: Text extraction relies on PyMuPDF text streams. Scanned raster PDF documents without OCR text layers require Tesseract OCR pre-processing.
2. **File Size Limit**: Default file upload limit is set to 50MB per document (configurable via `MAX_CONTENT_LENGTH`).
3. **AI Rate Limits**: High-frequency concurrent contract analysis is bounded by Google Gemini / OpenAI API rate limits.
4. **Air-Gapped Deployment**: Public cloud LLMs (Gemini/OpenAI) require outbound HTTPS internet connectivity; air-gapped enterprise deployments require self-hosted Ollama/vLLM endpoints.
