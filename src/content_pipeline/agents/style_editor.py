import json
from pathlib import Path

from ..client import ContentClient


STYLE_EDITOR_SYSTEM = """당신은 브랜드 톤/말투 전문 에디터예요.
콘텐츠가 브랜드 스타일 가이드에 맞는지 검수하고, 피드백을 제공해주세요.

검수 기준:
1. 말투: ~해요/~네요/~어요 구어체가 일관되게 사용되었는가
2. 금지 표현: ~다/함/임 체가 사용되지 않았는가 (인용문 제외)
3. 톤: "친절한 사수"처럼 전문적이면서 따뜻한 느낌이 나는가
4. 인사이트: 단순 요약이 아닌 실무자 관점의 인사이트가 포함되어 있는가
5. 문체 일관성: 글 샘플과 비교했을 때 문체가 자연스러운가

반드시 아래 JSON 형식으로만 응답해주세요:
{
  "passed": true 또는 false,
  "tone_score": 1~10 사이 정수,
  "forbidden_found": ["발견된 금지 표현 1", "발견된 금지 표현 2"],
  "insight_included": true 또는 false,
  "feedback": "Writer에게 전달할 톤/말투 수정 피드백 (passed가 false일 때)"
}"""


class StyleResult:
    def __init__(self, passed: bool, feedback: str, tone_score: int, forbidden_found: list[str]):
        self.passed = passed
        self.feedback = feedback
        self.tone_score = tone_score
        self.forbidden_found = forbidden_found


class StyleEditorAgent:
    """브랜드 톤/말투 검수를 담당하는 서브에이전트"""

    def review_style(
        self,
        client: ContentClient,
        content: str,
        brand_guide: str,
        writing_samples: str = "",
    ) -> StyleResult:
        samples_section = ""
        if writing_samples:
            samples_section = f"\n\n--- 글쓰기 샘플 (이 문체를 참고하세요) ---\n{writing_samples}"

        user_prompt = f"""아래 콘텐츠가 브랜드 스타일 가이드에 맞는지 검수해주세요.

--- 콘텐츠 ---
{content}

--- 브랜드 스타일 가이드 ---
{brand_guide}{samples_section}

위 가이드 기준으로 톤, 말투, 금지 표현, 실무 인사이트 포함 여부를 꼼꼼히 검수해주세요."""

        raw = client.generate(STYLE_EDITOR_SYSTEM, user_prompt)

        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            return StyleResult(
                passed=data.get("passed", True),
                feedback=data.get("feedback", ""),
                tone_score=data.get("tone_score", 7),
                forbidden_found=data.get("forbidden_found", []),
            )
        except (json.JSONDecodeError, KeyError):
            return StyleResult(passed=True, feedback="", tone_score=7, forbidden_found=[])

    def load_writing_samples(self, brand_dir: Path) -> str:
        """글쓰기 샘플 파일 로드"""
        samples_file = brand_dir / "writing-samples.md"
        if samples_file.exists():
            return samples_file.read_text(encoding="utf-8")
        return ""

    def save_approved_sample(self, content: str, platform: str, references_dir: Path) -> Path:
        """검증 통과된 콘텐츠를 레퍼런스에 자동 축적"""
        references_dir.mkdir(parents=True, exist_ok=True)

        # 기존 샘플 수 확인해서 번호 부여
        existing = list(references_dir.glob(f"{platform}_*.md"))
        num = len(existing) + 1
        sample_path = references_dir / f"{platform}_{num:03d}.md"
        sample_path.write_text(content, encoding="utf-8")
        return sample_path
