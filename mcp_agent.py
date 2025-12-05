import asyncio
from agno.agent import Agent,RunOutput
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.models.google import Gemini
from agno.tools.mcp import MCPTools
from textwrap import dedent
from agno.utils.pprint import pprint_run_response
from mcp import StdioServerParameters

# key = AIzaSyBMXMSYdZtHCyCf1qtJdegzkBtp-vOcVR0


llmNote = dedent("""
### Context: Spring Expression Language (SpEL) and Model Hierarchy

Spring Expression Language (SpEL) is a powerful expression language used to query and manipulate object graphs at runtime. In this specific system, you are working with a hierarchical model structure defined by **three** JSON configurations:

1.  **Model**: Defines parent business domains (Models) with modelItems such as `id`, `name`, and `title`. This can be retrieved from MCP Server
2.  **modelItems**: Contains child entities (ModelItems) that reference their parent via `modelId` **and include type information (Text, Number, Enumeration)**. This can be retrieved from MCP Server
3.  ** modelItemEnumerations**: Contains predefined enumeration values for ModelItems of type "Enumeration", with `modelItemId`, `enumText`, and `enumValue` fields. This can be retrieved from MCP Server

**Syntax Rule:**
When writing SpEL expressions, you must use the dot-notation pattern:
`${ModelName.ModelItemName}` 

* **ModelName**: The name of the parent domain (e.g., "ImportRequest").
* **ModelItemName**: The specific entity within that domain (e.g., "ImportLicense").

* For Enumeration Types:**
When referencing enumeration values, you **must use only the numeric enumValue**:
* `${ForeignExchange.CurrencyPair} == 1` ✅ (using enumValue for USD/IRR)
* ~~`${ForeignExchange.CurrencyPair} == 'USD/IRR'`~~ ❌ (enumText not allowed)
---

### Allowed SpEL Operations

The following operations are permitted for defining business rules and logic:

#### 1. Relational Operators
Used to compare values.
* **Equal:** `==` or `eq` 
* **Not Equal:** `!=` or `ne` 
* **Less Than:** `<` or `lt` 
* **Less Than or Equal:** `<=` or `le` 
* **Greater Than:** `>` or `gt` 
* **Greater Than or Equal:** `>=` or `ge` 
* *Example:* `${ImportRequest.Amount} > 10000` 
* ** Enumeration Example:** `${ForeignExchange.CurrencyPair} == 2` (for EUR/IRR)

#### 2. Logical Operators
Used to combine multiple conditions.
* **AND:** `and` 
* **OR:** `or` 
* **NOT:** `!` or `not` 
* *Example:* `${ForeignExchange.Currency} == 'USD' and ${ImportRequest.Risk} == 'High'` 
* ** Enumeration Example:** `${ForeignExchange.CurrencyPair} == 1 and ${ImportRequest.Amount} > 50000`

#### 3. Mathematical Operators
Used for calculations.
* **Arithmetic:** `+`, `-`, `*`, `/`, `%` (modulus), `^` (power)
* *Example:* `${ImportRequest.TotalValue} * 0.20` 

** 4. Type-Specific Operations**
Different operations based on ModelItem types:
* **Text Type:** String operations, pattern matching
* **Number Type:** Mathematical calculations, numeric comparisons  
* **Enumeration Type:** Equality checks against numeric enumValues only (enumText not permitted)
""")

async def main():
    # Initialize MCP tools
    ## mcp_tools = MCPTools(transport="streamable-http", url="http://localhost:8080/mcp")
    try:



        
        # Create Agent with MCP server connection
        agent = Agent(
             #  model=Gemini(id="gemini-2.5-flash"),
             model = Ollama(id = "llama3.2"),
            tools=[MCPTools(transport="streamable-http", url="http://localhost:8080/mcp")],
            instructions=dedent(f"""\
            You are an AI assistant that ONLY uses the actual MCP server tools provided to you.
            
            CRITICAL RULES:
            1. You MUST ONLY call tools that are actually available through the MCP server connection
            2. You are FORBIDDEN from inventing, assuming, or hallucinating tool names
            4. You MUST first list available tools before attempting to use any
            5. If the MCP server has no relevant tools, respond exactly: "I can't help you"
            6. Do NOT use general knowledge or make assumptions about what tools exist
            
            WORKFLOW:
            1. First, identify what tools are actually available from the MCP server
            2. Only use tools that are confirmed to exist and are relevant
            3. If no suitable tools exist, respond: "I can't help you"
            4. Never invent tool calls or function names
            
            OUTPUT FORMAT:
            1. Return Json in format: {{ expr: GeneratedSPEL, models: [List of used models] }} 
            
            ADDITIONALINFO: 
            ${llmNote}
            
            Remember: Only use real MCP server tools, never invented ones.
            """),
            markdown=True
        )

        # First, let's see what tools are available
        await agent.acli_app(
            input="",
            stream=True,
            markdown=True,
            exit_on=["exit", "quit"],
        )
        # await agent.aprint_response(input="Get all modelitems for ImportRequest"
        #                             , stream=True)


    finally:
        pass



# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
