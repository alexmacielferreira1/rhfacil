from app.modules.ai.gateway import AIResult


class AIProviderUnavailable(Exception):
    """Raised when no external AI provider is enabled."""


class DisabledAIProvider:
    provider_name = 'disabled'
    model_name = 'none'

    async def generate(self, *, prompt: str, max_output_tokens: int) -> AIResult:
        del prompt, max_output_tokens
        raise AIProviderUnavailable
