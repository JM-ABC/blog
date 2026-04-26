from .base import PlatformGenerator
from ..prompts import blog_post as prompts


class BlogPostGenerator(PlatformGenerator):
    platform_name = "블로그 포스트"
    file_name = "blog-post"

    def _get_system_prompt(self) -> str:
        return prompts.SYSTEM

    def _get_user_prompt(self, topic: str, reference: str) -> str:
        return prompts.get_user_prompt(topic, reference)
