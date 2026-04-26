from abc import ABC, abstractmethod

from ..client import ContentClient
from ..prompts.base_system import get_base_system


class PlatformGenerator(ABC):
    platform_name: str
    file_name: str

    @abstractmethod
    def _get_system_prompt(self) -> str:
        ...

    @abstractmethod
    def _get_user_prompt(self, topic: str, reference: str) -> str:
        ...

    def generate(self, client: ContentClient, topic: str, reference: str, brand_context: str = "") -> str:
        base = get_base_system(brand_context)
        platform_system = self._get_system_prompt()
        system_prompt = f"{base}\n\n{platform_system}"
        user_prompt = self._get_user_prompt(topic, reference)
        return client.generate(system_prompt, user_prompt)
