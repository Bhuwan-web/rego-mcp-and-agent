import os
import sys
import dspy
import dotenv
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import pydantic
dotenv.load_dotenv()  # Load environment variables from .env file

lm=dspy.LM("deepseek/deepseek-v4-flash",api_key=os.environ.get("MODEL_API_KEY"),api_url=os.environ.get("MODEL_API_BASE"))
dspy.configure(lm=lm)

class PolicyInputSchema(pydantic.BaseModel):
    method: str
    url: str
    host: str
    user_agent: str

class ResponseSchema(pydantic.BaseModel):
    success: bool
    message: str

class PolicySignature(dspy.Signature):
    """
    - **query** is the user query for policy generation, it should be a natural language description of the policy requirements and constraints.
    - generate OPA policy based on Rego language V1 syntax."""
    query: str = dspy.InputField(desc="user query for policy generation")
    input: dict = dspy.InputField(desc="pydantic schema for policy input. The test example should match the schema.")
    output: ResponseSchema = dspy.OutputField(desc="output of the policy evaluation")

policy_generator = dspy.Predict(PolicySignature)

async def generate_policy(query: str) -> ResponseSchema:
    input_schema = PolicyInputSchema.model_json_schema()
    response = policy_generator(query=query, input=input_schema)
    return response.output.message

async def get_policy_input_schema():
    return PolicyInputSchema.model_json_schema()

async def main(query: str):
    # Use stdio_client for MCP connection
    server_params = StdioServerParameters(
        command="python",
        args=["../server.py"],
        env=None,
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List and convert tools
            response = await session.list_tools()
            dspy_tools = [
                dspy.Tool.from_mcp_tool(session, tool)
                for tool in response.tools
            ]

            react_agent = dspy.ReAct(
                signature=PolicySignature,
                tools=dspy_tools,
                max_iters=5
            )
            policy_input_schema = await get_policy_input_schema()
            result = await react_agent.acall(query=query, input=policy_input_schema)
            print(result)

if __name__ == "__main__":
    DUMMY_QUERY = "only allow put and post request for github.com"
    user_request = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DUMMY_QUERY
    print(f"Generating policy for user query: {user_request}")
    response = asyncio.run(main(user_request))
