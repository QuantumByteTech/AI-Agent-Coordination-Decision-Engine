from agent_action_pipeline import execute_agent_action


queries = [
    "What are the work from home rules?",
    "How many casual leaves do employees receive?",
    "What is the information for employee 1?",
    "What is the information for employee abc?",
    "Tell me something unrelated"
]


for query in queries:

    print("\n" + "=" * 60)
    print("Question:", query)

    result = execute_agent_action(query)

    print("Pipeline Result:")
    print(result)