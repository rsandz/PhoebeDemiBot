from datetime import datetime
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.agents import tool, AgentExecutor
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

from discord.utils import get

load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

async def get_points_with_context(ctx):
    myRoles = ctx.author.roles
    rolePoints = 10
    if (get(ctx.guild.roles, name='Ya Boi') in myRoles):
        rolePoints = 100000
    elif (get(ctx.guild.roles, name='SPICY Bubble Tea Buddy') in myRoles):
        rolePoints = 500
    elif (get(ctx.guild.roles, name='Bubble Tea Buddy') in myRoles):
        rolePoints = 250
    elif (get(ctx.guild.roles, name='Popsicle Pal') in myRoles):
        rolePoints = 100
    elif (get(ctx.guild.roles, name='From the Far Future') in myRoles):
        rolePoints = 20
    elif (get(ctx.guild.roles, name='From Another Realm') in myRoles):
        rolePoints = 20
    
    agePoints = (datetime.now() - ctx.author.joined_at.replace(tzinfo=None)).days

    messagePoints = 0
    async for message in ctx.channel.history(limit = 1000):
        if message.author == ctx.author:
            messagePoints += 1
            if messagePoints >= 200:
                break

    desc = "Total Points: " + str(rolePoints + agePoints + messagePoints)
    desc += "\n\nRole Points: " + str(rolePoints)
    desc += "\nTime in Server Points: " + str(agePoints)
    desc += "\nMessage Points: " + str(messagePoints)

    return desc


template = """
You are a helpful discord bot. You play as 2 characters: Phoebe and Demi.
Answer in a casual and light hearted manner. Use emojis liberally.
If you don't know the answer to a question, just say that you don't know, don't try to make up an answer.
"""
human_template = "{text}"

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        ("user", human_template),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# enable langchain tracing
LANGCHAIN_TRACING = True

async def llm_invoke(ctx, *args):

    @tool(return_direct=True)
    async def get_points():
        """Get the discords points for the user."""
        return await get_points_with_context(ctx)

    tools = [get_points]

    llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

    agent = (
        {
            "text": lambda x: x["text"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
        }
        | chat_prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agentExecutor = AgentExecutor(agent=agent, tools=tools, max_iterations=2, verbose=True)

    return (await agentExecutor.ainvoke({
        "text": " ".join(args)
    })).get("output")
