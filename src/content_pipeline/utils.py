import re
from datetime import datetime
from pathlib import Path


def slugify(text: str, max_length: int = 30) -> str:
    """한국어 텍스트를 파일명에 안전한 슬러그로 변환"""
    slug = re.sub(r"[^\w가-힣\s-]", "", text)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:max_length].rstrip("-")


def today_str() -> str:
    return datetime.now().strftime("%Y%m%d")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_brand_context(brand_dir: Path) -> str:
    """assets/brand/ 디렉토리의 모든 .md 파일을 읽어 합침"""
    if not brand_dir.exists():
        return ""
    parts = []
    for md_file in sorted(brand_dir.glob("*.md")):
        parts.append(md_file.read_text(encoding="utf-8"))
    return "\n\n".join(parts)
