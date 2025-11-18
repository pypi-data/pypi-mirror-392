"""Instrument Claude Code SDK (deprecated)."""

import asyncio
import os

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient

from atla_insights import configure, instrument, instrument_claude_code_sdk


@instrument("My Claude Code SDK application")
async def my_app() -> None:
    """My Claude Code SDK application."""
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a performance engineer",
            allowed_tools=["Bash", "Read", "WebSearch"],
            max_turns=3,
        )
    ) as client:
        await client.query("Analyze system performance")

        async for message in client.receive_response():
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(block.text)


async def main() -> None:
    """Main function.

    NOTE: The `claude-code-sdk` library is deprecated in favor of the `claude-agent-sdk`
    library.

    Please visit [Anthopric's migration guide](https://docs.claude.com/en/docs/claude-code/sdk/migration-guide)
    for more information.
    """
    # Configure the client
    configure(token=os.environ["ATLA_INSIGHTS_TOKEN"])

    # Instrument the Claude Code SDK
    instrument_claude_code_sdk()

    # Calling the instrumented function will create spans behind the scenes
    await my_app()


if __name__ == "__main__":
    asyncio.run(main())
