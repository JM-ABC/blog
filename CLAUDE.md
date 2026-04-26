ContentPipe 에이전트 설계서


작업 개요

  목적: 주제 + 참고자료를 입력받아 5개 플랫폼용 콘텐츠를 자동 생성하는 CLI 도구
  입력: 주제(텍스트), URL 또는 참고자료(텍스트/파일), 플랫폼 선택
  출력: 플랫폼별 markdown 파일 (instagram-cardnews, reels-scenario, linkedin-post, blog-post, threads-post)
  제약조건: Claude API 호출 비용, 크롤링 제한, 브랜드 스타일 일관성 유지


에이전트 구조

  유형: 오케스트레이터 + 서브에이전트 4개

  Orchestrator (generator.py)
    전체 워크플로우 감독 및 조율
    서브에이전트 간 직접 호출 금지, 반드시 오케스트레이터를 통해 조율
    --quality 옵션에 따라 워크플로우 분기

  Topic Suggester 서브에이전트 (agents/topic_suggester.py)
    역할: 최신 트렌드 기반 주제 5개 추천 + 사용자 선택 처리
    웹 검색으로 최근 1-2주 이슈 수집 후 페르소나(이커머스 전문가) 관점으로 필터링
    각 주제에 한 줄 추천 이유 포함
    사용자 입력 처리: 번호 선택(① - ⑤) 또는 직접 주제 입력 모두 허용
    선택된 주제를 Orchestrator로 전달하여 generate 워크플로우 연결
    설계: .claude/agents/topic-suggester/AGENT.md

  Writer 서브에이전트 (agents/writer.py)
    역할: 플랫폼별 콘텐츠 초고 생성 + 피드백 반영 재작성
    5개 플랫폼의 프롬프트 조합 + API 호출 담당
    Reviewer, Style Editor 피드백을 반영한 재작성 능력
    설계: .claude/agents/writer/AGENT.md

  Reviewer 서브에이전트 (agents/reviewer.py)
    역할: 비판적/냉정한 논리 검토 + 팩트체크
    인터넷 검색으로 추가 팩트체크 (출처 넓게 허용, 출처 명시)
    피드백만 반환, 직접 수정하지 않음
    고품질 모드(--quality high)에서만 활성화
    설계: .claude/agents/reviewer/AGENT.md

  Style Editor 서브에이전트 (agents/style_editor.py)
    역할: 브랜드 톤/말투 검수
    voice-guide.md + writing-samples.md 기반 톤 적합성 평가
    금지 표현 검출, 실무 인사이트 포함 여부 확인
    피드백만 반환, Writer가 재작성
    검증 통과 결과물을 레퍼런스에 자동 축적
    고품질 모드(--quality high)에서만 활성화
    설계: .claude/agents/style-editor/AGENT.md


워크플로우

  기본 모드 (--quality standard, 기본값)

    1. 입력 검증 (스크립트, cli.py)
    2. 참고자료 저장 (스크립트, asset_manager.py)
    3. 브랜드 컨텍스트 로드 (style-reference 스킬)
    4. 각 플랫폼별:
       Writer 초고 생성 -> Validator 규칙 검증 -> (실패 시 재작성 최대 2회) -> 저장

    API 호출: 플랫폼당 1-3회

  고품질 모드 (--quality high)

    1. 입력 검증 (스크립트)
    2. 참고자료 저장 (스크립트)
    3. 브랜드 컨텍스트 + 글 샘플 로드
    4. 각 플랫폼별:
       Writer 초고 생성
       -> Validator 규칙 검증 (실패 시 재작성 최대 2회)
       -> Reviewer 논리/팩트 검토 (실패 시 Writer 재작성 1회)
       -> Style Editor 톤/말투 검수 (실패 시 Writer 재작성 1회)
       -> Validator 최종 검증
       -> 저장
       -> 통과된 결과물 레퍼런스 자동 축적

    API 호출: 플랫폼당 4-7회


단계별 성공 기준과 검증 방법

  입력 검증
    성공 기준: 주제 비어있지 않음, 최소 1개 플랫폼 선택
    검증 방법: 규칙 기반
    실패 시: 에스컬레이션 (사용자에게 재입력 요청)

  콘텐츠 생성 (Writer)
    성공 기준: 응답 비어있지 않음
    검증 방법: 스키마 검증
    실패 시: 자동 재시도 (API 레벨, 최대 3회)

  근거 기반 작성 규칙 (전 모드, 전 플랫폼 공통, 절대 규칙)
    모든 수치·사례·플랫폼 행동 주장에 출처 필수
    적용 대상: 통계, 판매량·검색량 변화, 소비자 행동 패턴, 기업 전략·실적, 해외 사례 등 사실 주장 전체
    작성 전 웹서치로 출처 확인 필수. 확인 불가 시 아래 중 택일:
      · 삭제
      · "과거 유사 사례에서 반복됐던 패턴이에요", "~하는 경향이 있어요" 등 추론임을 명시한 표현으로 교체
    절대 금지: 출처 없이 구체적 수치, 플랫폼명, 기업명을 단정적으로 서술
      예시 금지: "쿠팡 매출이 X% 증가했어요" (출처 없음)
      예시 허용: "과거 유사 사례에서 이커머스 생필품 매출이 단기 급증하는 경향이 있었어요"
    출처 명시 형식: 본문 인용 시 괄호로 표기 (매체명, 연도) / 파일 하단 출처 섹션에 별도 정리

  규칙 검증 (Validator)
    성공 기준: 필수 섹션 존재, 글자수 범위, 금지 표현 없음, 내부 메타 표현 없음
    검증 방법: 규칙 기반 (validator.py)
    실패 시: 피드백 포함 Writer 재작성 (최대 2회)
    내부 메타 표현 금지 패턴 (결과물에 포함 시 검증 실패 처리)
      · CLAUDE.md / SKILL.md / AGENT.md 등 내부 파일명 언급
      · "메모:", "참고:", "TODO:", "여기에 내용 추가" 등 작업 노트성 표현
      · 괄호 안 지시어 (예: (내용 추가), (수정 필요))

  논리/팩트 검토 (Reviewer, 고품질 모드)
    성공 기준: 팩트 오류 없음, 논리적 비약 없음, 수치 출처 신뢰성 확인
    검증 방법: LLM 자기 검증 + 인터넷 검색
    실패 시: 피드백 전달 -> Writer 재작성 1회
    수치 인용 검증 규칙 (통계·시장 데이터 인용 시 필수 적용)
      신뢰 출처 우선: Gartner / Forrester / McKinsey / Juniper Research / eMarketer / IBM / 국내 통계청·KISA 등
      수치 간 논리 일관성 검증: 같은 글 안에서 연도별 수치가 앞뒤로 모순되지 않는지 확인
        예시 오류: 2025년 시장 2,900억 달러 → 2035년 326억 달러 (역성장 불가)
      미검증 출처 처리: 주요 기관에서 확인되지 않는 출처는 수치 대신 방향성·범위로 대체
        예시 대체: "12.3%" → "10% 이상", "25~30% 향상" → "두 자릿수 향상 보고"
      베스트케이스 주의: 개별 사례 수치는 "특정 사례 기준" 또는 "도입 사례에서 보고" 등으로 한정 표현

  톤/말투 검수 (Style Editor, 고품질 모드)
    성공 기준: 톤 점수 7/10 이상, 금지 표현 없음, 인사이트 포함
    검증 방법: LLM 자기 검증
    실패 시: 피드백 전달 -> Writer 재작성 1회


판단과 코드의 역할 분리

  에이전트(LLM)가 직접 수행
    콘텐츠 생성 (자연어 생성)
    논리/팩트 검토 (Reviewer)
    톤 적합성 평가 (Style Editor)
    피드백 반영 재작성 (Writer)

  스크립트로 처리
    파일 I/O (참고자료 저장, 결과물 저장, 샘플 축적)
    CLI 입력 파싱 및 유효성 검사
    글자 수 카운트, 필수 섹션 체크, 금지 표현 정규식
    API 호출 재시도 로직
    디렉토리 생성, 슬러그 변환


스킬 목록

  content-generator
    역할: 플랫폼별 콘텐츠 생성 (프롬프트 조합 + API 호출)
    설계: .claude/skills/content-generator/SKILL.md

  quality-validator
    역할: 생성된 콘텐츠의 품질 검증 (스키마/규칙/LLM 톤 체크)
    설계: .claude/skills/quality-validator/SKILL.md

  style-reference
    역할: 브랜드 가이드라인 + 글쓰기 샘플 관리
    설계: .claude/skills/style-reference/SKILL.md


브랜드 스타일 규칙 (전 플랫폼 공통)

  페르소나: '커머스의 모든 것' 블로그 운영자, 15년 경력 이커머스 전문가
  말투: 구어체 (~해요, ~네요, ~어요), 전문적 맥락에서만 ~했습니다
  금지: ~다/함/임 체 (딱딱한 보고서 스타일)
  필수: 실무자 관점 인사이트 1-2문장 이상 포함
  참조: assets/brand/voice-guide.md
  샘플: assets/brand/writing-samples.md


출력 형식 규칙 (전 에이전트, 전 플랫폼 공통, 절대 규칙)

  1. 마크다운 기호 절대 사용 금지
     # ## ### (헤딩), ** __ (볼드), * _ (이탤릭), - (불렛),
     > (인용), ``` (코드블록), | --- | (테이블), [텍스트](URL) (링크)
     위 기호들을 결과물에 절대 포함하지 않는다.

  2. 제목과 섹션 구분 (3단계)
     대제목: 줄바꿈과 대문자로만 구분 (글 전체 제목)
     큰 섹션 소제목: ■ + 텍스트 (예: ■ 에이전틱 커머스가 뭔지, 한 번만 정리해요)
     중간 소제목: ✔️ + 텍스트 (예: ✔️ 네이버의 전략)
     구분선(--- / ━━━ 등): 사용 금지. 빈 줄(줄바꿈)만 사용
  3. 강조 표현 금지: **, __, <>, 이탤릭(*_), 따옴표 강조 등 모든 강조 기법 사용 금지
  4. 번호 나열: 반드시 숫자 이모지 사용 (① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩)
     1. 2. 3. 형식 숫자 나열 금지
     적용 범위: 단계 나열, 목록 나열, 연도별 전망 등 순서가 있는 모든 나열
  5. 비번호 목록: 가운뎃점(·) 사용
  5. 표: 탭 정렬 또는 줄바꿈 나열 방식
  6. 결과물은 복사해서 바로 사용할 수 있는 일반 텍스트(plain text)로만 제공
  7. 출처 표기 (블로그 플랫폼 한정, 웹서치 기반 작성 시 필수)
     FAQ 다음, SEO 태그 앞에 출처 섹션 추가
     형식: 매체명, "기사/보도자료 제목", YYYY.MM.DD (일 단위까지 명시)
       예시: 무신사 뉴스룸, "무신사, 2025년 영업이익 전년비 37% 늘어 1405억원", 2026.03.31
       제목 확인 불가 시: 매체명, YYYY.MM.DD (연도만 아는 경우에도 연·월까지는 반드시 명시)
     URL 직접 노출 금지
     본문 인용 괄호 표기도 일 단위까지: (매체명, YYYY.MM.DD)

  8. SEO 태그 (블로그 플랫폼 한정)
     파일 맨 끝에 네이버 블로그 SEO 최적화 검색태그 30개 추가
     본문 내용을 분석해서 핵심 키워드 + 세부 키워드 조합으로 구성
     형식: 태그: 태그1, 태그2, 태그3, ... (쉼표 구분, 한 줄로 작성)

  9. 블로그 SEO 구조 (블로그 플랫폼 한정, 절대 규칙)

     상단 목차형 요약 (TL;DR 대체)
       위치: 인트로 마지막 문장 바로 다음, 첫 ■ 섹션 전
       형식: "이 글에서 다루는 것" 제목 + · 항목 5-6개 나열
       목적: 독자 체류시간 보호(TL;DR 결론 선공개 금지) + 네이버 C-Rank 주제 인식 강화
       금지: 결론·판단·수치 노출 (항목은 "~의 실체", "~비교", "~현실성" 등 궁금증 유발형으로)

     하단 FAQ
       위치: 결론 단락 다음, 출처 섹션 전
       형식: ■ 자주 묻는 질문 (FAQ) → Q. 질문 → 답변 2-4문장 → 빈 줄 구분 → 5개
       질문 유형: 정보형(몇 층이에요?) 금지, 분석·판단형 중심 ("~가능할까요?", "~다른 이유가 뭔가요?", "~실패할 가능성은?")
       목적: 네이버 VIEW 탭 롱테일 질문 키워드 매칭 강화


디렉토리 구조

  src/content_pipeline/
    cli.py                      CLI 명령어 (generate, list, show)
    config.py                   설정 로드 (.env)
    client.py                   Claude API 래퍼 (재시도 포함)
    generator.py                오케스트레이터 (워크플로우 조율)
    asset_manager.py            파일 입출력 관리
    validator.py                규칙 기반 품질 검증
    utils.py                    유틸리티 함수
    agents/                     서브에이전트 Python 로직
      writer.py                 Writer 서브에이전트
      reviewer.py               Reviewer 서브에이전트
      style_editor.py           Style Editor 서브에이전트
      topic_suggester.py        Topic Suggester 서브에이전트
    platforms/                  플랫폼별 생성기 (Writer가 참조)
    prompts/                    플랫폼별 프롬프트 템플릿

  .claude/
    agents/                     서브에이전트 설계 문서
      writer/AGENT.md
      reviewer/AGENT.md
      style-editor/AGENT.md
      topic-suggester/AGENT.md
    skills/                     스킬 정의
      content-generator/SKILL.md
      quality-validator/SKILL.md
      style-reference/
        SKILL.md
        references/             검증 통과 결과물 자동 축적

  assets/
    topics/                     입력 참고자료 저장
    brand/
      voice-guide.md            브랜드 스타일 가이드
      writing-samples.md        사용자 글쓰기 샘플

  output/                       생성된 콘텐츠 출력


CLI 명령어

  contentpipe generate -t "주제" -f ref.md --all                    기본 모드 (검증만)
  contentpipe generate -t "주제" -r "참고자료" --all --quality high  고품질 모드 (풀 루프)
  contentpipe generate -t "주제" -p instagram,blog --quality high   특정 플랫폼 고품질
  contentpipe generate                                             인터랙티브 모드
  contentpipe topics                                               트렌드 기반 주제 5개 추천
  contentpipe topics -c "이커머스"                                   카테고리 지정 추천
  contentpipe list                                                 목록 확인
  contentpipe show {slug} {platform}                               결과 보기

  topics 명령어 인터랙티브 흐름
    Topic Suggester가 웹 검색 후 5개 주제를 이유와 함께 출력
    "원하는 번호를 선택하거나, 직접 주제를 입력하세요 (q: 종료): " 프롬프트 표시
    ① - ⑤ 입력: 해당 추천 주제로 generate 워크플로우 진행
    텍스트 직접 입력: 입력한 주제로 generate 워크플로우 진행
    q 입력: 종료
