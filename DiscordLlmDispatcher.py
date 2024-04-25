from phoebe_demi_bot_llm import LlmDispatcher, Context

class DiscordLlmDispatcherFactory:
    def __init__(self, discord_client):
        self.tools = []
        self.terminal_tools = []
        self.discord_client = discord_client

    def add_discord_command_as_tool(self, command, description):

        async def command_wrapper(context: Context):
            discord_context = context.discord_context
            print(f"Invoking command: {command}")
            return (await self.discord_client.get_command(command).invoke(discord_context))
        command_wrapper.__doc__ = description
        command_wrapper.__name__ = command

        self.terminal_tools.append(command_wrapper)

        return self

    def build(self):
        return LlmDispatcher(tools=self.tools, terminal_tools=self.terminal_tools)