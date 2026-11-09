import re
from typing import List, Dict, Any

class PolicyChunker:
    """Chunks merchant policy documents into semantically coherent sections."""

    @staticmethod
    def chunk_document(content: str, merchant_id: str, title: str) -> List[Dict[str, Any]]:
        # Split by markdown headers or numbered sections
        sections = re.split(r'\n(?=#{1,3}\s|\d+\.\s)', content)
        chunks = []

        for idx, sec in enumerate(sections):
            clean_sec = sec.strip()
            if not clean_sec:
                continue

            # Extract section title from first line
            lines = clean_sec.split('\n')
            first_line = lines[0].strip('# .')
            section_title = first_line[:100] if first_line else f"Section {idx+1}"

            # Basic keyword detection for rules
            lower = clean_sec.lower()
            detected_window = None
            window_match = re.search(r'(\d+)\s*days?', lower)
            if window_match:
                detected_window = int(window_match.group(1))

            chunks.append({
                "merchant_id": merchant_id,
                "section_title": section_title,
                "content": clean_sec,
                "metadata": {
                    "policy_title": title,
                    "section_index": idx,
                    "return_window_days": detected_window or 30,
                    "mentions_damage": "damage" in lower or "defect" in lower,
                    "mentions_refund": "refund" in lower
                }
            })

        return chunks

policy_chunker = PolicyChunker()
