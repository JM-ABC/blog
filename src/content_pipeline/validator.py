import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    passed: bool = True
    issues: list[str] = field(default_factory=list)
    suggestions: str = ""


# 플랫폼별 검증 규칙
# blog는 CLAUDE.md 규칙(20,000바이트 이상)에 맞춰 byte 단위로 측정하고,
# 나머지 플랫폼은 기존처럼 글자수(char) 단위로 측정한다.
PLATFORM_RULES = {
    "instagram": {
        "min_length": 500,
        "max_length": 5000,
        "length_unit": "char",
        "required_keywords": ["슬라이드", "캡션", "해시태그"],
        "min_keyword_counts": {"슬라이드": 7},
    },
    "reels": {
        "min_length": 400,
        "max_length": 4000,
        "length_unit": "char",
        "required_keywords": ["화면:", "자막:"],
        "min_keyword_counts": {},
    },
    "linkedin": {
        "min_length": 800,
        "max_length": 2500,
        "length_unit": "char",
        "required_keywords": [],
        "min_keyword_counts": {},
    },
    "blog": {
        "min_length": 20000,
        "max_length": 45000,
        "length_unit": "byte",
        "required_keywords": [],
        "min_keyword_counts": {},
    },
    "threads": {
        "min_length": 200,
        "max_length": 3000,
        "length_unit": "char",
        "required_keywords": [],
        "min_keyword_counts": {},
    },
}

# 금지 패턴: 문장 끝의 ~다/함/임 체 (인용문 제외) - 전 플랫폼 공통
FORBIDDEN_ENDINGS = re.compile(
    r'(?<!["\'“”])(?:^|[.!?]\s)'
    r'[^.!?\n]*'
    r'(?:한다|했다|된다|됐다|이다|였다|있다|없다|같다|보인다|나타난다'
    r'|하였다|되었다|기록하였다|증가하였다|감소하였다'
    r'|하였음|되었음|했음|됨|함|임)\s*[.!?]?\s*$',
    re.MULTILINE,
)

# 마크다운 기호 금지 - 전 에이전트, 전 플랫폼 공통, 절대 규칙 (CLAUDE.md 출력 형식 규칙 1번)
MARKDOWN_PATTERNS = {
    "헤딩(# ## ###)": re.compile(r'(?m)^\s{0,3}#{1,6}\s'),
    "볼드(** __)": re.compile(r'\*\*[^*\n]+\*\*|__[^_\n]+__'),
    "이탤릭(* _)": re.compile(r'(?<![\w*])\*[^*\n]+\*(?![\w*])|(?<![\w_])_[^_\n]+_(?![\w_])'),
    "불렛(-)": re.compile(r'(?m)^\s*-\s'),
    "인용(>)": re.compile(r'(?m)^\s*>\s'),
    "코드블록(```)": re.compile(r'```'),
    "테이블(| --- |)": re.compile(r'\|\s*-{2,}\s*\|'),
    "링크([텍스트](URL))": re.compile(r'\[[^\]\n]+\]\([^)\n]+\)'),
    "숫자나열(1. 2. 3.)": re.compile(r'(?m)^\s*\d+\.\s'),
    "구분선(--- / ━━━)": re.compile(r'(?m)^\s*(?:-{3,}|_{3,}|━{3,}|\*{3,})\s*$'),
}

# "~기사에 따르면" 류 간접 인용 서술어 금지 - 전 플랫폼 공통, 절대 규칙
INDIRECT_QUOTE_PATTERN = re.compile(r'기사에\s*따르면|기사에서는|보도에\s*따르면|에\s*의하면')

# 본문 내 괄호 출처 인용 금지 (출처는 하단 섹션에만) - 블로그 한정
INLINE_CITATION_PATTERN = re.compile(
    r'[(（][^()（）\n]{0,40}(?:뉴스룸|일보|경제|신문|매체|타임스|투데이|비즈|헤럴드|연합|뉴시스|머니|조선|중앙|한겨레|동아|파이낸셜|데일리)'
    r'[^()（）\n]{0,40},?\s*\d{4}[.\-]\d{1,2}(?:[.\-]\d{1,2})?[)）]'
)

# 독자를 가르치는 말투 금지 - 브랜드 스타일 규칙 (전 플랫폼 공통)
TEACHING_TONE_PATTERN = re.compile(
    r'으로만\s*보면\s*절반|만으로는\s*절반밖에|밖에\s*안\s*돼요|이렇게\s*읽어야\s*해요|을\s*알아야\s*해요'
)

# 개인 감정 고백형 오프닝 금지 - voice-guide.md 인트로 작성 규칙
CONFESSIONAL_INTRO_PATTERN = re.compile(
    r'솔직히\s*말하면|솔직히\s*이건\s*좀\s*의외'
    r'|처음\s*봤을\s*때[^.!?\n]{0,40}(?:멈칫|넘기지\s*않)'
)

# 내부 메타 표현 금지 - Validator 규칙 검증 항목
META_LEAK_PATTERN = re.compile(
    r'CLAUDE\.md|SKILL\.md|AGENT\.md|\(내용\s*추가\)|\(수정\s*필요\)|^\s*(?:메모|참고|TODO)\s*[:：]',
    re.MULTILINE,
)

# 해외 사례 비교 필수 (voice-guide.md, 블로그 플랫폼 필수) - 최소한의 키워드 기반 점검
GLOBAL_CASE_KEYWORDS = [
    "알리바바", "Alibaba", "아마존", "Amazon", "월마트", "Walmart", "타오바오", "Taobao",
    "징동", "JD.com", "핀둬둬", "Pinduoduo", "쉬인", "Shein", "테무", "Temu",
    "라쿠텐", "Rakuten", "이베이", "eBay", "메르카리", "Mercari", "쇼피", "Shopee",
    "세포라", "Sephora", "Zara", "유니클로", "Uniqlo", "인디텍스", "Inditex",
    "패스트리테일링", "Fast Retailing", "나이키", "Nike", "스타벅스", "Starbucks",
    "코스트코", "Costco", "Target", "쇼피파이", "Shopify", "엣시", "Etsy",
    "인스타카트", "Instacart", "도어대시", "DoorDash", "우버이츠", "Uber Eats",
    "Meta", "구글", "Google", "넷플릭스", "Netflix", "에어비앤비", "Airbnb",
    "로레알", "L'Oréal", "에스티로더", "Estée Lauder", "LVMH", "까르푸", "Carrefour",
    "테스코", "Tesco", "알디", "Aldi", "리들", "Lidl",
]
# "자라"(Zara)·"타겟"(Target)·"메타"(Meta)의 한글 표기는 일반 동사/명사와 겹쳐 오탐을
# 유발하므로 영문 표기만 키워드로 둔다 (예: 자라다, 타겟팅, 메타버스).


def _content_length(content: str, unit: str) -> int:
    if unit == "byte":
        return len(content.encode("utf-8"))
    return len(content)


def _body_before_sources(content: str) -> str:
    """'출처' 섹션 이전 본문만 추출 (본문 내 인용 검사용)"""
    match = re.search(r'(?m)^\s*출처\s*$', content)
    return content[: match.start()] if match else content


def _strip_sources_section(content: str) -> str:
    """분량 계산에서 '출처' 섹션만 제외한 콘텐츠를 반환한다 (태그 줄은 그대로 유지).

    출처 목록은 검증 과정에서 확인한 근거 수만큼 계속 늘어나는 부록성 구간이라
    실제 독자가 읽는 본문 분량과는 성격이 달라서, 블로그 분량 기준(CLAUDE.md 13번)
    산정에서 제외한다."""
    src_match = re.search(r'(?m)^\s*출처\s*$', content)
    if not src_match:
        return content
    tag_match = re.search(r'(?m)^\s*태그\s*[:：]', content[src_match.end():])
    if tag_match:
        tag_start = src_match.end() + tag_match.start()
        return content[: src_match.start()] + content[tag_start:]
    return content[: src_match.start()]


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

    if platform == "blog":
        issues.extend(_validate_blog_schema(content))

    return issues


def _validate_blog_schema(content: str) -> list[str]:
    """블로그 플랫폼 전용 구조 검증 (CLAUDE.md 출력 형식 규칙 9~10번)"""
    issues = []
    lines = content.splitlines()

    # 블로그 시리즈 헤더 (맨 첫 2줄)
    if not lines or not re.match(r'^커머스\s*인사이트\s*Vol\.\d+', lines[0].strip()):
        issues.append("1번째 줄에 '커머스 인사이트 Vol.XXX' 헤더가 없어요")
    if len(lines) < 2 or not re.search(r'\d{4}년\s*\d{1,2}월\s*[^\s]*째\s*주', lines[1]):
        issues.append("2번째 줄에 'YYYY년 N월 N째 주' 헤더가 없어요")

    # 상단 목차형 요약
    if "이 글에서 다루는 것" not in content:
        issues.append("상단 목차형 요약 섹션('■ 이 글에서 다루는 것')이 없어요")
    else:
        toc_section = content.split("이 글에서 다루는 것", 1)[1].split("■", 1)[0]
        toc_items = re.findall(r'(?m)^\s*·', toc_section)
        if len(toc_items) < 5:
            issues.append(f"상단 목차 항목이 {len(toc_items)}개예요 (5~6개 필요)")

    # 하단 FAQ
    if "더 생각해볼 것들" not in content:
        issues.append("하단 FAQ 섹션('■ 더 생각해볼 것들')이 없어요")
    else:
        faq_section = content.split("더 생각해볼 것들", 1)[1]
        faq_questions = re.findall(r'(?m)^\s*Q\.', faq_section)
        if len(faq_questions) < 2:
            issues.append(f"FAQ 질문이 {len(faq_questions)}개예요 (2~3개 필요)")

    # 출처 섹션
    if not re.search(r'(?m)^\s*출처\s*$', content):
        issues.append("하단 출처 섹션('출처')이 없어요")

    # SEO 태그 30개
    tag_match = re.search(r'(?m)^\s*태그\s*[:：]\s*(.+)$', content)
    if not tag_match:
        issues.append("SEO 태그 섹션('태그: ...')이 없어요")
    else:
        tag_count = len([t for t in tag_match.group(1).split(",") if t.strip()])
        if tag_count < 25:
            issues.append(f"SEO 태그가 {tag_count}개예요 (30개 필요)")

    # 해외 사례 비교 (voice-guide.md 필수 규칙) - 출처 목록 인용만으로는 인정하지 않고 본문만 검사
    body = _body_before_sources(content)
    if not any(kw in body for kw in GLOBAL_CASE_KEYWORDS):
        issues.append(
            "해외 사례 비교가 없어요 (voice-guide.md 필수 규칙: 관련 업계 해외 플랫폼·기업 사례를 "
            "1개 이상 포함하고 국내 사례와 비교·대조할 것)"
        )

    issues.extend(_check_term_definitions(body))

    return issues


def _check_term_definitions(body: str) -> list[str]:
    """용어 정의(※) 배치 검증 (CLAUDE.md 출력 형식 12번)

    ① 본문에 실제로 등장하지 않는 용어를 정의하면 안 됨
    ② 정의는 해당 용어가 처음 나온 뒤에 와야 함 (앞서 쓰고 나중에 설명 금지)

    목차 구간은 항목 나열일 뿐이라 '첫 등장' 판정에서 제외한다.
    """
    issues = []

    toc_match = re.search(r'■\s*이 글에서 다루는 것', body)
    first_section = re.search(r'(?m)^■(?!\s*이 글에서 다루는 것)', body)
    scan_start = first_section.start() if first_section else (toc_match.end() if toc_match else 0)

    for match in re.finditer(r'※\s*([^,\n]+?)(?:이란|란|는)\s*,', body):
        term = match.group(1).strip()
        # 정의문 자체는 등장 위치에서 제외
        uses = [
            m.start()
            for m in re.finditer(re.escape(term), body)
            if m.start() >= scan_start and not (match.start() <= m.start() <= match.end())
        ]
        if not uses:
            issues.append(
                f"용어 정의 오류: '{term}'이(가) 본문에 등장하지 않는데 정의만 있어요 "
                f"(해당 문단에서 실제 쓰인 용어만 설명할 것)"
            )
        elif min(uses) > match.start():
            issues.append(
                f"용어 정의 위치 오류: '{term}' 정의가 첫 등장보다 앞서 있어요 "
                f"(용어가 처음 나오는 문단 직후에 배치할 것)"
            )

    return issues


def validate_rules(content: str, platform: str) -> list[str]:
    """2단계: 규칙 기반 검증 - 글자 수/바이트 수, 금지 표현"""
    issues = []
    rules = PLATFORM_RULES.get(platform, {})
    unit = rules.get("length_unit", "char")
    length_target = _strip_sources_section(content) if platform == "blog" else content
    content_length = _content_length(length_target, unit)
    unit_label = "바이트" if unit == "byte" else "자"

    min_len = rules.get("min_length", 0)
    max_len = rules.get("max_length", 99999)

    if content_length < min_len:
        issues.append(f"분량 부족: {content_length}{unit_label} (최소 {min_len}{unit_label} 필요)")

    if content_length > max_len:
        issues.append(f"분량 초과: {content_length}{unit_label} (최대 {max_len}{unit_label})")

    # 금지 표현(~다/함/임 체) - 전 플랫폼 공통
    forbidden_matches = FORBIDDEN_ENDINGS.findall(content)
    if forbidden_matches:
        samples = forbidden_matches[:3]
        sample_text = " / ".join(s.strip()[-20:] for s in samples)
        issues.append(f"금지 표현(~다/함/임 체) 검출 {len(forbidden_matches)}건: ...{sample_text}")

    # 마크다운 기호 - 전 플랫폼 공통, 절대 규칙
    for name, pattern in MARKDOWN_PATTERNS.items():
        if pattern.search(content):
            issues.append(f"마크다운 기호 사용 금지 위반: {name}")

    # 간접 인용 서술어 - 전 플랫폼 공통, 절대 규칙
    if INDIRECT_QUOTE_PATTERN.search(content):
        issues.append("간접 인용 서술어(~기사에 따르면 등) 사용 금지 위반")

    # 가르치는 말투 - 브랜드 스타일 규칙 공통
    if TEACHING_TONE_PATTERN.search(content):
        issues.append("독자를 가르치는 말투 금지 표현 검출")

    # 개인 감정 고백형 인트로 - voice-guide.md
    if CONFESSIONAL_INTRO_PATTERN.search(content):
        issues.append("금지된 개인 감정 고백형 오프닝 패턴 검출 (예: '처음 봤을 때 ~넘기지 않았어요')")

    # 내부 메타 표현 누출
    if META_LEAK_PATTERN.search(content):
        issues.append("내부 메타 표현(CLAUDE.md/SKILL.md 언급, 작업노트성 표현 등) 검출")

    if platform == "blog":
        body = _body_before_sources(content)
        if INLINE_CITATION_PATTERN.search(body):
            issues.append("본문 내 괄호 출처 인용 금지 위반 (출처는 하단 출처 섹션에만 표기)")

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
    feedback_parts.append("~다/함/임으로 끝나는 문장이나 마크다운 기호(#, **, -, > 등)는 절대 쓰지 마세요.")
    feedback_parts.append("실무자 관점의 인사이트도 빠뜨리지 마세요.")
    if platform == "blog":
        feedback_parts.append(
            "블로그는 Vol 헤더, 상단 목차(■ 이 글에서 다루는 것), 하단 FAQ(■ 더 생각해볼 것들), "
            "출처 섹션, SEO 태그 30개, 해외 사례 비교를 모두 포함해야 해요."
        )

    return "\n".join(feedback_parts)
