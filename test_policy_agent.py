from agents.policy_agent import ask_policy_agent

question = input("Enter your HR policy question: ")

answer = ask_policy_agent(question)

print("\nPolicy Agent:")
print(answer)