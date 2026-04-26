from .base import PlatformGenerator
from ..prompts import instagram_cardnews as prompts


class InstagramCardnewsGenerator(PlatformGenerator):
    platform_name = "인스타그램 카드뉴스"
    file_name = "instagram-cardnews"

    def _get_system_prompt(self) -> str:
        return prompts.SYSTEM

    def _get_user_prompt(self, topic: str, reference: str) -> str:
        return prompts.get_user_prompt(topic, reference)
