from .base import PlatformGenerator
from ..prompts import linkedin_post as prompts


class LinkedinPostGenerator(PlatformGenerator):
    platform_name = "LinkedIn 포스트"
    file_name = "linkedin-post"

    def _get_system_prompt(self) -> str:
        return prompts.SYSTEM

    def _get_user_prompt(self, topic: str, reference: str) -> str:
        return prompts.get_user_prompt(topic, reference)
