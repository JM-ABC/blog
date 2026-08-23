# 주간 자동 발행 플로우 설계

날짜: 2026-08-24


## 배경 및 목적

지금까지는 사용자가 매주 직접 주제를 정하고 Claude Code 세션에서 블로그 초고 생성을 요청해왔다.
앞으로는 주제 선정과 초고 생성(팩트체크 포함)을 자동화하고, 사용자는 이메일로 주제만 승인하면
되도록 만든다. 실제 네이버 발행(복사·게시)은 이번 범위에서 제외하고 초고 생성까지만 자동화한다.

로컬 세션 기반 CronCreate는 세션 종료 시 소멸하고 7일 뒤 자동 만료되어 "영구 반복"에 맞지 않는다.
대신 클라우드 라우틴(claude.ai/code/routines, RemoteTrigger로 생성)을 사용한다. 각 라우틴은
JM-ABC/blog 저장소를 클론한 독립된 클라우드 세션에서 실행되며, 삭제하기 전까지 계속 유지된다.


## 아키텍처 개요

라우틴 2개로 구성한다.

- 라우틴 A "주간 주제 추천": 매주 목요일 09:00 KST (cron `0 0 * * 4`, UTC) 실행
  - 웹서치로 최근 1~2주 이커머스 트렌드 수집 → 페르소나(15년 경력 이커머스 전문가) 관점 필터링
  - output/ 폴더의 기존 발행 글과 중복되지 않는 5개 주제 후보 + 한 줄 추천 이유 선정
  - 후보를 `assets/topics/pending_topic_<YYYYMMDD>.md`에 저장하고 main에 commit+push
  - Gmail로 jmyoonkr@gmail.com에 5개 주제 + 이유 + "토요일 11시까지 회신 없으면 1순위로 자동
    진행합니다" 안내 메일 발송 (제목에 날짜 포함, 예: "[커머스 인사이트] 주제 추천 2026-08-27")
  - 모델: claude-sonnet-5

- 라우틴 B "주간 초고 생성": 매주 토요일 11:00 KST (cron `0 2 * * 6`, UTC) 실행
  - 이번 주 라우틴 A가 커밋한 pending_topic 파일을 읽음
  - Gmail에서 해당 주제 추천 메일 스레드의 회신을 검색 → 회신에서 번호(1~5) 또는 직접 입력한
    주제를 파싱. 회신 없으면 pending 파일의 1순위 주제로 자동 진행
  - CLAUDE.md의 고품질 모드(--quality high) 워크플로우를 그대로 따름:
    01-strategist(기획) → 02-writer(초고) → 03-reviewer(팩트체크) → 04-style-editor(톤 검수)
    → Writer 재작성 루프 → 최종 검증. 이 저장소의 .claude/agents/*.md 서브에이전트를 Agent
    도구로 호출하되, 사용 불가 시 각 .md 파일의 역할 지시를 직접 따른다
  - "발행 전 팩트체크 전수 점검" 절차(CLAUDE.md 규칙)를 초고 완성 직후 반드시 수행 —
    문장 단위 전수 검증, 회계연도 확인, 수치 정합성, 최신성 확인 등 9개 항목 전부
  - Vol 번호는 output/ 폴더에서 가장 최근 blog-post 파일 번호 +1 (CLAUDE.md 규칙 10 우선순위)
  - 실적/추이 지표가 있으면 assets/brand/chart_style.py 기반 인포그래픽 자동 생성 (규칙 17)
  - 대상 플랫폼: blog-post만 (5개 플랫폼 전체 아님)
  - 결과물을 output/<slug>/blog-post.txt (+ 인포그래픽)로 저장하고 main에 commit+push
  - 완료 후 Gmail로 확인 메일 발송: 선택된 주제, Vol 번호, 바이트 수, 팩트체크 점검 결과 요약
    (점검한 수치 개수 · 발견 오류 · 조치 내용 · 판단이 갈리는 항목)
  - 모델: claude-opus-5 (품질이 중요한 생성·검증 작업이라 상위 모델 사용)


## 데이터 흐름

```
목(09:00 KST)                              토(11:00 KST)
라우틴 A                                     라우틴 B
  웹서치 트렌드 조사                            pending_topic 파일 읽기
  → 5개 후보 선정                              → Gmail 회신 검색·파싱
  → assets/topics/pending_topic_*.md 저장       → (없으면 1순위 자동)
    commit+push                               → strategist→writer→reviewer
  → Gmail 발송 (jmyoonkr@gmail.com)              →style-editor 루프
                                              → 전수 팩트체크
        사용자 회신 (선택)  ---------------->    → Vol 번호 계산, 인포그래픽
                                              → output/ 저장, commit+push
                                              → 결과 요약 메일 발송
```


## 실패/예외 처리

- 라우틴 A가 중복 없는 주제를 못 찾으면: 범위를 넓혀(예: 카테고리 한정 해제) 재시도, 그래도
  실패 시 이유를 메일에 명시하고 가장 근접한 5개를 그대로 추천
- 라우틴 B가 이메일 회신을 못 찾으면: pending 파일의 1순위 주제로 자동 진행 (월요 발행 페이스
  유지가 우선)
- 라우틴 B의 팩트체크에서 핵심 수치의 출처를 확인할 수 없으면: CLAUDE.md 근거 기반 작성
  규칙에 따라 삭제하거나 추론 표현으로 대체 (생성을 중단하지 않음)
- git push 실패(충돌 등) 시: 실패 사실과 원인을 확인 메일에 포함해 사용자에게 알림


## 범위 밖 (이번에 하지 않는 것)

- 네이버 블로그에 실제로 포스팅하는 자동화 (API/브라우저 자동화) — 초고까지만 자동화, 게시는
  사용자가 수동으로
- instagram-cardnews / reels-scenario / linkedin-post / threads-post 자동 생성 — blog-post만
- Slack 알림 (Slack 채널 미확정으로 이메일로 대체)


## 구현 계획으로 넘어가기 전 확인된 결정 사항

- 결과물 전달 방식: main에 직접 commit+push (별도 브랜치/PR 없음)
- 알림 채널: Gmail (jmyoonkr@gmail.com)
- 무응답 시 처리: 마감 후 1순위 주제로 자동 진행
- 대상 플랫폼: blog-post만
- 모델: 라우틴 A는 claude-sonnet-5, 라우틴 B는 claude-opus-5
