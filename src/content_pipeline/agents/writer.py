from ..client import ContentClient
from ..platforms import PLATFORM_MAP
from ..prompts.base_system import get_base_system


class WriterAgent:
    """콘텐츠 초고 생성 + 피드백 반영 재작성을 담당하는 서브에이전트"""

    def generate(
        self,
        client: ContentClient,
        topic: str,
        reference: str,
        platform: str,
        brand_context: str = "",
    ) -> str:
        generator_cls = PLATFORM_MAP[platform]
        generator = generator_cls()
        return generator.generate(client, topic, reference, brand_context)

    def revise(
        self,
        client: ContentClient,
        topic: str,
        reference: str,
        platform: str,
        brand_context: str,
        previous_content: str,
        feedback: str,
    ) -> str:
        generator_cls = PLATFORM_MAP[platform]
        generator = generator_cls()

        base_system = get_base_system(brand_context)
        platform_system = generator._get_system_prompt()
        system_prompt = f"{base_system}\n\n{platform_system}"

        user_prompt = f"""이전에 작성한 콘텐츠를 아래 피드백을 반영하여 수정해주세요.

--- 수정 피드백 ---
{feedback}

--- 이전 콘텐츠 ---
{previous_content}

--- 원본 주제 ---
{topic}

--- 참고 자료 ---
{reference}

피드백을 꼼꼼히 반영하여 콘텐츠를 처음부터 다시 작성해주세요."""

        return client.generate(system_prompt, user_prompt)
