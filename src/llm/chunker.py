"""
Intelligent Chunking Engine for LLM Payload Truncation (413 Payload Too Large Prevention).
Splits oversized HTML/DOM trees and raw text documents into semantically dense chunks
preserving key headers, structural meta tags, and high-density entity sections.
"""

from typing import List
import re

class SemanticChunker:
    def __init__(self, max_chunk_tokens: int = 3500, est_chars_per_token: float = 4.0):
        self.max_chunk_chars = int(max_chunk_tokens * est_chars_per_token)

    def chunk_document(self, text: str) -> List[str]:
        """
        Splits text into semantically dense chunks small enough to fit within LLM context windows.
        Prioritizes splits at section headers, paragraphs, or sentence boundaries.
        """
        if not text:
            return []

        text = text.strip()
        if len(text) <= self.max_chunk_chars:
            return [text]

        chunks = []
        # Split by double newlines or structural headers (<h1-h6>, markdown #)
        sections = re.split(r'\n{2,}|(?=<h[1-6]>)|(?=\n#+ )', text)

        current_chunk = []
        current_len = 0

        for sec in sections:
            sec_len = len(sec)
            if current_len + sec_len <= self.max_chunk_chars:
                current_chunk.append(sec)
                current_len += sec_len
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_len = 0
                
                # If individual section is larger than max_chunk_chars, split by lines/sentences
                if sec_len > self.max_chunk_chars:
                    sub_sentences = re.split(r'(?<=[.!?])\s+', sec)
                    sub_chunk = []
                    sub_len = 0
                    for sent in sub_sentences:
                        if sub_len + len(sent) <= self.max_chunk_chars:
                            sub_chunk.append(sent)
                            sub_len += len(sent)
                        else:
                            if sub_chunk:
                                chunks.append(" ".join(sub_chunk))
                            sub_chunk = [sent]
                            sub_len = len(sent)
                    if sub_chunk:
                        chunks.append(" ".join(sub_chunk))
                else:
                    current_chunk.append(sec)
                    current_len = sec_len

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def truncate_payload(self, text: str, max_chars: int = 12000) -> str:
        """
        Quick truncation helper retaining head and tail context if document exceeds threshold.
        """
        if len(text) <= max_chars:
            return text
        
        half = max_chars // 2 - 100
        head = text[:half]
        tail = text[-half:]
        return f"{head}\n\n[... PAYLOAD TRUNCATED TO PREVENT 413 ERROR ...]\n\n{tail}"
