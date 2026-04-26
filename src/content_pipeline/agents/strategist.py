import json

from ..client import ContentClient


STRATEGIST_SYSTEM = """당신은 '커머스의 모든 것' 블로그의 콘텐츠 전략 기획자예요.
15년 경력 이커머스 전문가의 시각으로 주제를 분석하고, 실무자에게 실질적으로 도움이 되는 글 구조를 설계해요.

기획 기준:
1. 트렌드 적시성: 지금 다룰 가치가 있는 주제인지
2. 독자 니즈: 이커머스 실무자가 알고 싶어하는 내용인지
3. 차별화: "오, 이건 몰랐네" 포인트가 있는지
4. 데이터 기반: 수치와 팩트로 뒷받침 가능한지

아웃라인 설계 원칙:
- 도입: 독자의 관심을 끄는 훅 (수치 또는 질문)
- 본론: 현황 -> 원인 분석 -> 시사점 순서
- 결론: 실무자 관점 인사이트 + 전망

반드시 아래 JSON 형식으로만 응답해주세요:
{
  "topic_analysis": "주제 분석 결과 (2-3문장)",
  "target_audience": "타겟 독자 정의",
  "key_messages": ["핵심 메시지 1", "핵심 메시지 2", "핵심 메시지 3"],
  "content_outline": [
    {"section": "섹션명", "points": ["포인트1", "포인트2"]},
    {"section": "섹션명", "points": ["포인트1", "포인트2"]}
  ],
  "unique_angle": "차별화 관점 (실무자 인사이트, 1-2문장)",
  "data_points": ["참고자료에서 추출한 핵심 수치/팩트1", "수치/팩트2"]
}"""


class StrategyBrief:
    def __init__(
        self,
        topic_analysis: str,
        target_audience: str,
        key_messages: list[str],
        content_outline: list[dict],
        unique_angle: str,
        data_points: list[str],
    ):
        self.topic_analysis = topic_analysis
        self.target_audience = target_audience
        self.key_messages = key_messages
        self.content_outline = content_outline
        self.unique_angle = unique_angle
        self.data_points = data_points

    def to_prompt_text(self) -> str:
        """Writer 프롬프트에 포함할 텍스트 형식으로 변환"""
        lines = ["[기획 브리프]", ""]
        lines.append(f"주제 분석: {self.topic_analysis}")
        lines.append(f"타겟 독자: {self.target_audience}")
        lines.append(f"차별화 관점: {self.unique_angle}")
        lines.append("")

        lines.append("핵심 메시지:")
        for i, msg in enumerate(self.key_messages, 1):
            lines.append(f"  {i}. {msg}")
        lines.append("")

        lines.append("글 구조 (아웃라인):")
        for section in self.content_outline:
            lines.append(f"  · {section['section']}")
            for point in section.get("points", []):
                lines.append(f"    - {point}")
        lines.append("")

        if self.data_points:
            lines.append("핵심 수치/팩트:")
            for dp in self.data_points:
                lines.append(f"  · {dp}")

        return "\n".join(lines)


class StrategistAgent:
    """콘텐츠 주제 분석 및 글 구조 기획을 담당하는 서브에이전트"""

    def analyze(
        self,
        client: ContentClient,
        topic: str,
        reference: str,
        platforms: list[str],
    ) -> StrategyBrief:
        platforms_str = ", ".join(platforms)
        user_prompt = f"""아래 주제와 참고자료를 바탕으로 콘텐츠 전략을 기획해주세요.

--- 주제 ---
{topic}

--- 대상 플랫폼 ---
{platforms_str}

--- 참고 자료 ---
{reference}

참고자료에서 핵심 수치와 팩트를 추출하고, 이커머스 실무자에게 가장 유용한 글 구조를 설계해주세요."""

        raw = client.generate(STRATEGIST_SYSTEM, user_prompt)

        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            return StrategyBrief(
                topic_analysis=data.get("topic_analysis", ""),
                target_audience=data.get("target_audience", ""),
                key_messages=data.get("key_messages", []),
                content_outline=data.get("content_outline", []),
                unique_angle=data.get("unique_angle", ""),
                data_points=data.get("data_points", []),
            )
        except (json.JSONDecodeError, KeyError):
            # 파싱 실패 시 빈 브리프 반환 (Writer가 기본 방식으로 진행)
            return StrategyBrief(
                topic_analysis="",
                target_audience="이커머스 실무자",
                key_messages=[],
                content_outline=[],
                unique_angle="",
                data_points=[],
            )
