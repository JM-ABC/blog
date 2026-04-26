from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    api_key: str
    model: str
    max_tokens: int
    project_root: Path
    assets_dir: Path
    output_dir: Path
    brand_dir: Path


def load_config(project_root: Path | None = None) -> Config:
    root = project_root or Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(
            "ANTHROPIC_API_KEY가 설정되지 않았습니다.\n"
            "1. .env.example 파일을 .env로 복사하세요\n"
            "2. .env 파일에 API 키를 입력하세요"
        )

    return Config(
        api_key=api_key,
        model=os.getenv("CONTENT_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=int(os.getenv("CONTENT_MAX_TOKENS", "4096")),
        project_root=root,
        assets_dir=root / "assets",
        output_dir=root / "output",
        brand_dir=root / "assets" / "brand",
    )
