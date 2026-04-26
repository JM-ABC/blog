from .base import PlatformGenerator
from ..prompts import reels_scenario as prompts


class ReelsScenarioGenerator(PlatformGenerator):
    platform_name = "릴스 시나리오"
    file_name = "reels-scenario"

    def _get_system_prompt(self) -> str:
        return prompts.SYSTEM

    def _get_user_prompt(self, topic: str, reference: str) -> str:
        return prompts.get_user_prompt(topic, reference)
