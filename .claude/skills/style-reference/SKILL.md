style-reference 스킬


역할
  브랜드 스타일 가이드와 글쓰기 샘플을 관리하고,
  콘텐츠 생성 시 스타일 컨텍스트를 제공하는 스킬

트리거 조건
  content-generator가 프롬프트를 조합할 때 자동으로 참조
  사용자가 "스타일 업데이트", "샘플 추가" 등을 요청할 때

입력
  action: "load" (스타일 컨텍스트 로드) 또는 "update" (가이드 수정)
  sample_text (선택): 새로 추가할 글쓰기 샘플

출력
  load 시: 스타일 가이드 + 글 샘플을 합친 컨텍스트 텍스트
  update 시: 업데이트된 파일 경로


관리 파일

  assets/brand/voice-guide.md
    브랜드 스타일 가이드 (페르소나, 말투 규칙, 톤 예시)
    이 파일은 모든 플랫폼 콘텐츠 생성 시 공통 적용

  assets/brand/writing-samples.md (선택)
    사용자가 직접 작성한 글 샘플 모음
    실제 문체, 어휘 선택, 문장 리듬을 학습하기 위한 레퍼런스
    새로운 샘플을 추가하면 이 파일에 누적 저장

  references/ (이 스킬 폴더 하위)
    플랫폼별 좋은 예시 콘텐츠 저장 공간
    검증 통과한 고품질 결과물을 레퍼런스로 보관 가능


스타일 컨텍스트 로드 흐름
  1. assets/brand/voice-guide.md 읽기
  2. assets/brand/writing-samples.md가 있으면 읽기
  3. 두 파일 내용을 합쳐서 하나의 스타일 컨텍스트로 반환
  4. content-generator가 이 컨텍스트를 시스템 프롬프트에 주입

참조 파일
  assets/brand/ 하위 모든 .md 파일
  src/content_pipeline/utils.py (read_brand_context 함수)
