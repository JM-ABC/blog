# 네이버플러스 스토어 역대 최대 MAU 콘텐츠 생성 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 네이버플러스 스토어 역대 최대 MAU 달성 배경을 3각 전략 프레임으로 분석한 블로그 포스트 + 링크드인 포스트 생성

**Architecture:** Writer가 초고 생성 → Validator 규칙 검증 → Reviewer 팩트체크 → Style Editor 톤 검수 → 최종 저장 (고품질 모드)

**Tech Stack:** Claude API (claude-sonnet-4-6), ContentPipe CLI, Python

---

## 참고 데이터 (검증된 수치)

- 네이버플러스 스토어 MAU: 776만9721명 (2026년 3월, 역대 최대)
- 전월 대비 성장률: 9.3% (2월 710만6731명 대비)
- N배송 거래액: 전년 대비 77% 증가 / 주문 건수 65% 증가
- 컬리N마트: 월 50% 이상 성장, 재구매율 60%
- AI 쇼핑 에이전트 베타 1.0 출시 (롱테일 검색 대화형 추천)
- 출처: 테크M, 2026 / 이코노미스트, 2026.04.03

---

### Task 1: 블로그 포스트 초고 생성

**Files:**
- Create: `output/2026-04-05-naver-plus-store-mau/blog-post.md`

**Step 1: Writer — 초고 작성**

프롬프트 지침:
- 구조: 도입 → 배경 → 전략① AI → 전략② N배송 → 전략③ 컬리 → 종합 시사점 → 결론
- 분량: 2,000~3,000자
- 말투: ~해요/~네요 구어체, 15년 경력 이커머스 전문가 페르소나
- 출처 없는 수치 금지, 마크다운 기호 금지
- 소제목: ■ 기호 사용, 번호 나열: ① ② ③ 이모지

**Step 2: Validator 검증**

체크 항목:
- 필수 섹션 존재 여부 (도입/전략①②③/결론)
- 글자수 2,000~3,000자 범위
- 금지 표현 없음 (마크다운 기호, 내부 메타 표현)
- 출처 섹션 존재

실패 시: 피드백 포함 재작성 (최대 2회)

**Step 3: Reviewer 팩트체크**

검증 항목:
- MAU 수치 출처 일치 여부
- N배송 77% 수치 논리 일관성
- 컬리N마트 재구매율 60% 출처 확인
- 추가 수치 사용 시 방향성 표현 대체 여부

실패 시: 피드백 전달 → Writer 재작성 1회

**Step 4: Style Editor 톤 검수**

검증 항목:
- 구어체 (~해요/~네요) 유지 여부
- 실무자 인사이트 1~2문장 포함
- ~다/함/임 체 금지 표현 없음
- 톤 점수 7/10 이상

실패 시: 피드백 전달 → Writer 재작성 1회

**Step 5: 최종 Validator 검증 후 저장**

저장 경로: `output/2026-04-05-naver-plus-store-mau/blog-post.md`

---

### Task 2: 링크드인 포스트 초고 생성

**Files:**
- Create: `output/2026-04-05-naver-plus-store-mau/linkedin-post.md`

**Step 1: Writer — 초고 작성**

프롬프트 지침:
- 구조: 훅 → ① ② ③ 포인트 → 실무자 인사이트 → 댓글 유도 질문
- 분량: 700~1,000자
- 말투: 구어체, 전문가 관점
- 마크다운 기호 금지, 번호 나열: ① ② ③ 이모지

**Step 2: Validator 검증**

체크 항목:
- 글자수 700~1,000자 범위
- 훅 + 3포인트 + 마무리 구조
- 금지 표현 없음

**Step 3: Reviewer 팩트체크**

블로그와 동일 수치 사용 시 일관성 확인

**Step 4: Style Editor 톤 검수**

링크드인 특성상 전문가 어조 + 구어체 균형 확인

**Step 5: 최종 저장**

저장 경로: `output/2026-04-05-naver-plus-store-mau/linkedin-post.md`

---

### Task 3: 검증 통과 결과물 레퍼런스 축적

**Files:**
- Append: `.claude/skills/style-reference/references/`

고품질 모드 통과 결과물을 style-reference 레퍼런스에 자동 추가
