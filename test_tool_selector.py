from tools.tool_selector import select_tool

queries = [
    "What are the work from home rules?",
    "How many casual leaves do employees receive?",
    "What is the information for employee 1?",
    "What is the department of employee 1?",
    "Tell me something unrelated"
]

for query in queries:

    result = select_tool(query)

    print("\nQuestion:", query)
    print("Selection:", result)