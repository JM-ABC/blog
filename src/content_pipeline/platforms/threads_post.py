from .base import PlatformGenerator
from ..prompts import threads_post as prompts


class ThreadsPostGenerator(PlatformGenerator):
    platform_name = "Threads 포스트"
    file_name = "threads-post"

    def _get_system_prompt(self) -> str:
        return prompts.SYSTEM

    def _get_user_prompt(self, topic: str, reference: str) -> str:
        return prompts.get_user_prompt(topic, reference)
