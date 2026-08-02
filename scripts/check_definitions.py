"""블로그 원고 검증 실행 스크립트.

validate_output(content, platform) 인자 순서와 플랫폼 키('blog')를 고정해두어
호출 실수로 검증이 무력화되는 것을 막는다.

용어 정의(※) 배치 규칙이 실제로 작동하는지도 함께 회귀 테스트한다.
  ① 본문에 없는 용어를 정의만 해둔 경우
  ② 정의가 용어 첫 등장보다 앞에 오는 경우
"""
import sys

sys.path.insert(0, "src")
from content_pipeline.validator import validate_output

PATH = r"output\K뷰티-수출최대-관세리스크_20260802\blog-post.txt"
PLATFORM = "blog"

text = open(PATH, encoding="utf-8").read()


def report(label, content):
    result = validate_output(content, PLATFORM)
    print(f"{label}: passed={result.passed}")
    for i, issue in enumerate(result.issues, 1):
        print(f"   {i}. {issue}")
    return result


report("[1] 현재 원고", text)

print()
broken = text.replace(
    "■ 프라임데이 나흘이 보여준 성적표",
    "※역직구란, 국내 사업자가 해외 소비자에게 온라인으로 직접 판매하는 방식을 말해요.\n\n"
    "■ 프라임데이 나흘이 보여준 성적표",
    1,
)
issues = validate_output(broken, PLATFORM).issues
caught = [i for i in issues if "역직구" in i]
print("[2] 본문에 없는 용어 정의 삽입 -> 검출:", caught or "실패")

print()
definition = (
    "※인디브랜드란, 대기업 계열이 아닌 중소·신생 화장품 브랜드를 말해요. "
    "자체 공장 없이 기획과 마케팅에 집중하고 생산은 외부 전문 제조사에 맡기는 구조가 일반적이에요."
)
moved = text.replace(definition + "\n\n", "", 1).replace(
    "■ 70억 달러라는 숫자", definition + "\n\n■ 70억 달러라는 숫자", 1
)
issues = validate_output(moved, PLATFORM).issues
caught = [i for i in issues if "위치 오류" in i]
print("[3] 정의를 첫 등장 앞으로 이동 -> 검출:", caught or "실패")
