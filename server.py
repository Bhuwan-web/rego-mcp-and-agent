import subprocess
import os
import json 
import aiofile
import fastmcp


mcp = fastmcp.FastMCP(
    "Self Harnessing OPA V1 Policy Generation and Testing MCP",
    instructions="""
    - call `get_skill_context` to get the context for policy generation, which includes the policy requirements and constraints.
    - call `test_rego` to test the generated OPA V1 policy using OPA CLI, you can call it multiple times with different mock_input to test various scenarios, and use the `retry_count` to keep track of how many times the test has been retried for debugging purposes. If the test fails, analyze the error message and adjust the policy accordingly, then retry the test until it passes.
    - call `harness_skill` to save the final version of the generated policy in markdown format, which includes the policy code and explanations of the rules and logic used in the policy. This will serve as documentation for the generated policy and can be used for future reference or sharing with others."""
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@mcp.tool
async def get_skill_context():
    """
    - Use this skill content to write good policy.
    """
    async with aiofile.AIOFile(os.path.join(BASE_DIR, "policy_skill.md"), "r") as f:
        return await f.read()
@mcp.tool
async def verify_input_schema(input_schema:dict):
   """
   - is this input schema mentioned by user or self generated??
   - if self generated, ask user to provide input schema, don't generate on the fly based on assumption, as it may lead to wrong policy generation and testing, which is counterproductive. The input schema should be user specified, as it is the basis for policy generation and testing.
   """
   ...

@mcp.tool
async def test_rego(policy:str, package_name:str,mock_input:list[dict],test_value:str=None,retry_count:int=0):
    """
    - **mock_inputs** must be user specified schema, If user doesn't specify input schema, ask user to do so. Don't generate on the fly based on assumption. It is set base model, as it can be dynamic based on user request
    -Test the generated OPA V1 policy using OPA CLI
    - dynamic `test_value` for agents to **debug**, format it as <data.<package_name>.<variable>>, default to data.package_name.decision.result"""
    
    
    os.makedirs("generated_policies", exist_ok=True)
    file_name = f"generated_policies/{package_name}.rego"
    if not test_value:
        test_value=f"data.{package_name}.decision.result"
    async with aiofile.AIOFile(file_name, "w") as f:
        await f.write(policy) 

    results=[]
    for i, item in enumerate(mock_input):
        input_file = file_name.replace('.rego',f'_input_{i}.json')
        async with aiofile.AIOFile(input_file, "w") as f:
            await f.write(json.dumps(item))
        try:
            print(f"Testing policy with input case {i} for value {test_value}: Retry_count: {retry_count}")
            OPA_CLI_PATH = os.path.join(BASE_DIR, "opa")  # Adjust this path if OPA CLI is located elsewhere
            result = subprocess.run(
                [OPA_CLI_PATH, "eval", "-i", input_file, "-d", file_name, test_value],
                capture_output=True,
                text=True,
                check=True,
            )
            results.append(result.stdout)
        except subprocess.CalledProcessError as e:
            """
            If the OPA CLI command fails, return the error message for debugging.
            Rules:
            - if unsafe var, may be due to reasignment of default variable with := instead of =, or using decision variable name in rule body, or missing else block for default decision assignment"""
            return e.stderr or e.stdout,retry_count
    return results,retry_count

@mcp.tool
async def harness_skill(current_skill:str, updated_skill:str):
    """
    - harness skill for future improvements and reference.
    - only run this if `test_rego` tool returns successful tests after multiple retries and debugging.if succeeded in one try, no need to harness, if failed and error out, No point on harnessing, as it still doesn't know what solves the problem.
    - get current skill calling `get_skill_context`, and update it
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    async with aiofile.AIOFile(os.path.join(BASE_DIR, "policy_skill.md"), "w") as f:
        await f.write(updated_skill)

if __name__ == "__main__":
    print("Starting FastMCP")
    #* http mode
    # mcp.run(transport="http", host="127.0.0.1", port=8000)
    #* stdio mode for mcp through docker
    mcp.run()