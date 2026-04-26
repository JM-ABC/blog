"""블로그 콘텐츠 생성 도구 — CLI 진입점"""

import argparse
import sys

from dotenv import load_dotenv

from generator import (
    CONTENT_TYPES,
    fetch_multiple_urls,
    generate_content,
    save_output,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="블로그 콘텐츠 생성 도구 — 주제와 참고 URL을 입력하면 콘텐츠를 생성합니다."
    )
    parser.add_argument("topic", help="콘텐츠 주제 (예: 'Python 비동기 프로그래밍')")
    parser.add_argument(
        "-u", "--urls",
        nargs="+",
        default=[],
        help="참고 URL 목록 (공백으로 구분)",
    )
    parser.add_argument(
        "-t", "--type",
        choices=list(CONTENT_TYPES.keys()),
        default="blog",
        help="콘텐츠 유형 (기본값: blog)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="출력 폴더 (기본값: output)",
    )
    parser.add_argument(
        "-m", "--model",
        default=None,
        help="Claude 모델 (기본값: .env 설정 또는 claude-sonnet-4-5-20250929)",
    )
    return parser.parse_args()


def run_interactive():
    """인자 없이 실행 시 대화형 모드."""
    print("=" * 50)
    print("  블로그 콘텐츠 생성 도구")
    print("=" * 50)

    topic = input("\n주제를 입력하세요: ").strip()
    if not topic:
        print("주제를 입력해야 합니다.")
        sys.exit(1)

    urls_input = input("참고 URL을 입력하세요 (쉼표 또는 공백으로 구분, 없으면 Enter): ").strip()
    urls = [u.strip() for u in urls_input.replace(",", " ").split() if u.strip()] if urls_input else []

    print("\n콘텐츠 유형:")
    for key, val in CONTENT_TYPES.items():
        print(f"  {key:10s} — {val['label']}")
    content_type = input("유형을 선택하세요 (기본값: blog): ").strip() or "blog"
    if content_type not in CONTENT_TYPES:
        print(f"알 수 없는 유형: {content_type}")
        sys.exit(1)

    return topic, urls, content_type, None, None


def main():
    load_dotenv()

    # 인자가 없으면 대화형 모드
    if len(sys.argv) == 1:
        topic, urls, content_type, output_dir, model = run_interactive()
    else:
        args = parse_args()
        topic, urls, content_type = args.topic, args.urls, args.type
        output_dir, model = args.output_dir, args.model

    # 1. URL 크롤링
    references = []
    if urls:
        print(f"\n참고 URL {len(urls)}개 수집 중...")
        references = fetch_multiple_urls(urls)
    else:
        print("\n참고 URL 없이 주제만으로 생성합니다.")

    # 2. 콘텐츠 생성
    ct_label = CONTENT_TYPES[content_type]["label"]
    print(f"\n'{topic}' 주제로 {ct_label} 생성 중...")
    try:
        content = generate_content(topic, content_type, references, model=model)
    except Exception as e:
        print(f"\n콘텐츠 생성 실패: {e}")
        sys.exit(1)

    # 3. 파일 저장
    filepath = save_output(content, topic, content_type, output_dir=output_dir)
    print(f"\n저장 완료: {filepath}")
    print("-" * 50)
    print(content[:500])
    if len(content) > 500:
        print(f"\n... (총 {len(content)}자, 전체 내용은 파일에서 확인)")


if __name__ == "__main__":
    main()
