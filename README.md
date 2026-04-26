# ContentPipe

주제와 참고자료를 입력하면 5개 플랫폼용 콘텐츠를 자동으로 생성하는 CLI 도구예요.

## 주요 기능

- 인스타그램 카드뉴스, 릴스 시나리오, 링크드인, 블로그, 스레드 콘텐츠 일괄 생성
- 트렌드 기반 주제 자동 추천 (웹 검색 활용)
- 브랜드 톤·말투 일관성 유지 (15년 경력 이커머스 전문가 페르소나)
- 팩트체크 + 논리 검토 + 스타일 검수 포함 고품질 모드 지원
- 근거 없는 수치·사례 자동 필터링 (출처 기반 작성 원칙)

## 설치

```bash
pip install -e .
```

## 사용법

```bash
# 기본 생성 (전체 플랫폼)
contentpipe generate -t "주제" --all

# 참고자료 포함 고품질 생성
contentpipe generate -t "주제" -r "참고자료" --all --quality high

# 특정 플랫폼만 선택
contentpipe generate -t "주제" -p instagram,blog --quality high

# 트렌드 기반 주제 추천
contentpipe topics
contentpipe topics -c "이커머스"

# 결과 확인
contentpipe list
contentpipe show {slug} {platform}
```

## 출력 플랫폼

| 플랫폼 | 파일명 |
|--------|--------|
| 인스타그램 카드뉴스 | instagram-cardnews.md |
| 릴스 시나리오 | reels-scenario.md |
| 링크드인 | linkedin-post.md |
| 블로그 | blog-post.md |
| 스레드 | threads-post.md |

## 품질 모드

**standard (기본값)**: Writer 생성 → 규칙 검증 → 저장 (플랫폼당 API 1~3회)

**high**: Writer 생성 → 규칙 검증 → Reviewer 팩트체크 → Style Editor 톤 검수 → 저장 (플랫폼당 API 4~7회)

## 블로그 콘텐츠 생성 상세

### 프롬프트 설계

블로그 포스트는 SEO와 가독성을 동시에 잡는 구조로 설계되어 있어요.

생성되는 글의 구조:

```
1. 제목      — H1, SEO 키워드 포함, 호기심 유발
2. 메타 설명 — 150자 이내, 검색 결과 미리보기용
3. 목차      — H2 기반 전체 구조 안내
4. 도입부    — 독자 공감 유도, 문제 정의
5. 본문      — H2/H3 구조, 3~5개 섹션
6. 체크리스트 — 실용적 조언 정리
7. 결론 + CTA
```

분량 기준: 2,000~3,000자 (Validator 허용 범위: 1,500~6,000자)

---

### 품질 컨트롤 파이프라인

글 하나가 저장되기까지 최대 5단계를 거쳐요.

**standard 모드**

```
Strategist (주제 분석·기획)
  ↓
Writer (초고 생성)
  ↓
Validator (규칙 검증) — 실패 시 Writer 재작성 최대 2회
  ↓
저장
```

**high 모드** (`--quality high`)

```
Strategist (주제 분석·기획)
  ↓
Writer (초고 생성)
  ↓
Validator (규칙 검증) — 실패 시 Writer 재작성 최대 2회
  ↓
Reviewer (팩트·논리 검토) — 실패 시 Writer 재작성 1회
  ↓
Style Editor (톤/말투 검수) — 실패 시 Writer 재작성 1회
  ↓
Validator (최종 검증)
  ↓
저장 + 레퍼런스 자동 축적
```

---

### 각 에이전트의 검증 기준

**Validator** (규칙 기반, 코드 처리)

| 항목 | 기준 |
|------|------|
| 글자 수 | 1,500자 이상 ~ 6,000자 이하 |
| 금지 표현 | `~다/함/임` 체 정규식 검출 시 실패 |

**Reviewer** (LLM, `--quality high` 전용)

① 논리적 일관성 — 주장과 근거가 연결되어 있는가
② 팩트 정확성 — 참고자료 수치·사실과 일치하는가
③ 과장·비약 — 근거 없는 단정 표현이 있는가
④ 누락 — 참고자료의 핵심 내용이 빠졌는가
⑤ 균형 — 특정 관점에 과도하게 편향되었는가

통과/실패를 JSON으로 반환하고, 실패 시 구체적 피드백을 Writer에게 전달해요.

**Style Editor** (LLM, `--quality high` 전용)

① 말투 — `~해요/~네요/~어요` 구어체가 일관되게 사용되었는가
② 금지 표현 — `~다/함/임` 체 잔존 여부
③ 톤 — "친절한 사수"처럼 전문적이면서 따뜻한 느낌
④ 인사이트 — 단순 요약이 아닌 실무자 관점 포함 여부
⑤ 문체 일관성 — 기존 글쓰기 샘플과 자연스럽게 이어지는가

톤 점수 10점 만점으로 채점하며, 7점 미만이면 재작성을 요청해요.
통과된 결과물은 `.claude/skills/style-reference/references/`에 자동으로 쌓여서 다음 글의 문체 레퍼런스로 활용돼요.

---

## 디렉토리 구조

```
src/content_pipeline/
├── cli.py               CLI 명령어
├── generator.py         오케스트레이터
├── validator.py         규칙 기반 검증
├── agents/              서브에이전트 (writer, reviewer, style_editor, topic_suggester)
└── prompts/             플랫폼별 프롬프트 템플릿

assets/brand/
├── voice-guide.md       브랜드 스타일 가이드
└── writing-samples.md   글쓰기 샘플

output/                  생성된 콘텐츠
```

## 환경변수

`.env.example` 파일을 복사해 `.env`로 저장 후 API 키를 입력하세요.

```bash
cp .env.example .env
```
