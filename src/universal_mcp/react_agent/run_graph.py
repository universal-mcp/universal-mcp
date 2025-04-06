import asyncio
from universal_mcp.react_agent.graph import graph  

async def main():
    result = await graph.ainvoke({}, {"recursion_limit": 100})
    print("Graph execution completed!")
    
    if "functions_processed" in result:
        print(f"Processed {result['functions_processed']} functions")
    
if __name__ == "__main__":
    asyncio.run(main())