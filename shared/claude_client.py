import anthropic

_MAX_USER_CHARS = 400_000  # ~100K tokens


class ClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 4096,
    ) -> str:
        suffix = "\n\n[TRUNCATED: diff too large, showing first 400K chars]"
        if len(user) > _MAX_USER_CHARS:
            user = user[:_MAX_USER_CHARS - len(suffix)] + suffix

        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        if not response.content:
            raise ValueError("Empty response from Claude API")

        return response.content[0].text
