"""
RAG Pipeline
Enhanced chunking with token-aware splitting, rich metadata, and JSONL export.
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def count_tokens(text: str) -> int:
    """Estimate token count (rough: ~4 chars per token)."""
    return len(text) // 4


@dataclass
class Chunk:
    """A single RAG chunk with rich metadata."""
    chunk_id: str
    source_file: str
    chunk_index: int
    header: str
    header_path: str
    content: str
    level: int
    token_count: int
    char_count: int
    prev_header: str
    next_header: str
    tags: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_jsonl_line(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class RAGPipeline:
    """Enhanced RAG pipeline with header-based chunking and rich metadata."""

    def __init__(
        self,
        chunk_level: int = 2,
        overlap: int = 50,
        max_tokens: int = 512,
    ):
        self.chunk_level = chunk_level
        self.overlap = overlap
        self.max_tokens = max_tokens

    def chunk(self, markdown: str, source_file: str) -> list[Chunk]:
        """
        Split markdown into chunks by headers.

        Args:
            markdown: Markdown text content
            source_file: Source file name for metadata

        Returns:
            List of Chunk objects
        """
        lines = markdown.splitlines(keepends=True)
        chunks: list[Chunk] = []

        header_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
        headers: list[tuple[int, int, str, str]] = []  # (line_idx, level, text, path)

        for i, line in enumerate(lines):
            m = header_pattern.match(line.strip())
            if m:
                level = len(m.group(1))
                text = m.group(2).strip()
                if level <= self.chunk_level:
                    path_parts = [h[2] for h in headers if h[3]]
                    path_parts.append(text)
                    header_path = " > ".join(path_parts)
                    headers.append((i, level, text, header_path))

        if not headers:
            token_count = count_tokens(markdown)
            return [
                Chunk(
                    chunk_id=str(uuid.uuid4())[:8],
                    source_file=source_file,
                    chunk_index=0,
                    header="",
                    header_path="",
                    content=markdown.strip(),
                    level=0,
                    token_count=token_count,
                    char_count=len(markdown),
                    prev_header="",
                    next_header="",
                    tags=[],
                )
            ]

        for idx, (line_idx, level, header_text, header_path) in enumerate(headers):
            start = line_idx
            end = headers[idx + 1][0] if idx + 1 < len(headers) else len(lines)
            content = "".join(lines[start:end]).strip()
            token_count = count_tokens(content)
            prev_header = headers[idx - 1][2] if idx > 0 else ""
            next_header = headers[idx + 1][2] if idx + 1 < len(headers) else ""
            tags = self._extract_tags(header_path, content)

            chunks.append(Chunk(
                chunk_id=str(uuid.uuid4())[:8],
                source_file=source_file,
                chunk_index=idx,
                header=header_text,
                header_path=header_path,
                content=content,
                level=level,
                token_count=token_count,
                char_count=len(content),
                prev_header=prev_header,
                next_header=next_header,
                tags=tags,
            ))

        return chunks

    def _extract_tags(self, header_path: str, content: str) -> list[str]:
        """Extract tags from header path and content."""
        tags: list[str] = []
        words = re.findall(r"[a-zA-Z]{4,}", header_path.lower())
        common = {"about", "after", "again", "also", "back", "been", "before", "being",
                  "between", "both", "each", "from", "have", "here", "into", "more",
                  "most", "other", "some", "such", "than", "that", "their", "them",
                  "then", "there", "these", "they", "this", "those", "through",
                  "under", "until", "very", "were", "what", "when", "where",
                  "which", "while", "will", "with", "your"}
        words = [w for w in words if w not in common]
        tags.extend(words[:5])
        return list(dict.fromkeys(tags))

    def generate_metadata(
        self,
        markdown: str,
        source_file: str,
        chunks: Optional[list[Chunk]] = None,
        ai_summary: Optional[str] = None,
        keywords: Optional[list[str]] = None,
    ) -> dict:
        """Generate metadata dict for YAML frontmatter."""
        total_tokens = sum(c.token_count for c in chunks) if chunks else count_tokens(markdown)
        lang = "vi"
        if chunks:
            sample = " ".join(c.content[:500] for c in chunks[:3])
            if re.search(r"[a-zA-Z]{20,}", sample):
                lang = "en"
        doc_type = self._detect_doc_type(markdown)

        metadata: dict = {
            "source_file": source_file,
            "converted_at": datetime.now(timezone.utc).isoformat(),
            "total_chunks": len(chunks) if chunks else 0,
            "total_tokens": total_tokens,
        }
        if ai_summary:
            metadata["ai_summary"] = ai_summary
        if keywords:
            metadata["ai_keywords"] = keywords
        if doc_type:
            metadata["document_type"] = doc_type
        metadata["language"] = lang
        return metadata

    def _detect_doc_type(self, markdown: str) -> str:
        """Auto-detect document type from content patterns."""
        lower = markdown.lower()
        if re.search(r"(báo cáo|tài chính|doanh thu|lợi nhuận|quý|năm)", lower):
            return "financial-report"
        if re.search(r"(hợp đồng|điều khoản|bên A|bên B|thanh toán)", lower):
            return "contract"
        if re.search(r"(biên bản|cuộc họp|đại biểu|chủ trì)", lower):
            return "meeting-minutes"
        if re.search(r"(đề xuất|dự án|ngân sách|triển khai)", lower):
            return "proposal"
        if re.search(r"(hướng dẫn|sử dụng|cài đặt|cấu hình)", lower):
            return "guide"
        return "document"

    def save_jsonl(self, chunks: list[Chunk], output_path: str) -> None:
        """Save chunks to a .jsonl file."""
        with open(output_path, "w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(chunk.to_jsonl_line() + "\n")
        logger.info(f"Saved {len(chunks)} chunks to {output_path}")

    def generate_yaml_frontmatter(self, metadata: dict) -> str:
        """Generate YAML frontmatter string from metadata dict."""
        lines = ["---"]
        for key, value in metadata.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, str) and "\n" in value:
                lines.append(f"{key}: |")
                for ln in value.splitlines():
                    lines.append(f"  {ln}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---")
        return "\n".join(lines)
