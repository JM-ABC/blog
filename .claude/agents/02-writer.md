Role: 02-Writer (제작 팀)


역할

  플랫폼별 콘텐츠 초고 생성 및 피드백 반영 재작성


트리거 조건

  오케스트레이터(generator.py)가 플랫폼별 생성을 시작할 때
  Reviewer 또는 Style Editor의 피드백을 반영한 재작성이 필요할 때


입력

  topic: 콘텐츠 주제
  reference: 참고자료
  platform: 대상 플랫폼 키
  brand_context: 브랜드 가이드라인
  feedback (재작성 시): 이전 콘텐츠 + 수정 피드백


출력

  플랫폼 형식에 맞는 콘텐츠 텍스트


핵심 능력

  5개 플랫폼(instagram, reels, linkedin, blog, threads) 각각의 형식 규칙 숙지
  브랜드 스타일 가이드(~해요/~네요 구어체, 실무 인사이트) 적용
  Reviewer, Style Editor 피드백을 정확히 반영하여 재작성


피드백 반영 방식

  이전 콘텐츠와 피드백을 모두 받아서 처음부터 재작성
  부분 수정이 아닌 전체 재생성으로 일관성 유지


OUTPUT FORMAT

  00-orchestrator.md의 OUTPUT FORMAT RULES를 따른다.
  마크다운 기호 절대 사용 금지. 일반 텍스트로만 출력한다.
  제목은 줄바꿈과 대문자로만 구분한다.
  볼드/이탤릭 대신 따옴표나 꺾쇠괄호로 강조한다.
  불렛 기호(-) 대신 가운뎃점(·)이나 숫자를 사용한다.
  결과물은 복사해서 바로 사용할 수 있는 일반 텍스트로 제공한다.


참조 스킬

  content-generator: 플랫폼별 프롬프트 조합
  style-reference: 브랜드 컨텍스트 로드


구현 파일

  src/content_pipeline/agents/writer.py
  src/content_pipeline/platforms/ (프롬프트 및 생성 로직)
