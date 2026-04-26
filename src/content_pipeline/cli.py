import sys
from pathlib import Path

import click

from .config import load_config
from .platforms import ALL_PLATFORMS


@click.group()
@click.version_option(package_name="content-pipeline")
def main():
    """콘텐츠 파이프라인 - 주제를 입력하면 5개 플랫폼용 콘텐츠를 자동 생성합니다."""
    pass


@main.command()
@click.option("-t", "--topic", type=str, help="콘텐츠 주제")
@click.option("-r", "--reference", type=str, multiple=True, help="참고 자료 텍스트 (여러 개 가능)")
@click.option("-f", "--reference-file", type=click.Path(exists=True), multiple=True, help="참고 자료 파일 경로")
@click.option("-p", "--platforms", type=str, help=f"플랫폼 (쉼표 구분: {','.join(ALL_PLATFORMS)})")
@click.option("-a", "--all", "all_platforms", is_flag=True, help="전체 플랫폼 생성")
@click.option("-v", "--verbose", is_flag=True, help="상세 출력")
@click.option("--dry-run", is_flag=True, help="API 호출 없이 설정만 확인")
@click.option("-q", "--quality", type=click.Choice(["standard", "high"]), default="standard",
              help="품질 모드: standard(기본, 검증만) / high(Reviewer+Style Editor 풀 루프)")
def generate(topic, reference, reference_file, platforms, all_platforms, verbose, dry_run, quality):
    """콘텐츠를 생성합니다. 인자 없이 실행하면 인터랙티브 모드로 진입합니다."""
    # 인터랙티브 모드
    if not topic:
        topic = click.prompt("\n콘텐츠 주제를 입력하세요")

    if not reference and not reference_file:
        click.echo("\n참고 자료를 붙여넣으세요 (빈 줄 2번으로 종료):")
        lines = []
        empty_count = 0
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append("")
            else:
                empty_count = 0
                lines.append(line)
        reference = (("\n".join(lines)).strip(),)
        if not reference[0]:
            click.echo("참고 자료 없이 주제만으로 콘텐츠를 생성합니다.")
            reference = (topic,)

    # 참고 자료 합치기
    ref_parts = list(reference)
    for f in reference_file:
        ref_parts.append(Path(f).read_text(encoding="utf-8"))
    combined_reference = "\n\n---\n\n".join(ref_parts)

    # 플랫폼 결정
    if all_platforms or not platforms:
        if not all_platforms and not platforms:
            choices = click.prompt(
                f"\n플랫폼 선택 (쉼표 구분, 'all' = 전체)\n  사용 가능: {', '.join(ALL_PLATFORMS)}",
                default="all",
            )
            if choices.strip().lower() == "all":
                target_platforms = ALL_PLATFORMS
            else:
                target_platforms = [p.strip() for p in choices.split(",")]
        else:
            target_platforms = ALL_PLATFORMS
    else:
        target_platforms = [p.strip() for p in platforms.split(",")]

    # 유효성 검사
    invalid = [p for p in target_platforms if p not in ALL_PLATFORMS]
    if invalid:
        click.secho(f"알 수 없는 플랫폼: {', '.join(invalid)}", fg="red")
        click.echo(f"사용 가능: {', '.join(ALL_PLATFORMS)}")
        sys.exit(1)

    # 설정 로드
    config = load_config()

    click.echo(f"\n{'='*50}")
    click.echo(f"주제: {topic}")
    click.echo(f"플랫폼: {', '.join(target_platforms)}")
    click.echo(f"모델: {config.model}")
    mode_label = "고품질 (Writer->Reviewer->Style Editor)" if quality == "high" else "기본 (검증만)"
    click.echo(f"품질: {mode_label}")
    click.echo(f"{'='*50}")

    if dry_run:
        click.echo("\n[dry-run] API 호출 없이 종료합니다.")
        return

    # 생성 실행
    from .generator import run
    run(config, topic, combined_reference, target_platforms, verbose, quality)


@main.command("list")
@click.option("--topics", is_flag=True, help="저장된 토픽 목록")
@click.option("--outputs", is_flag=True, help="생성된 출력 목록")
def list_cmd(topics, outputs):
    """저장된 토픽 및 출력 목록을 확인합니다."""
    config = load_config()
    from .asset_manager import AssetManager
    mgr = AssetManager(config.assets_dir, config.output_dir)

    if not topics and not outputs:
        topics = outputs = True

    if topics:
        click.echo("\n📁 저장된 토픽:")
        items = mgr.list_topics()
        if not items:
            click.echo("  (없음)")
        for item in items:
            click.echo(f"  - {item['topic']} ({item['date']}) [{', '.join(item.get('platforms', []))}]")

    if outputs:
        click.echo("\n📄 생성된 출력:")
        items = mgr.list_outputs()
        if not items:
            click.echo("  (없음)")
        for item in items:
            click.echo(f"  - {item['slug']}: {', '.join(item['platforms'])}")


@main.command()
@click.argument("slug")
@click.argument("platform")
def show(slug, platform):
    """생성된 콘텐츠를 터미널에 출력합니다."""
    config = load_config()
    from .asset_manager import AssetManager
    mgr = AssetManager(config.assets_dir, config.output_dir)

    content = mgr.read_output(slug, platform)
    if content is None:
        # slug 부분 매칭 시도
        for item in mgr.list_outputs():
            if slug in item["slug"]:
                content = mgr.read_output(item["slug"], platform)
                if content:
                    break

    if content is None:
        click.secho(f"'{slug}/{platform}.md' 파일을 찾을 수 없습니다.", fg="red")
        click.echo("\n사용 가능한 출력:")
        for item in mgr.list_outputs():
            click.echo(f"  - {item['slug']}: {', '.join(item['platforms'])}")
        sys.exit(1)

    click.echo(content)
