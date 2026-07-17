import os
import fitz  # PyMuPDF
import docx
from flask import current_app

class DocumentParser:
    @staticmethod
    def parse_pdf(file_path):
        """
        Parses a PDF using PyMuPDF (fitz) and extracts text blocks,
        preserving page numbers and paragraph (block) numbers.
        """
        chunks = []
        doc = fitz.open(file_path)
        
        chunk_position = 0
        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            # "blocks" returns: (x0, y0, x1, y1, text, block_no, block_type)
            blocks = page.get_text("blocks")
            
            for block in blocks:
                text = block[4].strip()
                block_no = block[5]
                block_type = block[6]
                
                # Filter out image blocks (block_type == 1) or very short/whitespace blocks
                if block_type == 0 and text:
                    chunks.append({
                        "text": text,
                        "page_number": page_num,
                        "paragraph_number": block_no + 1,
                        "chunk_position": chunk_position
                    })
                    chunk_position += 1
                    
        doc.close()
        return chunks

    @staticmethod
    def parse_docx(file_path):
        """
        Parses a DOCX using python-docx and extracts paragraphs.
        Word files do not have rigid pages, so pages are simulated
        every 10 paragraphs.
        """
        chunks = []
        doc = docx.Document(file_path)
        
        chunk_position = 0
        for para_idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text:
                # Estimate a page number (every 10 paragraphs constitutes a page)
                simulated_page = (para_idx // 10) + 1
                chunks.append({
                    "text": text,
                    "page_number": simulated_page,
                    "paragraph_number": para_idx + 1,
                    "chunk_position": chunk_position
                })
                chunk_position += 1
                
        return chunks

    @classmethod
    def parse_document(cls, file_path, file_type):
        """
        Routes the document to the correct parser based on file type.
        """
        file_type = file_type.upper()
        if file_type == 'PDF':
            return cls.parse_pdf(file_path)
        elif file_type == 'DOCX' or file_type == 'DOC':
            return cls.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
current_parser = DocumentParser()
