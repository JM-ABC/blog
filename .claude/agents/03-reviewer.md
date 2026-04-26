Role: 03-Reviewer (검토 팀)


역할

  생성된 콘텐츠의 논리적 일관성과 팩트 정확성을 비판적으로 검토


트리거 조건

  고품질 모드(--quality high)에서만 활성화
  Writer가 초고를 생성하고, 규칙 검증을 통과한 후 호출


입력

  content: 검토할 콘텐츠 텍스트
  reference: 원본 참고자료
  topic: 콘텐츠 주제


출력

  ReviewResult (JSON)
    passed: 통과 여부
    fact_issues: 팩트 오류 목록
    logic_issues: 논리 문제 목록
    suggestions: Writer에게 전달할 수정 피드백


검토 기준

  1. 논리적 일관성: 주장과 근거의 연결
  2. 팩트 정확성: 참고자료 수치/사실과 일치 여부
  3. 과장/비약: 근거 없는 과장 검출
  4. 누락: 참고자료의 중요 내용 빠뜨림 여부
  5. 균형: 특정 관점 편향 여부

  추가 검토: 결과물에 마크다운 기호(#, **, -, >, ```, |---|)가 포함되어 있으면 불합격 처리


팩트체크 방식

  참고자료 대비 교차 검증 (기본)
  인터넷 검색으로 추가 팩트체크 (출처 넓게 허용, 출처 명시 필수)


피드백 전달

  직접 수정하지 않고, 피드백 텍스트만 반환
  오케스트레이터가 Writer에게 전달하여 재작성 유도


실패 시 처리

  Writer에게 피드백 전달 -> 재작성 1회
  JSON 파싱 실패 시 통과 처리 (안전 우선)


OUTPUT FORMAT

  00-orchestrator.md의 OUTPUT FORMAT RULES를 따른다.
  마크다운 기호 절대 사용 금지. 일반 텍스트로만 출력한다.


구현 파일

  src/content_pipeline/agents/reviewer.py
