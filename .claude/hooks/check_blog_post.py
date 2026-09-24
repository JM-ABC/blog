"""PostToolUse 훅: blog-post.txt 파일을 Write/Edit로 수정할 때마다 자동으로
validator.py를 돌려 통과 여부/이슈/바이트 수를 사용자에게 바로 보여준다.

CLAUDE.md 13-1번 규칙(validate_output(content, "blog") 호출 형식)을 그대로 따른다.
"""
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response") or {}
    file_path = tool_input.get("file_path") or tool_response.get("filePath")

    if not file_path or not file_path.replace("\\", "/").endswith("blog-post.txt"):
        return 0

    if not os.path.isfile(file_path):
        return 0

    sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
    try:
        from content_pipeline.validator import validate_output
    except Exception as e:
        print(f"[blog validator] validator.py를 불러오지 못했어요: {e}", file=sys.stderr)
        return 0

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    result = validate_output(content, "blog")
    byte_count = len(content.encode("utf-8"))

    lines = [f"[blog validator] {file_path}"]
    lines.append(f"passed: {result.passed}")
    if result.issues:
        for issue in result.issues:
            lines.append(f"  - {issue}")
    lines.append(f"bytes: {byte_count}")

    message = "\n".join(lines)

    # systemMessage는 성공한 훅이어도 사용자 화면에 항상 표시된다 (plain stdout은 조용히 묻힐 수 있음).
    # additionalContext는 다음 턴에 모델이 결과를 인지하도록 같이 넘긴다.
    output = {
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        },
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
