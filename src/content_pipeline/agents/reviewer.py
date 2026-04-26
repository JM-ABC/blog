import json

from ..client import ContentClient


REVIEWER_SYSTEM = """당신은 콘텐츠 품질을 비판적으로 검토하는 에디터예요.
냉정하고 날카롭게 분석하되, 건설적인 피드백을 제공해주세요.

검토 기준:
1. 논리적 일관성: 주장과 근거가 논리적으로 연결되어 있는가
2. 팩트 정확성: 참고자료에 있는 수치/사실과 일치하는가
3. 과장/비약: 근거 없는 과장이나 논리적 비약이 있는가
4. 누락: 참고자료의 중요한 내용을 빠뜨리지 않았는가
5. 균형: 특정 관점에 지나치게 편향되지 않았는가

반드시 아래 JSON 형식으로만 응답해주세요:
{
  "passed": true 또는 false,
  "overall_comment": "전체적인 평가 한 줄",
  "fact_issues": ["팩트 오류 1", "팩트 오류 2"],
  "logic_issues": ["논리 문제 1", "논리 문제 2"],
  "suggestions": "Writer에게 전달할 수정 피드백 (passed가 false일 때)"
}"""


class ReviewResult:
    def __init__(self, passed: bool, feedback: str, fact_issues: list[str], logic_issues: list[str]):
        self.passed = passed
        self.feedback = feedback
        self.fact_issues = fact_issues
        self.logic_issues = logic_issues


class ReviewerAgent:
    """논리/팩트 검토를 담당하는 서브에이전트"""

    def review(
        self,
        client: ContentClient,
        content: str,
        reference: str,
        topic: str,
    ) -> ReviewResult:
        user_prompt = f"""아래 콘텐츠를 참고자료와 대조하여 검토해주세요.

--- 콘텐츠 ---
{content}

--- 참고 자료 ---
{reference}

--- 주제 ---
{topic}

위 콘텐츠에 팩트 오류, 논리적 비약, 과장된 표현이 있는지 꼼꼼히 검토해주세요."""

        raw = client.generate(REVIEWER_SYSTEM, user_prompt)

        try:
            # JSON 파싱 시도 (코드블록 제거)
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            return ReviewResult(
                passed=data.get("passed", True),
                feedback=data.get("suggestions", ""),
                fact_issues=data.get("fact_issues", []),
                logic_issues=data.get("logic_issues", []),
            )
        except (json.JSONDecodeError, KeyError):
            # 파싱 실패 시 통과 처리
            return ReviewResult(passed=True, feedback="", fact_issues=[], logic_issues=[])
