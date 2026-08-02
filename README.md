# ContentPipe

주제와 참고자료를 입력하면 5개 플랫폼용 콘텐츠를 자동으로 생성하는 CLI 도구예요.

Strategist(기획) → Writer(초고) → Validator(규칙 검증) → Reviewer(팩트체크) → Style Editor(톤 검수)로 이어지는 멀티 에이전트 파이프라인을 통해, 근거 없는 수치나 딱딱한 말투 없이 브랜드 톤이 일관된 콘텐츠를 만들어요.

## 주요 기능

- 인스타그램 카드뉴스, 릴스 시나리오, 링크드인, 블로그, 스레드 콘텐츠 일괄 생성
- Strategist가 주제를 먼저 분석해 아웃라인·차별화 관점을 기획한 뒤 Writer에게 전달
- 브랜드 톤·말투 일관성 유지 (15년 경력 이커머스 전문가 페르소나, 구어체 필수)
- 팩트체크 + 논리 검토 + 스타일 검수까지 포함하는 고품질 모드 지원
- 근거 없는 수치·간접 인용·가르치는 말투·마크다운 기호 등을 규정식으로 자동 검출
- 고품질 모드에서 검증 통과한 결과물은 스타일 레퍼런스로 자동 축적

## 설치

```bash
pip install -e .
```

## 환경변수

`.env.example`을 복사해 `.env`로 저장하고 API 키를 입력하세요.

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...
CONTENT_MODEL=claude-sonnet-4-20250514
CONTENT_MAX_TOKENS=4096
```

## 사용법

```bash
# 인터랙티브 모드 (인자 없이 실행)
contentpipe generate

# 기본 생성 (전체 플랫폼)
contentpipe generate -t "주제" --all

# 참고자료 포함 고품질 생성
contentpipe generate -t "주제" -r "참고자료" --all --quality high

# 파일로 참고자료 전달
contentpipe generate -t "주제" -f ref.md --all

# 특정 플랫폼만 선택
contentpipe generate -t "주제" -p instagram,blog --quality high

# API 호출 없이 설정만 확인
contentpipe generate -t "주제" --all --dry-run

# 결과 확인
contentpipe list
contentpipe show {slug} {platform}
```

## 출력 플랫폼

| 플랫폼 | 키 | 파일명 |
|--------|-----|--------|
| 인스타그램 카드뉴스 | `instagram` | instagram-cardnews.md |
| 릴스 시나리오 | `reels` | reels-scenario.md |
| 링크드인 | `linkedin` | linkedin-post.md |
| 블로그 | `blog` | blog-post.md |
| 스레드 | `threads` | threads-post.md |

## 품질 파이프라인

모든 콘텐츠는 생성 전에 Strategist가 주제를 분석하고, 생성 후 최소 Validator 검증을 거쳐요.

```
Strategist  주제 분석 · 아웃라인 · 차별화 관점 기획
    ↓
Writer      초고 생성 (Strategist 브리프 반영)
    ↓
Validator   규칙 기반 검증 — 실패 시 Writer 재작성 최대 2회
    ↓
저장 (standard 모드는 여기서 종료)
```

`--quality high`를 주면 아래 단계가 이어져요.

```
    ↓
Reviewer      팩트 · 논리 검토 — 피드백 있으면 Writer 재작성 1회
    ↓
Style Editor  톤 · 말투 검수 — 피드백 있으면 Writer 재작성 1회
    ↓
Validator     최종 검증 (경고만 남기고 저장은 진행)
    ↓
저장 + 통과 결과물을 style-reference에 자동 축적
```

| 모드 | API 호출 | 특징 |
|------|----------|------|
| `standard` (기본값) | 플랫폼당 2~4회 | Strategist + Writer + Validator만 거침 |
| `high` | 플랫폼당 5~8회 | Reviewer·Style Editor까지 포함한 풀 루프 |

## 콘텐츠 작성 원칙

전 플랫폼 공통으로 Validator가 아래 항목을 코드로 강제해요. 어기면 Writer에게 구체적 피드백과 함께 재작성을 요청해요.

- 말투: `~해요/~네요/~어요` 구어체 필수, `~다/함/임`체 문장 종결 금지
- 마크다운 기호 전면 금지: 헤딩(`#`), 볼드(`**`), 이탤릭(`*`/`_`), 불렛(`-`), 인용(`>`), 코드블록(``` ``` ```), 표(`|---|`), 링크(`[]()`), 숫자 나열(`1. 2. 3.`), 구분선(`---`) — 복사해서 바로 쓰는 순수 텍스트로만 출력
- 간접 인용 서술어 금지: "~기사에 따르면", "~에 의하면" 등 — 사실을 직접 서술하고 출처는 하단 섹션에만 표기
- 독자를 가르치는 말투 금지 (예: "~밖에 안 돼요", "이렇게 읽어야 해요")
- 개인 감정 고백형 오프닝 금지 (예: "솔직히 말하면 ~놀랐어요")
- 내부 메타 표현 누출 금지 (CLAUDE.md/SKILL.md 언급, "메모:", "TODO:" 등 작업노트성 표현)
- 근거 없는 수치·사례·기업명 단정 서술 금지 — 출처 확인 불가 시 추론 표현으로 대체

## 블로그 전용 출력 형식

블로그(`blog`)는 다른 플랫폼보다 훨씬 엄격한 구조·분량 기준을 가져요.

- 분량: 초고부터 20,000~26,000바이트 목표 (Validator가 바이트 단위로 측정)
- 1~2번째 줄: `커머스 인사이트 Vol.XXX` / `YYYY년 N월 N째 주` 시리즈 헤더
- 소제목 표기: 큰 섹션은 `■`, 중간 섹션은 `✔️`, 목록은 `·`, 번호 나열은 `① ② ③ ...`
- 인트로 다음: `■ 이 글에서 다루는 것` — 결론·수치 노출 없이 궁금증 유발형 항목 5~6개
- 결론 다음: `■ 더 생각해볼 것들` — 분석·판단형 `Q.` 질문 5개 + 답변
- 하단: 출처 섹션(매체명, 제목, YYYY.MM.DD) → SEO 태그 30개(`태그: ...`)
- 관련 업계 해외 기업·플랫폼 사례를 1개 이상 포함해 국내 사례와 비교

## 디렉토리 구조

```
src/content_pipeline/
├── cli.py                 CLI 명령어 (generate, list, show)
├── generator.py           오케스트레이터 (파이프라인 조율)
├── validator.py           규칙 기반 검증 (마크다운/말투/분량/블로그 스키마)
├── client.py              Claude API 래퍼 (재시도 포함)
├── asset_manager.py       참고자료·결과물 파일 입출력
├── agents/
│   ├── strategist.py      주제 분석 · 아웃라인 기획
│   ├── writer.py          초고 생성 · 피드백 반영 재작성
│   ├── reviewer.py        팩트체크 · 논리 검토 (고품질 모드)
│   └── style_editor.py    톤/말투 검수 (고품질 모드)
├── platforms/             플랫폼별 생성기 (5개)
└── prompts/               플랫폼별 시스템 프롬프트

.claude/
├── agents/                서브에이전트 설계 문서 (00-orchestrator ~ 04-style-editor)
└── skills/
    ├── content-generator/
    ├── quality-validator/
    └── style-reference/
        └── references/    검증 통과 결과물 자동 축적 위치

assets/brand/
├── voice-guide.md         브랜드 스타일 가이드
└── writing-samples.md     글쓰기 샘플

output/                    생성된 콘텐츠 (슬러그별 디렉토리)
```
