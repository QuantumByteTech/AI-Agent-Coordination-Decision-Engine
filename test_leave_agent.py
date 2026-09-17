from agents.leave_agent import ask_leave_agent

question = input("Enter your leave question: ")

answer = ask_leave_agent(question)

print("\nLeave Agent:")
print(answer)