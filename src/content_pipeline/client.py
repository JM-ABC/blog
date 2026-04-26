import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import Config


class ContentClient:
    def __init__(self, config: Config):
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.model = config.model
        self.max_tokens = config.max_tokens

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIConnectionError)),
    )
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except anthropic.AuthenticationError:
            raise SystemExit(
                "API 키가 유효하지 않습니다. .env 파일의 ANTHROPIC_API_KEY를 확인하세요."
            )
