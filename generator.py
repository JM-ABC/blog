"""블로그 콘텐츠 생성 모듈: URL 크롤링 + Claude API 콘텐츠 생성"""

import os
import re
from datetime import datetime

import anthropic
import requests
from bs4 import BeautifulSoup


def fetch_url_content(url: str) -> dict:
    """URL에서 제목, 본문 텍스트, 메타 정보를 추출한다."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding

    soup = BeautifulSoup(resp.text, "html.parser")

    # 불필요한 태그 제거
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    # 메타 설명
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()

    # 본문 텍스트 추출 (article > body 순서)
    article = soup.find("article")
    body = article if article else soup.find("body")
    text = body.get_text(separator="\n", strip=True) if body else ""

    # 연속 빈줄 정리 & 길이 제한
    text = re.sub(r"\n{3,}", "\n\n", text)
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...(truncated)"

    return {"url": url, "title": title, "meta_description": meta_desc, "text": text}


def fetch_multiple_urls(urls: list[str]) -> list[dict]:
    """여러 URL을 크롤링하고 결과 리스트를 반환한다."""
    results = []
    for url in urls:
        try:
            data = fetch_url_content(url)
            results.append(data)
            print(f"  [OK] {url}")
        except Exception as e:
            print(f"  [FAIL] {url} — {e}")
            results.append({"url": url, "title": "", "text": "", "error": str(e)})
    return results


CONTENT_TYPES = {
    "blog": {
        "label": "블로그 포스트",
        "instruction": (
            "SEO에 최적화된 블로그 포스트를 작성해 주세요.\n"
            "- Markdown 형식\n"
            "- H1 제목, 서론, 본문(H2/H3 소제목 활용), 결론 구조\n"
            "- 독자가 실질적으로 활용할 수 있는 정보 중심\n"
            "- 자연스러운 한국어, 1500~3000자 분량"
        ),
    },
    "sns": {
        "label": "SNS 게시글",
        "instruction": (
            "SNS(트위터/인스타그램/링크드인)에 올릴 수 있는 짧은 게시글을 작성해 주세요.\n"
            "- 각 플랫폼별로 1개씩, 총 3개\n"
            "- 해시태그 포함\n"
            "- 핵심 메시지를 간결하게 전달\n"
            "- Markdown 형식으로 구분"
        ),
    },
    "summary": {
        "label": "요약 정리",
        "instruction": (
            "참고자료를 바탕으로 핵심 요약 문서를 작성해 주세요.\n"
            "- Markdown 형식\n"
            "- 주요 포인트를 불릿으로 정리\n"
            "- 원문 출처 표시\n"
            "- 500~1000자 분량"
        ),
    },
}


def build_prompt(topic: str, content_type: str, references: list[dict]) -> str:
    """Claude API에 전달할 프롬프트를 조립한다."""
    ct = CONTENT_TYPES.get(content_type, CONTENT_TYPES["blog"])

    ref_block = ""
    for i, ref in enumerate(references, 1):
        if ref.get("error"):
            continue
        ref_block += (
            f"\n---\n"
            f"### 참고자료 {i}\n"
            f"- URL: {ref['url']}\n"
            f"- 제목: {ref['title']}\n"
            f"- 요약: {ref['meta_description']}\n"
            f"- 본문:\n{ref['text']}\n"
        )

    prompt = (
        f"## 요청\n"
        f"주제: **{topic}**\n"
        f"콘텐츠 유형: {ct['label']}\n\n"
        f"## 작성 지침\n{ct['instruction']}\n\n"
        f"## 참고자료\n{ref_block if ref_block else '(참고자료 없음)'}\n\n"
        f"위 참고자료를 바탕으로 콘텐츠를 작성해 주세요. "
        f"참고자료의 문장을 그대로 복사하지 말고 자신의 언어로 재구성하세요."
    )
    return prompt


def generate_content(
    topic: str,
    content_type: str,
    references: list[dict],
    model: str | None = None,
) -> str:
    """Claude API를 호출해 콘텐츠를 생성한다."""
    model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 환경변수 자동 사용

    prompt = build_prompt(topic, content_type, references)

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def save_output(content: str, topic: str, content_type: str, output_dir: str = None) -> str:
    """생성된 콘텐츠를 .md 파일로 저장하고 파일 경로를 반환한다."""
    output_dir = output_dir or os.getenv("OUTPUT_DIR", "output")
    os.makedirs(output_dir, exist_ok=True)

    # 파일명 생성: 날짜_주제_유형.md
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = re.sub(r"[^\w가-힣\s-]", "", topic).strip().replace(" ", "_")[:30]
    filename = f"{date_str}_{safe_topic}_{content_type}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
