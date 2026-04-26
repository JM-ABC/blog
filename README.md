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
