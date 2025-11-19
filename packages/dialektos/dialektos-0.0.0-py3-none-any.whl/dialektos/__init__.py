import asyncio
from dataclasses import dataclass
from enum import StrEnum

from litellm import acompletion
from litellm.types.utils import Message as MessageLitellm


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class Message:
    role: MessageRole
    content: str | None = None

    def _to_litellm_message(self) -> MessageLitellm:
        return MessageLitellm(
            role=self.role.value,
            content=self.content)


async def chat_loop() -> None:
    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="You are a helpful AI assistant")]

    while True:
        user_input = input("USER: ")
        messages.append(Message(
            role=MessageRole.USER,
            content=user_input))
        response = await acompletion(
            model="deepseek/deepseek-chat",
            messages=[m._to_litellm_message() for m in messages],
            temperature=1.0,
            max_tokens=1000)
        response_text = response.choices[0].message.content
        print(f"ASSISTANT: {response_text}")
        messages.append(Message(
            role=MessageRole.ASSISTANT,
            content=response_text))

def main() -> None:
    asyncio.run(chat_loop())
