import time

import click

from .agents import WriterAgent, ReviewerAgent, StyleEditorAgent, StrategistAgent
from .asset_manager import AssetManager
from .client import ContentClient
from .config import Config
from .platforms import PLATFORM_MAP, ALL_PLATFORMS
from .utils import read_brand_context, read_file
from .validator import validate_output

MAX_VALIDATION_RETRIES = 2


def run(
    config: Config,
    topic: str,
    reference: str,
    platforms: list[str] | None = None,
    verbose: bool = False,
    quality: str = "standard",
) -> dict[str, str | None]:
    """모든 플랫폼에 대해 콘텐츠를 생성하고, 검증 후 저장"""
    platforms = platforms or ALL_PLATFORMS
    client = ContentClient(config)
    asset_mgr = AssetManager(config.assets_dir, config.output_dir)

    # 서브에이전트 초기화
    strategist = StrategistAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()
    style_editor = StyleEditorAgent()

    # 참고 자료 에셋으로 저장
    topic_dir = asset_mgr.save_input(topic, reference, platforms)
    click.echo(f"\n참고 자료 저장 완료 -> {topic_dir}")

    # 브랜드 컨텍스트 로드
    brand_context = read_brand_context(config.brand_dir)
    brand_guide_path = config.brand_dir / "voice-guide.md"
    brand_guide = read_file(brand_guide_path) if brand_guide_path.exists() else ""
    writing_samples = style_editor.load_writing_samples(config.brand_dir)

    # Strategist: 주제 분석 및 글 구조 기획
    click.echo("\n  [Strategist] 주제 분석 및 기획 중 ... ", nl=False)
    _start = time.time()
    try:
        brief = strategist.analyze(client, topic, reference, platforms)
        strategy_text = brief.to_prompt_text() if brief.topic_analysis else ""
        click.secho(f"완료 ({time.time() - _start:.1f}초)", fg="green")
        if brief.unique_angle:
            click.echo(f"     차별화 관점: {brief.unique_angle[:60]}...")
    except Exception as e:
        click.secho(f"스킵 - {e}", fg="yellow")
        strategy_text = ""

    mode_label = "고품질" if quality == "high" else "기본"
    click.echo(f"\n콘텐츠 생성 시작 ({len(platforms)}개 플랫폼, {mode_label} 모드):")
    click.echo("=" * 50)

    results: dict[str, str | None] = {}
    total = len(platforms)

    for i, platform_key in enumerate(platforms, 1):
        if platform_key not in PLATFORM_MAP:
            click.echo(f"  [{i}/{total}] {platform_key} ... 알 수 없는 플랫폼 (건너뜀)")
            results[platform_key] = None
            continue

        platform_name = PLATFORM_MAP[platform_key]().platform_name
        click.echo(f"\n  [{i}/{total}] {platform_name}")

        content = _generate_for_platform(
            client=client,
            writer=writer,
            reviewer=reviewer,
            style_editor=style_editor,
            topic=topic,
            reference=reference,
            strategy_text=strategy_text,
            platform=platform_key,
            brand_context=brand_context,
            brand_guide=brand_guide,
            writing_samples=writing_samples,
            quality=quality,
            verbose=verbose,
        )

        if content:
            output_path = asset_mgr.save_output(topic, PLATFORM_MAP[platform_key]().file_name, content)
            if verbose:
                click.echo(f"         -> {output_path}")
            results[platform_key] = str(output_path)

            # 고품질 모드에서 통과된 결과물 자동 축적
            if quality == "high":
                refs_dir = config.project_root / ".claude" / "skills" / "style-reference" / "references"
                style_editor.save_approved_sample(content, platform_key, refs_dir)
        else:
            results[platform_key] = None

    # 결과 요약
    click.echo("\n" + "=" * 50)
    success = sum(1 for v in results.values() if v is not None)
    click.echo(f"\n결과: {success}/{total} 플랫폼 생성 완료")

    if success < total:
        failed = [k for k, v in results.items() if v is None]
        click.echo(f"실패: {', '.join(failed)}")
        click.echo(f"재시도: contentpipe generate -t \"{topic}\" -p {','.join(failed)}")

    return results


def _generate_for_platform(
    client: ContentClient,
    writer: WriterAgent,
    reviewer: ReviewerAgent,
    style_editor: StyleEditorAgent,
    topic: str,
    reference: str,
    strategy_text: str,
    platform: str,
    brand_context: str,
    brand_guide: str,
    writing_samples: str,
    quality: str,
    verbose: bool,
) -> str | None:
    """단일 플랫폼에 대한 전체 생성 파이프라인"""

    # Strategist 브리프를 Writer용 reference 앞에 붙임 (Reviewer는 원본 reference 사용)
    writer_reference = f"{strategy_text}\n\n[원본 참고자료]\n{reference}" if strategy_text else reference

    # Step 1: Writer 초고 생성
    click.echo("         [Writer] 초고 생성 중 ... ", nl=False)
    start = time.time()
    try:
        content = writer.generate(client, topic, writer_reference, platform, brand_context)
        click.secho(f"완료 ({time.time() - start:.1f}초)", fg="green")
    except Exception as e:
        click.secho(f"실패 - {e}", fg="red")
        return None

    # Step 2: 규칙 기반 검증 + 재시도
    for attempt in range(MAX_VALIDATION_RETRIES + 1):
        click.echo("         [Validator] 규칙 검증 중 ... ", nl=False)
        validation = validate_output(content, platform)

        if validation.passed:
            click.secho("통과", fg="green")
            break
        else:
            click.secho(f"실패 ({len(validation.issues)}건)", fg="yellow")
            for issue in validation.issues:
                click.echo(f"           - {issue}")

            if attempt < MAX_VALIDATION_RETRIES:
                click.echo("         [Writer] 피드백 반영 재작성 중 ... ", nl=False)
                start = time.time()
                try:
                    content = writer.revise(
                        client, topic, writer_reference, platform,
                        brand_context, content, validation.suggestions,
                    )
                    click.secho(f"완료 ({time.time() - start:.1f}초)", fg="green")
                except Exception as e:
                    click.secho(f"실패 - {e}", fg="red")
                    break
            else:
                click.secho("         최대 재시도 초과. 현재 결과를 저장해요.", fg="yellow")

    # 기본 모드는 여기서 종료
    if quality != "high":
        click.echo("         저장 완료")
        return content

    # Step 3: Reviewer 논리/팩트 검토 (고품질 모드)
    click.echo("         [Reviewer] 논리/팩트 검토 중 ... ", nl=False)
    start = time.time()
    try:
        review = reviewer.review(client, content, reference, topic)
        elapsed = time.time() - start

        if review.passed:
            click.secho(f"통과 ({elapsed:.1f}초)", fg="green")
        else:
            click.secho(f"피드백 있음 ({elapsed:.1f}초)", fg="yellow")
            if review.fact_issues:
                for issue in review.fact_issues:
                    click.echo(f"           팩트: {issue}")
            if review.logic_issues:
                for issue in review.logic_issues:
                    click.echo(f"           논리: {issue}")

            # Writer 재작성
            click.echo("         [Writer] Reviewer 피드백 반영 중 ... ", nl=False)
            start = time.time()
            content = writer.revise(
                client, topic, writer_reference, platform,
                brand_context, content, review.feedback,
            )
            click.secho(f"완료 ({time.time() - start:.1f}초)", fg="green")
    except Exception as e:
        click.secho(f"스킵 - {e}", fg="yellow")

    # Step 4: Style Editor 톤/말투 검수 (고품질 모드)
    click.echo("         [Style Editor] 톤/말투 검수 중 ... ", nl=False)
    start = time.time()
    try:
        style = style_editor.review_style(client, content, brand_guide, writing_samples)
        elapsed = time.time() - start

        if style.passed:
            click.secho(f"통과 (톤 {style.tone_score}/10, {elapsed:.1f}초)", fg="green")
        else:
            click.secho(f"피드백 있음 (톤 {style.tone_score}/10, {elapsed:.1f}초)", fg="yellow")
            if style.forbidden_found:
                click.echo(f"           금지 표현: {', '.join(style.forbidden_found[:3])}")

            # Writer 재작성
            click.echo("         [Writer] Style 피드백 반영 중 ... ", nl=False)
            start = time.time()
            content = writer.revise(
                client, topic, writer_reference, platform,
                brand_context, content, style.feedback,
            )
            click.secho(f"완료 ({time.time() - start:.1f}초)", fg="green")
    except Exception as e:
        click.secho(f"스킵 - {e}", fg="yellow")

    # Step 5: 최종 규칙 검증
    click.echo("         [Validator] 최종 검증 중 ... ", nl=False)
    final = validate_output(content, platform)
    if final.passed:
        click.secho("통과", fg="green")
    else:
        click.secho(f"경고 ({len(final.issues)}건) - 저장은 진행해요", fg="yellow")

    click.echo("         저장 완료")
    return content
