import asyncio
import sys
from universal_mcp.react_agent.graph import graph  

async def main(target_script_path=None):
    if target_script_path is None:
        if len(sys.argv) > 1:
            target_script_path = sys.argv[1]
        else:
            print("Error: No target script path provided")
            print("Usage: python -m universal_mcp.react_agent.run_graph <target_script_path>")
            sys.exit(1)
    
    result = await graph.ainvoke({"target_script_path": target_script_path}, {"recursion_limit": 100})
    print("Graph execution completed!")
    
    if "functions_processed" in result:
        print(f"Processed {result['functions_processed']} functions")
    
if __name__ == "__main__":
    asyncio.run(main())