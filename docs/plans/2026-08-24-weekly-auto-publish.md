# 주간 자동 발행 플로우 구현 계획

> **For Claude:** 이 계획은 코드 변경이 아니라 클라우드 라우틴(RemoteTrigger) 2개를 생성하는
> 설정 작업이다. superpowers:executing-plans/subagent-driven-development 대신 이 세션에서
> 직접 순서대로 실행한다.

**Goal:** 매주 목요일 주제 추천 메일 발송, 토요일 초고 생성·팩트체크·push를 자동화하는 클라우드
라우틴 2개를 생성한다.

**Architecture:** [설계 문서](docs/plans/2026-08-24-weekly-auto-publish-design.md) 참조.
라우틴 A(주제 추천, claude-sonnet-5, 목 09:00 KST) + 라우틴 B(초고 생성, claude-opus-5,
토 11:00 KST). 둘 다 JM-ABC/blog 저장소를 클론해서 실행, Gmail MCP 커넥터 연결.

**Tech Stack:** RemoteTrigger 툴 (claude.ai/code/routines), Gmail MCP 커넥터, 기존
.claude/agents/*.md 서브에이전트.

---

### Task 1: RemoteTrigger 툴 로드

`ToolSearch select:RemoteTrigger` 로 스키마를 불러온다.

### Task 2: 라우틴 A 프롬프트 작성

`assets/topics/` 디렉토리 존재 확인 (없으면 생성). 프롬프트는 아래 내용을 포함해야 한다:
- 오늘 날짜 확인 (`date` 명령)
- 웹서치로 최근 1~2주 국내 이커머스 트렌드 조사
- output/ 폴더 스캔해서 이미 다룬 주제와 중복 배제
- 페르소나(15년 경력 이커머스 전문가, CLAUDE.md 브랜드 스타일 참조) 관점으로 5개 후보 선정,
  각 한 줄 추천 이유 + 순위
- `assets/topics/pending_topic_<YYYYMMDD>.md`에 5개 후보 저장 (형식: 순위, 주제, 이유)
- git add/commit/push to main
- Gmail MCP로 jmyoonkr@gmail.com에 메일 발송. 제목: `[커머스 인사이트] 주제 추천 <YYYYMMDD>`.
  본문: 5개 주제+이유, "이번 주 토요일 11시까지 회신 없으면 1순위로 자동 진행합니다" 안내

### Task 3: 라우틴 A 생성

`RemoteTrigger` action: create. body:
- name: "weekly-topic-suggestion"
- cron_expression: "0 0 * * 4" (목 09:00 KST)
- job_config.ccr.session_context.model: "claude-sonnet-5"
- sources: JM-ABC/blog
- allowed_tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch
- mcp_connections: Gmail (connector_uuid 6a0ef32a-6f73-448a-812e-eb9690234dfb)
- events[0].message.content: Task 2에서 작성한 프롬프트

생성 후 `https://claude.ai/code/routines/{id}` 링크를 기록한다.

### Task 4: 라우틴 B 프롬프트 작성

프롬프트는 아래 내용을 포함해야 한다:
- 오늘 날짜 확인, 이번 주 목요일 날짜 계산해서 `assets/topics/pending_topic_<그날짜>.md` 읽기
- Gmail MCP로 해당 주제 추천 메일 스레드의 회신 검색. 회신 있으면 번호(1~5) 또는 직접 입력
  주제 파싱. 없으면 pending 파일 1순위 주제 사용
- CLAUDE.md 전체 규칙을 따라 blog-post 고품질 모드 워크플로우 수행:
  Agent 툴로 01-strategist → 02-writer → 03-reviewer → 04-style-editor 순서 호출
  (subagent_type: blog-strategist, blog-writer, blog-reviewer, blog-style-editor).
  Agent 툴 사용 불가 시 각 .claude/agents/*.md 파일의 역할 지시를 직접 수행
- "발행 전 팩트체크 전수 점검" (CLAUDE.md 규칙, 9개 항목) 반드시 수행하고 결과 기록
- Vol 번호: output/ 폴더 최신 blog-post 파일 번호 +1
- 실적/추이 지표 있으면 assets/brand/chart_style.py 기반 인포그래픽 생성 (규칙 17)
- output/<slug>/blog-post.txt (+인포그래픽)로 저장, git add/commit/push to main
- Gmail로 완료 메일 발송: 선택 주제, Vol 번호, 바이트 수, 팩트체크 요약 (점검 수치 개수·오류·
  조치·판단 갈리는 항목)

### Task 5: 라우틴 B 생성

`RemoteTrigger` action: create. body:
- name: "weekly-draft-generation"
- cron_expression: "0 2 * * 6" (토 11:00 KST)
- job_config.ccr.session_context.model: "claude-opus-5"
- sources: JM-ABC/blog
- allowed_tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
- mcp_connections: Gmail
- events[0].message.content: Task 4 프롬프트

생성 후 링크 기록.

### Task 6: 검증

`RemoteTrigger` action: list 로 두 라우틴이 정상 등록됐는지 확인 (이름, cron, enabled 여부).
사용자에게 테스트 실행(`action: run`) 여부를 물어본다 — 실제 이메일 발송·git push가 발생하므로
반드시 사용자 확인 후 실행한다.

### Task 7: 사용자에게 보고

두 라우틴 링크, 다음 실행 시각, 테스트 실행 결과(실행했다면)를 요약해서 전달한다.
