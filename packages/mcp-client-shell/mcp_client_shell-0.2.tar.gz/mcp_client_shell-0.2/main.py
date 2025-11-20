import asyncio
from fastmcp import Client

async def main():
    port = input("Enter the port to access MCP server locally: ")
    show_tools = False
    try:
        async with Client(f"http://localhost:{port}/mcp") as client:
            await client.ping()
            tools_list = await client.list_tools()
            tools = {tool.name: tool for tool in tools_list}

            print("Available tools:")
            for i, name in enumerate(tools, 1):
                print(f" {i}. {name}")
            print("\nPress 'q' to exit\n")

            while True:
                if show_tools:
                    print("Available tools:")
                    for i, name in enumerate(tools, 1):
                        print(f" {i}. {name}")
                    print("\nPress 'q' to exit\n")

                user_input = input("Choose a tool by name or number, or 'q' to exit: ").strip()
                if user_input.lower() == "q":
                    break

                if user_input.isdigit():
                    idx = int(user_input) - 1
                    if 0 <= idx < len(tools):
                        tool = list(tools.values())[idx]
                    else:
                        print("Invalid tool number")
                        continue
                elif user_input in tools:
                    tool = tools[user_input]
                else:
                    print("Invalid tool selection")
                    continue

                args = {}
                for param in tool.inputSchema.get("required", []):
                    value = input(f"Enter value for '{param}': ").strip()
                    args[param] = value

                try:
                    result = await client.call_tool(tool.name, args)
                    print(f"{'-'*40}")
                    for item in result.content:
                        print("Result:\n", getattr(item, "text", item))
                        show_tools = True
                    print(f"{'-'*40}")
                except Exception as e:
                    print("Error calling tool:", e)

    except Exception as e:
        print("Failed to connect to MCP server:", e)

asyncio.run(main())
