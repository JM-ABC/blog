ContentPipe 리팩토링 설계서
에이전트 기반 콘텐츠 파이프라인 재설계


1. 현재 구조 분석과 문제점

  현재 흐름
    CLI 입력 -> generator.py 오케스트레이션 -> platforms/{각 플랫폼}.generate() -> validator.py 검증 -> 저장

  문제점
    platforms/ 생성기가 단순 프롬프트 래퍼 수준. 서브에이전트라 부르기엔 역할이 빈약
    생성 후 규칙 기반 검증만 있고, 논리/팩트 체크(Reviewer)가 없음
    Style Editor 단계가 없어서 말투 검수를 매번 수동으로 해야 함
    LLM 자기 검증이 미구현
    한 번 생성하면 끝. 피드백 기반 개선 루프가 형식적


2. 리팩토링 후 목표 구조

  에이전트 구조: 오케스트레이터 + 서브에이전트 3개

  Orchestrator (generator.py)
    전체 워크플로우 감독 및 조율
    서브에이전트 간 직접 호출 금지, 반드시 오케스트레이터를 통해 조율
    --quality 옵션에 따라 워크플로우 분기

  Writer 서브에이전트 (.claude/agents/writer/AGENT.md)
    역할: 플랫폼별 콘텐츠 초고 작성
    5개 플랫폼의 프롬프트 조합 + API 호출을 담당
    기존 platforms/ 로직을 흡수하되, Reviewer/Style Editor 피드백 반영 능력 추가
    스킬 참조: content-generator, style-reference

  Reviewer 서브에이전트 (.claude/agents/reviewer/AGENT.md)
    역할: 비판적/냉정한 논리 검토 + 팩트체크
    참고자료 대비 정확성 검증
    인터넷 검색으로 추가 팩트체크 (출처 넓게 허용, 출처 명시 필수)
    논리적 비약, 과장, 근거 없는 주장 지적
    피드백을 텍스트로 반환 (직접 수정하지 않음)

  Style Editor 서브에이전트 (.claude/agents/style-editor/AGENT.md)
    역할: 브랜드 톤/말투 검수
    voice-guide.md + writing-samples.md 기반으로 톤 적합성 평가
    금지 표현(~다/함/임 체) 검출 및 수정 피드백
    실무 인사이트 포함 여부 확인
    피드백을 텍스트로 반환 -> Writer가 재작성


3. 워크플로우 상세

  기본 모드 (--quality 없음 또는 --quality standard)

    1. 입력 검증 (스크립트)
    2. 참고자료 저장 (스크립트)
    3. 브랜드 컨텍스트 로드 (style-reference 스킬)
    4. 각 플랫폼별:
       4a. Writer가 콘텐츠 생성
       4b. validator.py로 규칙 기반 검증 (스키마 + 금지표현 + 글자수)
       4c. 검증 실패 시 피드백 포함 재생성 (최대 2회)
       4d. 저장

    API 호출: 플랫폼당 1-3회

  고품질 모드 (--quality high)

    1. 입력 검증 (스크립트)
    2. 참고자료 저장 (스크립트)
    3. 브랜드 컨텍스트 로드 (style-reference 스킬)
    4. 각 플랫폼별:
       4a. Writer가 콘텐츠 초고 생성
       4b. validator.py로 규칙 기반 검증
       4c. Reviewer가 논리/팩트 검토 + 인터넷 팩트체크
           피드백 반환
       4d. Writer가 Reviewer 피드백 반영하여 재작성
       4e. (4c-4d를 최대 1회 반복)
       4f. Style Editor가 톤/말투 검수
           피드백 반환
       4g. Writer가 Style Editor 피드백 반영하여 최종 작성
       4h. validator.py로 최종 규칙 검증
       4i. 저장

    API 호출: 플랫폼당 4-7회


4. 파일 구조 변경

  변경 전
    src/content_pipeline/
      platforms/
        base.py
        instagram_cardnews.py
        reels_scenario.py
        linkedin_post.py
        blog_post.py
        threads_post.py
      prompts/
        (각 플랫폼별 프롬프트)
      generator.py
      validator.py

  변경 후
    src/content_pipeline/
      platforms/              (유지 - Writer가 참조하는 프롬프트/생성 로직)
        base.py
        instagram_cardnews.py
        reels_scenario.py
        linkedin_post.py
        blog_post.py
        threads_post.py
      prompts/                (유지 - 플랫폼별 프롬프트 템플릿)
      agents/                 (신규 - 서브에이전트 Python 로직)
        writer.py             Writer 서브에이전트
        reviewer.py           Reviewer 서브에이전트
        style_editor.py       Style Editor 서브에이전트
      generator.py            (수정 - 오케스트레이터에 서브에이전트 호출 추가)
      validator.py            (유지 - 규칙 기반 검증)

    .claude/agents/           (신규 - 서브에이전트 설계 문서)
      writer/AGENT.md
      reviewer/AGENT.md
      style-editor/AGENT.md

    assets/brand/
      voice-guide.md          (유지)
      writing-samples.md      (신규 - 사용자 글쓰기 샘플)

    .claude/skills/
      style-reference/
        references/           (신규 - 검증 통과된 결과물 자동 축적)


5. 핵심 모듈 설계

  writer.py
    클래스: WriterAgent
    메서드:
      generate(client, topic, reference, platform, brand_context) -> str
        기존 PlatformGenerator.generate()를 래핑
        피드백이 있으면 참고자료에 추가하여 재생성

      revise(client, topic, reference, platform, brand_context, feedback) -> str
        피드백을 반영하여 콘텐츠 재작성
        시스템 프롬프트에 "다음 피드백을 반영하여 수정해주세요" 추가

  reviewer.py
    클래스: ReviewerAgent
    메서드:
      review(client, content, reference, topic) -> ReviewResult
        content를 읽고, reference 대비 정확성 검증
        논리적 비약, 과장, 근거 없는 주장 지적
        웹 검색으로 추가 팩트체크 (선택적)

      ReviewResult
        passed: bool
        feedback: str (수정 피드백)
        fact_issues: list[str] (팩트 오류 목록)
        logic_issues: list[str] (논리 문제 목록)

  style_editor.py
    클래스: StyleEditorAgent
    메서드:
      review_style(client, content, brand_guide, writing_samples) -> StyleResult
        voice-guide.md 기준으로 톤 적합성 평가
        writing-samples.md 기반 문체 일관성 체크
        금지 표현 검출
        실무 인사이트 포함 여부 확인

      StyleResult
        passed: bool
        feedback: str (톤/말투 수정 피드백)
        tone_score: int (1-10)
        forbidden_found: list[str]

      save_approved_sample(content, platform)
        검증 통과한 콘텐츠를 references/에 자동 저장


6. generator.py 수정 설계

  run() 함수 변경

    기존
      for platform in platforms:
        content = generator.generate(...)
        validation = validate_output(content, platform)
        save(content)

    변경
      quality_mode = "standard" or "high"

      for platform in platforms:
        # 1. Writer 초고 생성
        content = writer.generate(...)

        # 2. 규칙 검증
        validation = validate_output(content, platform)
        if not validation.passed:
          content = writer.revise(..., validation.suggestions)

        # 3. 고품질 모드일 때만
        if quality_mode == "high":
          # Reviewer 검토
          review = reviewer.review(client, content, reference, topic)
          if not review.passed:
            content = writer.revise(..., review.feedback)

          # Style Editor 검수
          style = style_editor.review_style(client, content, brand_guide, samples)
          if not style.passed:
            content = writer.revise(..., style.feedback)

          # 최종 규칙 검증
          final_validation = validate_output(content, platform)

        # 4. 저장
        save(content)

        # 5. 통과된 결과물 자동 축적 (고품질 모드)
        if quality_mode == "high":
          style_editor.save_approved_sample(content, platform)


7. CLI 변경

  추가 옵션
    --quality standard    기본. 생성 + 규칙 검증만 (현재와 동일)
    --quality high        풀 루프. Writer -> Reviewer -> Style Editor

  사용 예시
    contentpipe generate -t "주제" -r "참고자료" --all                    기본 모드
    contentpipe generate -t "주제" -r "참고자료" --all --quality high     고품질 모드


8. 데이터 전달 패턴

  서브에이전트 간 데이터 전달: 프롬프트 인라인 (콘텐츠 텍스트가 크지 않으므로)
  중간 산출물: 파일로 저장하지 않고 메모리에서 전달
  최종 산출물만 output/에 파일로 저장
  검증 통과된 샘플: .claude/skills/style-reference/references/에 자동 축적


9. 검증 패턴 정리

  단계별 검증 방식

  Writer 생성 후
    스키마 검증: 필수 섹션 존재 (스크립트, validator.py)
    규칙 기반: 글자수, 금지 표현 (스크립트, validator.py)

  Reviewer 검토 (고품질 모드)
    LLM 자기 검증: 논리 일관성, 팩트 정확성 (에이전트 판단)
    도구 활용: 인터넷 검색으로 팩트체크

  Style Editor 검수 (고품질 모드)
    LLM 자기 검증: 톤 적합성, 문체 일관성 (에이전트 판단)
    규칙 기반: 금지 표현 정규식 (스크립트, validator.py 재활용)

  실패 시 처리
    Writer 검증 실패: 자동 재시도 최대 2회
    Reviewer 검토 실패: Writer에게 피드백 전달, 재작성 1회
    Style Editor 검수 실패: Writer에게 피드백 전달, 재작성 1회
    전체 실패: 현재 결과 저장 + 경고 로그


10. 구현 순서

  Phase 1: 서브에이전트 Python 모듈
    src/content_pipeline/agents/writer.py
    src/content_pipeline/agents/reviewer.py
    src/content_pipeline/agents/style_editor.py

  Phase 2: 오케스트레이터 수정
    generator.py에 quality_mode 분기 추가
    서브에이전트 호출 로직 통합

  Phase 3: CLI 수정
    cli.py에 --quality 옵션 추가

  Phase 4: 에이전트 설계 문서
    .claude/agents/writer/AGENT.md
    .claude/agents/reviewer/AGENT.md
    .claude/agents/style-editor/AGENT.md

  Phase 5: 스타일 샘플 인프라
    assets/brand/writing-samples.md 초기 파일
    검증 통과 결과물 자동 축적 로직

  Phase 6: CLAUDE.md 업데이트
    리팩토링된 구조 반영
