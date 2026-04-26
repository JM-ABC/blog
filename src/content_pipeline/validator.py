import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    passed: bool = True
    issues: list[str] = field(default_factory=list)
    suggestions: str = ""


# 플랫폼별 검증 규칙
PLATFORM_RULES = {
    "instagram": {
        "min_length": 500,
        "max_length": 5000,
        "required_keywords": ["슬라이드", "캡션", "해시태그"],
        "min_keyword_counts": {"슬라이드": 7},
    },
    "reels": {
        "min_length": 400,
        "max_length": 4000,
        "required_keywords": ["화면:", "자막:"],
        "min_keyword_counts": {},
    },
    "linkedin": {
        "min_length": 800,
        "max_length": 2500,
        "required_keywords": [],
        "min_keyword_counts": {},
    },
    "blog": {
        "min_length": 1500,
        "max_length": 6000,
        "required_keywords": [],
        "min_keyword_counts": {},
    },
    "threads": {
        "min_length": 200,
        "max_length": 3000,
        "required_keywords": [],
        "min_keyword_counts": {},
    },
}

# 금지 패턴: 문장 끝의 ~다/함/임 체 (인용문 제외)
FORBIDDEN_ENDINGS = re.compile(
    r'(?<!["\'\u201c\u201d])(?:^|[.!?]\s)'
    r'[^.!?\n]*'
    r'(?:한다|했다|된다|됐다|이다|였다|있다|없다|같다|보인다|나타난다'
    r'|하였다|되었다|기록하였다|증가하였다|감소하였다'
    r'|하였음|되었음|했음|됨|함|임)\s*[.!?]?\s*$',
    re.MULTILINE,
)


def validate_schema(content: str, platform: str) -> list[str]:
    """1단계: 스키마 검증 - 필수 섹션 존재 여부"""
    issues = []
    rules = PLATFORM_RULES.get(platform, {})

    for keyword in rules.get("required_keywords", []):
        if keyword not in content:
            issues.append(f"필수 섹션 누락: '{keyword}'이(가) 콘텐츠에 없어요")

    min_counts = rules.get("min_keyword_counts", {})
    for keyword, min_count in min_counts.items():
        actual = content.count(keyword)
        if actual < min_count:
            issues.append(f"'{keyword}' 개수 부족: {actual}개 (최소 {min_count}개 필요)")

    return issues


def validate_rules(content: str, platform: str) -> list[str]:
    """2단계: 규칙 기반 검증 - 글자 수, 금지 표현"""
    issues = []
    rules = PLATFORM_RULES.get(platform, {})
    content_length = len(content)

    min_len = rules.get("min_length", 0)
    max_len = rules.get("max_length", 99999)

    if content_length < min_len:
        issues.append(f"글자 수 부족: {content_length}자 (최소 {min_len}자 필요)")

    if content_length > max_len:
        issues.append(f"글자 수 초과: {content_length}자 (최대 {max_len}자)")

    # 금지 표현 검출
    forbidden_matches = FORBIDDEN_ENDINGS.findall(content)
    if forbidden_matches:
        samples = forbidden_matches[:3]
        sample_text = " / ".join(s.strip()[-20:] for s in samples)
        issues.append(f"금지 표현(~다/함/임 체) 검출 {len(forbidden_matches)}건: ...{sample_text}")

    return issues


def validate_output(content: str, platform: str) -> ValidationResult:
    """통합 검증: 스키마 + 규칙 기반 (LLM 검증은 별도 호출)"""
    result = ValidationResult()

    if not content or not content.strip():
        result.passed = False
        result.issues.append("콘텐츠가 비어있어요")
        return result

    # 1단계: 스키마 검증
    schema_issues = validate_schema(content, platform)
    result.issues.extend(schema_issues)

    # 2단계: 규칙 기반 검증
    rule_issues = validate_rules(content, platform)
    result.issues.extend(rule_issues)

    # 이슈가 있으면 실패
    if result.issues:
        result.passed = False
        result.suggestions = build_feedback(result.issues, platform)

    return result


def build_feedback(issues: list[str], platform: str) -> str:
    """검증 실패 시 재생성용 피드백 텍스트 생성"""
    feedback_parts = [f"아래 {len(issues)}개 항목을 수정해서 다시 작성해주세요:"]
    for i, issue in enumerate(issues, 1):
        feedback_parts.append(f"  {i}. {issue}")

    feedback_parts.append("")
    feedback_parts.append("특히 말투는 반드시 ~해요/~네요/~어요 구어체를 사용하고,")
    feedback_parts.append("~다/함/임으로 끝나는 문장은 절대 쓰지 마세요.")
    feedback_parts.append("실무자 관점의 인사이트도 빠뜨리지 마세요.")

    return "\n".join(feedback_parts)
