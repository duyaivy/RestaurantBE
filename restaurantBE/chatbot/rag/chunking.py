import re
from typing import List


class TextChunkingService:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\u00a0", " ")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def split_text(self, text: str) -> List[str]:
        text = self.normalize_text(text)
        if not text:
            return []

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            candidate = (
                f"{current_chunk}\n\n{paragraph}".strip()
                if current_chunk
                else paragraph
            )

            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
                continue

            if current_chunk:
                chunks.append(current_chunk)

            # nếu 1 paragraph quá dài thì cắt cứng
            if len(paragraph) > self.chunk_size:
                chunks.extend(self._split_long_text(paragraph))
                current_chunk = ""
            else:
                current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return self._apply_overlap(chunks)

    def _split_long_text(self, text: str) -> List[str]:
        parts = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            parts.append(text[start:end].strip())
            if end >= text_length:
                break
            start = max(0, end - self.chunk_overlap)

        return [part for part in parts if part]

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        if not chunks:
            return []

        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped_chunks.append(chunk)
                continue

            prev_chunk = chunks[i - 1]
            overlap_text = (
                prev_chunk[-self.chunk_overlap :]
                if len(prev_chunk) > self.chunk_overlap
                else prev_chunk
            )
            merged = f"{overlap_text}\n\n{chunk}".strip()

            if len(merged) > self.chunk_size + self.chunk_overlap:
                merged = merged[-(self.chunk_size + self.chunk_overlap) :]

            overlapped_chunks.append(merged)

        return overlapped_chunks
